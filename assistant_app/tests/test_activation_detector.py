from voice.activation_detector import ActivationDetector


def test_detects_direct_activation():
    detector = ActivationDetector("Kaspian")
    result = detector.detect("Kaspian, pon música")
    assert result.activated is True
    assert result.cleaned_text == "pon música"
    assert result.confidence >= 0.8


def test_ignores_background_conversation():
    detector = ActivationDetector("Kaspian")
    result = detector.detect("Creo que mañana va a llover")
    assert result.activated is False
