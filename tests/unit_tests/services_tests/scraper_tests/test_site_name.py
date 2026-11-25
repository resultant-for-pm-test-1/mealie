import importlib
import importlib.util
from types import ModuleType

MODULE_NAME = "mealie.services.scraper.site_name"


def _site_name_module() -> ModuleType:
    """Load the site-name helpers, failing by assertion when the module does not exist yet."""
    assert importlib.util.find_spec(MODULE_NAME) is not None, f"{MODULE_NAME} does not exist"
    return importlib.import_module(MODULE_NAME)


def test_derive_site_name_from_import_address():
    site_name = _site_name_module()

    cases = {
        "https://www.allrecipes.com/recipe/123": "allrecipes.com",
        "https://example.org/r/1": "example.org",
        "https://Example.COM/Recipe": "example.com",
        "HTTPS://Example.COM/Recipe": "example.com",
    }

    for address, expected in cases.items():
        assert site_name.derive_site_name(address) == expected, address


def test_helpers_remove_credentials_from_address():
    site_name = _site_name_module()
    address = "https://user:pass@www.allrecipes.com/recipe/123"

    derived = site_name.derive_site_name(address)
    stripped = site_name.strip_url_credentials(address)

    assert derived == "allrecipes.com"
    assert stripped == "https://www.allrecipes.com/recipe/123"
    assert "pass" not in derived
    assert "pass" not in stripped
