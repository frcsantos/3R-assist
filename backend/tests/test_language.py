from app.services.language import detect_lang


def test_detect_lang_english_protocol():
    text = (
        "Acute toxicity study with Wistar rats using oral gavage. "
        "The animals were observed after dosing and the LD50 was determined."
    )
    assert detect_lang(text) == "en"


def test_detect_lang_portuguese_document():
    text = (
        "Resolução Normativa CONCEA nº 18/2014 reconhece métodos "
        "alternativos para a substituição do uso de animais em ensaios."
    )
    assert detect_lang(text) == "pt"


def test_detect_lang_empty_defaults_english():
    assert detect_lang("") == "en"
    assert detect_lang(None) == "en"
