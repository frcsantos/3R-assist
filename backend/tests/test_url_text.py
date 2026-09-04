from app.services.url_text import html_to_text, parse_as_fetch_url


def test_parse_as_fetch_url_accepts_http_https_and_www():
    assert parse_as_fetch_url("https://example.com/doc") == "https://example.com/doc"
    assert parse_as_fetch_url("http://example.com/doc") == "http://example.com/doc"
    assert parse_as_fetch_url("www.example.com/doc") == "https://www.example.com/doc"
    assert parse_as_fetch_url("  https://example.com/a  ") == "https://example.com/a"


def test_parse_as_fetch_url_rejects_plain_text_and_multiline():
    assert parse_as_fetch_url("not a url") is None
    assert parse_as_fetch_url("https://example.com/doc\nmore text") is None
    assert parse_as_fetch_url("see https://example.com") is None
    assert parse_as_fetch_url("ftp://example.com/doc") is None


def test_html_to_text_strips_scripts_and_keeps_title_body():
    html = """
    <html>
      <head><title>OECD TG 439</title>
        <script>window.x = 1</script>
        <style>.x { color: red }</style>
      </head>
      <body>
        <h1>Skin irritation</h1>
        <p>This guideline describes an in vitro method.</p>
        <script>alert('x')</script>
      </body>
    </html>
    """
    text = html_to_text(html)
    assert "OECD TG 439" in text
    assert "Skin irritation" in text
    assert "in vitro method" in text
    assert "window.x" not in text
    assert "alert(" not in text
    assert "color: red" not in text
