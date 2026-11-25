from urllib.parse import urlsplit, urlunsplit


def _split(url: str):
    """Split an import address, treating one without a scheme (such as `www.example.com/x`) as a host and path."""
    url = url.strip()
    return urlsplit(url if "://" in url else f"//{url}")


def derive_site_name(url: str | None) -> str | None:
    """The domain of an import address: lowercased, without a leading `www.`, port or credentials.

    The page title is deliberately not consulted, so the name depends on the address alone.
    """
    if not url:
        return None

    try:
        host = _split(url).hostname
    except ValueError:
        return None

    if not host:
        return None

    return host.lower().removeprefix("www.") or None


def strip_url_credentials(url: str | None) -> str | None:
    """The address without a `user:password@` section. An address that carries none is returned unchanged."""
    if not url:
        return url

    try:
        parts = _split(url)
        has_credentials = parts.username is not None or parts.password is not None
    except ValueError:
        return url

    if not has_credentials or "://" not in url:
        return url

    return urlunsplit(parts._replace(netloc=parts.netloc.rpartition("@")[2]))
