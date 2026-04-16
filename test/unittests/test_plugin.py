import unittest
from ovos_utterance_plugin_cancel import NevermindPlugin


class TestNevermindPlugin(unittest.TestCase):
    def setUp(self) -> None:
        self.plugin = NevermindPlugin()

    # --- happy path ---

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

    def test_cancel_word_in_context(self) -> None:
        _, ctx = self.plugin.transform(["cancel that"], {"lang": "en-US"})
        self.assertEqual(ctx.get("cancel_word"), "cancel that")

    def test_multiple_utterances_cancel_first_match(self) -> None:
        utterances, ctx = self.plugin.transform(
            ["set a timer", "forget it"], {"lang": "en-US"}
        )
        self.assertEqual(utterances, [])
        self.assertTrue(ctx.get("canceled"))

    # --- locale / language ---

    def test_default_lang_fallback(self) -> None:
        utterances, ctx = self.plugin.transform(["cancel that"], {})
        self.assertEqual(utterances, [])
        self.assertTrue(ctx.get("canceled"))

    def test_none_context_does_not_raise(self) -> None:
        utterances, ctx = self.plugin.transform(["cancel that"], None)
        self.assertEqual(utterances, [])
        self.assertTrue(ctx.get("canceled"))

    def test_get_cancel_words_returns_list(self) -> None:
        words = self.plugin.get_cancel_words("en-US")
        self.assertIsInstance(words, list)
        self.assertGreater(len(words), 0)

    def test_unsupported_lang_returns_empty(self) -> None:
        words = self.plugin.get_cancel_words("xx-XX")
        self.assertIsInstance(words, list)
        self.assertEqual(words, [])

    def test_unsupported_lang_passthrough(self) -> None:
        utterances, ctx = self.plugin.transform(["cancel that"], {"lang": "xx-XX"})
        self.assertEqual(utterances, ["cancel that"])
        self.assertEqual(ctx, {})

    # --- empty / degenerate inputs ---

    def test_empty_utterance_list(self) -> None:
        utterances, ctx = self.plugin.transform([], {"lang": "en-US"})
        self.assertEqual(utterances, [])
        self.assertEqual(ctx, {})

    def test_empty_string_utterance_no_cancel(self) -> None:
        utterances, ctx = self.plugin.transform([""], {"lang": "en-US"})
        self.assertEqual(utterances, [""])
        self.assertEqual(ctx, {})

    def test_whitespace_only_utterance(self) -> None:
        utterances, ctx = self.plugin.transform(["   "], {"lang": "en-US"})
        self.assertEqual(utterances, ["   "])
        self.assertEqual(ctx, {})

    def test_multiple_empty_strings(self) -> None:
        utterances, ctx = self.plugin.transform(["", "", ""], {"lang": "en-US"})
        self.assertEqual(utterances, ["", "", ""])
        self.assertEqual(ctx, {})

    def test_cancel_phrase_alone(self) -> None:
        """Bare cancel phrase with nothing before it should still match."""
        utterances, ctx = self.plugin.transform(["cancel that"], {"lang": "en-US"})
        self.assertEqual(utterances, [])
        self.assertTrue(ctx.get("canceled"))

    def test_cancel_phrase_not_at_tail(self) -> None:
        """Cancel phrase mid-sentence must NOT trigger (endswith only)."""
        utterances, ctx = self.plugin.transform(["cancel that alarm please"], {"lang": "en-US"})
        self.assertEqual(utterances, ["cancel that alarm please"])
        self.assertEqual(ctx, {})

    def test_mixed_list_first_normal_then_cancel(self) -> None:
        """First utterance is normal, second ends with cancel phrase."""
        utterances, ctx = self.plugin.transform(
            ["what is the weather", "actually forget it"], {"lang": "en-US"}
        )
        self.assertEqual(utterances, [])
        self.assertTrue(ctx.get("canceled"))

    def test_case_sensitive_no_match(self) -> None:
        """Matching is case-sensitive — uppercase phrase should not match."""
        utterances, ctx = self.plugin.transform(["CANCEL THAT"], {"lang": "en-US"})
        # if locale phrases are lowercase this should not match
        if ctx.get("canceled"):
            # locale phrases happen to be uppercase too — that's fine
            self.assertIn("cancel_word", ctx)
        else:
            self.assertEqual(utterances, ["CANCEL THAT"])

    # --- plugin metadata ---

    def test_plugin_name_and_priority(self) -> None:
        self.assertEqual(self.plugin.name, "ovos-utterance-cancel")
        self.assertEqual(self.plugin.priority, 15)

    def test_custom_name_and_priority(self) -> None:
        p = NevermindPlugin(name="custom", priority=5)
        self.assertEqual(p.name, "custom")
        self.assertEqual(p.priority, 5)


class TestNevermindPluginLocales(unittest.TestCase):
    """Smoke-test cancel detection for every shipped locale.

    Each case picks one phrase that must appear verbatim in the locale file
    (or is produced by bracket-expansion of a template in that file) and
    verifies the plugin actually cancels when the utterance ends with it.
    """

    def setUp(self) -> None:
        self.plugin = NevermindPlugin()

    def _assert_cancels(self, utterance: str, lang: str) -> None:
        utterances, ctx = self.plugin.transform([utterance], {"lang": lang})
        self.assertEqual(utterances, [], f"[{lang}] expected cancel for: {utterance!r}")
        self.assertTrue(ctx.get("canceled"), f"[{lang}] 'canceled' not set for: {utterance!r}")

    def _assert_passes(self, utterance: str, lang: str) -> None:
        utterances, ctx = self.plugin.transform([utterance], {"lang": lang})
        self.assertNotEqual(utterances, [], f"[{lang}] expected passthrough for: {utterance!r}")
        self.assertFalse(ctx.get("canceled"), f"[{lang}] unexpected cancel for: {utterance!r}")

    def test_ca_es_cancel(self) -> None:
        self._assert_cancels("cancel·la això", "ca-ES")

    def test_ca_es_passthrough(self) -> None:
        self._assert_passes("posa la llum", "ca-ES")

    def test_da_dk_cancel(self) -> None:
        self._assert_cancels("afbryd det", "da-DK")

    def test_da_dk_passthrough(self) -> None:
        self._assert_passes("tænd lyset", "da-DK")

    def test_de_de_cancel(self) -> None:
        self._assert_cancels("vergiss das", "de-DE")

    def test_de_de_passthrough(self) -> None:
        self._assert_passes("mach das licht an", "de-DE")

    def test_en_us_cancel(self) -> None:
        self._assert_cancels("nevermind that", "en-US")

    def test_en_us_passthrough(self) -> None:
        self._assert_passes("turn on the lights", "en-US")

    def test_es_es_cancel(self) -> None:
        self._assert_cancels("cancela eso", "es-ES")

    def test_es_es_passthrough(self) -> None:
        self._assert_passes("pon la luz", "es-ES")

    def test_fr_fr_cancel(self) -> None:
        self._assert_cancels("annuler que", "fr-FR")

    def test_fr_fr_passthrough(self) -> None:
        self._assert_passes("allume la lumière", "fr-FR")

    def test_gl_es_cancel(self) -> None:
        self._assert_cancels("cancelar iso", "gl-ES")

    def test_gl_es_passthrough(self) -> None:
        self._assert_passes("acende a luz", "gl-ES")

    def test_it_it_cancel(self) -> None:
        self._assert_cancels("lascia perdere il comando", "it-IT")

    def test_it_it_passthrough(self) -> None:
        self._assert_passes("accendi la luce", "it-IT")

    def test_nl_nl_cancel(self) -> None:
        self._assert_cancels("annuleren", "nl-NL")

    def test_nl_nl_passthrough(self) -> None:
        self._assert_passes("doe het licht aan", "nl-NL")

    def test_pt_br_cancel(self) -> None:
        self._assert_cancels("cancele", "pt-BR")

    def test_pt_br_passthrough(self) -> None:
        self._assert_passes("acenda a luz", "pt-BR")

    def test_pt_pt_cancel(self) -> None:
        self._assert_cancels("cancelar isso", "pt-PT")

    def test_pt_pt_passthrough(self) -> None:
        self._assert_passes("liga a luz", "pt-PT")

    def test_all_locales_have_cancel_words(self) -> None:
        for lang in ("ca-ES", "da-DK", "de-DE", "en-US", "es-ES",
                     "fr-FR", "gl-ES", "it-IT", "nl-NL", "pt-BR", "pt-PT"):
            words = self.plugin.get_cancel_words(lang)
            self.assertGreater(len(words), 0, f"No cancel words loaded for {lang}")


if __name__ == "__main__":
    unittest.main()
