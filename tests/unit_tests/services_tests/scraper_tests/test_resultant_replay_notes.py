import json
from copy import deepcopy

def test_F1():
    from recipe_scrapers import scrape_html
    from mealie.lang.providers import get_locale_provider
    from mealie.services.scraper.scraper_strategies import RecipeScraperPackage

    data = json.dumps({"@context": "https://schema.org", "@type": "Recipe", "name": "Soup",
                       "recipeIngredient": ["salt"], "recipeInstructions": ["Stir"],
                       "notes": [" <b>Serve warm</b> ", {"title": " <i>Store</i> ", "text": " Keep cold "}, " ", 9,
                                 {"title": "bad"}, {"text": "<b></b>"}]})
    url = "https://example.com/recipe"
    strategy = RecipeScraperPackage(url, get_locale_provider(), None)
    scraped = scrape_html(RecipeScraperPackage.ld_json_to_html(data), org_url=url, supported_only=False)
    recipe, _ = strategy.clean_scraper(scraped, url)
    assert [(n.title, n.text) for n in recipe.notes] == [("", "Serve warm"), ("Store", "Keep cold")]

def test_B1():
    from mealie.services.scraper.cleaner import clean_notes

    before = [{"text": "chill"}, "serve", {"title": "store", "text": "refrigerate"}, 14]
    expected = [{"text": "chill"}, "serve", {"title": "store", "text": "refrigerate"}, 14]
    assert clean_notes(before) == [{"title": "", "text": "chill"}, {"title": "", "text": "serve"},
                                   {"title": "store", "text": "refrigerate"}]
    assert before == expected
