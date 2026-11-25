from pathlib import Path

import pytest
from fastapi import HTTPException

import mealie.services.scraper.recipe_scraper as recipe_scraper_module
from mealie.lang.providers import get_locale_provider
from mealie.schema.recipe.recipe import RecipeDraft
from mealie.services.recipe.recipe_data_service import RecipeDataService
from mealie.services.scraper import scraper
from mealie.services.scraper.recipe_scraper import RecipeScraper
from mealie.services.scraper.scraped_extras import ScrapedExtras


@pytest.mark.asyncio
async def test_create_from_html_truncates_long_slug(monkeypatch):
    """A recipe scraped with an excessively long name must yield a slug short enough
    to be used as a filesystem directory name.

    Regression test for GH #7662: scraping (e.g. an Instagram caption) dumped the entire
    text into the recipe name. The scraper used a raw ``slugify`` instead of the shared
    ``create_recipe_slug`` helper, so the persisted slug could exceed the OS 255-byte
    filename limit. Editing/saving the recipe then raised an uncaught
    ``OSError: [Errno 36] File name too long`` in ``RecipeService.check_assets``.
    """
    # ~1300 characters, mirroring the caption-as-title data from the bug report
    long_name = "High Protein Low Calorie Recipes Smash Or Pass " * 28

    async def fake_scrape(self, url, html=None, on_progress=None, **kwargs):
        return RecipeDraft(name=long_name), ScrapedExtras()

    monkeypatch.setattr(RecipeScraper, "scrape", fake_scrape)

    translator = get_locale_provider()
    recipe, _ = await scraper.create_from_html(
        "https://example.com/recipe",
        repos=None,  # type: ignore[arg-type]
        translator=translator,
        html="<html></html>",
    )

    # The full title is preserved (name column is unbounded)...
    assert recipe.name == long_name
    # ...but the slug is truncated to a filesystem-safe length.
    assert 0 < len(recipe.slug) <= 250


@pytest.mark.parametrize(
    ("scraped_image", "download_result", "expect_key"),
    [
        pytest.param("https://example.com/img.jpg", Path("/images/original.webp"), True, id="image-downloaded"),
        pytest.param("https://example.com/img.jpg", None, False, id="download-failed"),
        pytest.param("no image", None, False, id="placeholder-url"),
        pytest.param(None, None, False, id="no-image-url"),
    ],
)
@pytest.mark.asyncio
async def test_finalize_only_stamps_a_cache_key_when_an_image_landed(
    monkeypatch, scraped_image, download_result, expect_key
):
    """`recipe.image` must stay empty unless a file actually reached the disk.

    The frontend reads the presence of this cache key as "this recipe has a picture" and
    skips the request entirely when it is empty. Stamping a key regardless of whether the
    download succeeded is what left recipes asking the media route for a file that 404s on
    every single render (mealie-recipes/mealie#8271, GH #4804).
    """

    async def fake_scrape_image(self, image_url):
        return download_result

    monkeypatch.setattr(RecipeDataService, "scrape_image", fake_scrape_image)

    recipe = await scraper.finalize_scraped_recipe(
        RecipeDraft(name="Test Recipe", image=scraped_image),
        get_locale_provider(),
    )

    assert bool(recipe.image) is expect_key


PAGE_TITLE = "Best Cookies Ever | Some Brand"
RECIPE_PAGE_HTML = f"""<html><head><title>{PAGE_TITLE}</title>
<meta property="og:title" content="{PAGE_TITLE}" />
<script type="application/ld+json">
{{"@context": "https://schema.org", "@type": "Recipe", "name": "Cookies",
 "recipeIngredient": ["1 cup flour", "1 egg"],
 "recipeInstructions": [{{"@type": "HowToStep", "text": "Mix."}}, {{"@type": "HowToStep", "text": "Bake."}}]}}
</script></head><body></body></html>"""


@pytest.mark.asyncio
async def test_scraped_recipe_site_name_comes_from_address_not_title():
    draft, _ = await scraper.create_from_html(
        "https://www.allrecipes.com/recipe/123",
        repos=None,  # type: ignore[arg-type]
        translator=get_locale_provider(),
        html=RECIPE_PAGE_HTML,
    )

    site_name = getattr(draft, "site_name", None)
    assert site_name == "allrecipes.com"
    assert site_name != PAGE_TITLE


@pytest.mark.asyncio
async def test_scraped_recipe_stores_no_password_in_original_address():
    draft, _ = await scraper.create_from_html(
        "https://user:pass@www.allrecipes.com/recipe/123",
        repos=None,  # type: ignore[arg-type]
        translator=get_locale_provider(),
        html=RECIPE_PAGE_HTML,
    )

    assert getattr(draft, "site_name", None) == "allrecipes.com"
    assert draft.org_url is not None
    assert "pass" not in draft.org_url
    assert "pass" not in (getattr(draft, "site_name", None) or "")


@pytest.mark.asyncio
async def test_failed_import_creates_no_recipe(monkeypatch):
    async def failed_fetch(url: str):
        return None

    monkeypatch.setattr(recipe_scraper_module, "resilient_fetch", failed_fetch)

    with pytest.raises(HTTPException) as exc_info:
        await scraper.create_from_html(
            "https://unreachable.invalid/recipe",
            repos=None,  # type: ignore[arg-type]
            translator=get_locale_provider(),
        )

    assert exc_info.value.status_code == 400
