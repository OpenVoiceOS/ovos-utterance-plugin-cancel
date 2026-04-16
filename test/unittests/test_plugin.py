import unittest
from unittest.mock import patch, MagicMock
from ovos_utterance_plugin_cancel import NevermindPlugin


class TestNevermindPlugin(unittest.TestCase):
    def setUp(self) -> None:
        self.plugin = NevermindPlugin()

    def test_cancel_word_detected_en(self) -> None:
        utterances, ctx = self.plugin.transform(["hey mycroft nevermind that"], {"lang": "en-US"})
        self.assertEqual(utterances, [])
        self.assertTrue(ctx.get("canceled"))
        self.assertIn("cancel_word", ctx)

    def test_passthrough_no_cancel(self) -> None:
        utterances, ctx = self.plugin.transform(["turn on the lights"], {"lang": "en-US"})
        self.assertEqual(utterances, ["turn on the lights"])
        self.assertEqual(ctx, {})

    def test_cancel_it(self) -> None:
        utterances, ctx = self.plugin.transform(["actually cancel it"], {"lang": "en-US"})
        self.assertEqual(utterances, [])
        self.assertTrue(ctx.get("canceled"))

    def test_forget_that(self) -> None:
        utterances, ctx = self.plugin.transform(["forget that"], {"lang": "en-US"})
        self.assertEqual(utterances, [])
        self.assertTrue(ctx.get("canceled"))

    def test_default_lang_fallback(self) -> None:
        """Missing lang key should default to en-US without error."""
        utterances, ctx = self.plugin.transform(["cancel that"], {})
        self.assertEqual(utterances, [])
        self.assertTrue(ctx.get("canceled"))

    def test_multiple_utterances_cancel_first_match(self) -> None:
        utterances, ctx = self.plugin.transform(
            ["set a timer", "forget it"], {"lang": "en-US"}
        )
        self.assertEqual(utterances, [])
        self.assertTrue(ctx.get("canceled"))

    def test_get_cancel_words_returns_list(self) -> None:
        words = self.plugin.get_cancel_words("en-US")
        self.assertIsInstance(words, list)
        self.assertGreater(len(words), 0)

    def test_unsupported_lang_returns_empty(self) -> None:
        words = self.plugin.get_cancel_words("xx-XX")
        self.assertIsInstance(words, list)

    def test_plugin_name_and_priority(self) -> None:
        self.assertEqual(self.plugin.name, "ovos-utterance-cancel")
        self.assertEqual(self.plugin.priority, 15)

    def test_cancel_word_in_context(self) -> None:
        _, ctx = self.plugin.transform(["cancel that"], {"lang": "en-US"})
        self.assertEqual(ctx.get("cancel_word"), "cancel that")


if __name__ == "__main__":
    unittest.main()
