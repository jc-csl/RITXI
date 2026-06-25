from app.services.emotions import parse_emotion


def test_parse_emotion_tag():
    parsed = parse_emotion("[SALUDO] Hola mundo")
    assert parsed.emotion == "saludo"
    assert parsed.clean_text == "Hola mundo"


def test_parse_without_emotions_disabled():
    parsed = parse_emotion("[BAILE] Hola", process_emotions=False)
    assert parsed.emotion == "neutral"
    assert parsed.clean_text == "[BAILE] Hola"
