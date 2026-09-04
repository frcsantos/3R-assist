from app.services.file_text import FileTextError, extract_text_from_upload


def test_extract_txt():
    text = extract_text_from_upload(
        filename="note.txt",
        content_type="text/plain",
        raw=b"Title: OECD TG 439\nThis guideline describes an in vitro method for skin irritation.",
    )
    assert "OECD TG 439" in text
    assert "skin irritation" in text


def test_extract_html_strips_markup():
    html = b"""
    <html><head><title>Guidance</title>
    <script>evil()</script></head>
    <body><h1>Protocol document</h1><p>Validated alternative method details here.</p></body></html>
    """
    text = extract_text_from_upload(
        filename="doc.html",
        content_type="text/html",
        raw=html,
    )
    assert "Guidance" in text
    assert "Protocol document" in text
    assert "evil" not in text


def test_reject_unsupported_extension():
    try:
        extract_text_from_upload(
            filename="image.png",
            content_type="image/png",
            raw=b"not-a-real-image-but-long-enough-bytes-1234567890",
        )
        assert False, "expected FileTextError"
    except FileTextError as exc:
        assert exc.code == "FILE_TYPE_UNSUPPORTED"
