# Copyright 2024 OpenVoiceOS
# Licensed under the Apache License, Version 2.0
import os
from os.path import join, dirname, isfile
from functools import lru_cache
from typing import Dict, List, Optional, Tuple

from ovos_plugin_manager.templates.transformers import UtteranceTransformer
from ovos_utils.log import LOG
from ovos_utils.lang import standardize_lang_tag
from ovos_utils.bracket_expansion import expand_template
from langcodes import closest_match


class NevermindPlugin(UtteranceTransformer):
    """Utterance transformer that drops utterances ending with a cancel phrase.

    Cancel phrases are loaded from ``locale/<lang>/cancel.intent`` and
    matched against the tail of each utterance.  On a match the utterance
    list is cleared and ``{"canceled": True, "cancel_word": <phrase>}`` is
    added to the context dict so downstream components can react.
    """

    def __init__(self, name: str = "ovos-utterance-cancel", priority: int = 15) -> None:
        super().__init__(name, priority)

    @lru_cache()
    def get_cancel_words(self, lang: str = "en-US") -> List[str]:
        """Return the list of cancel phrases for *lang*.

        Phrases are read from ``locale/<best_match>/cancel.intent``, expanded
        via bracket-expansion, and deduplicated.  The result is LRU-cached per
        language tag for the lifetime of the process.

        Args:
            lang: BCP-47 language tag (e.g. ``"en-US"``).

        Returns:
            List of cancel phrases, or an empty list when no locale is close
            enough (langcodes distance ≥ 10).
        """
        locale_dir = join(dirname(__file__), "locale")
        langs = [l for l in os.listdir(locale_dir)
                 if isfile(join(locale_dir, l, "cancel.intent"))]
        best_lang, score = closest_match(lang, langs)
        # langcodes distance: 0 = same, 1-3 = minor regional, 4-10 = significant regional
        if score < 10:
            res_path = join(locale_dir, best_lang, "cancel.intent")
            lines: List[str] = []
            with open(res_path) as f:
                for line in f.readlines():
                    if line.startswith("#"):
                        continue
                    lines.extend(expand_template(line))
            return list({l for l in lines if l.strip()})
        LOG.warning(f"cancel.intent not available for {lang}")
        return []

    def transform(
        self,
        utterances: List[str],
        context: Optional[Dict[str, object]] = None,
    ) -> Tuple[List[str], Dict[str, object]]:
        """Drop utterances that end with a cancel phrase.

        Args:
            utterances: Recognised utterance candidates.
            context: Session context dict; ``lang`` key is used for locale
                selection (defaults to ``"en-US"`` when absent).

        Returns:
            A 2-tuple of ``(utterances, extra_context)``.  When a cancel phrase
            is matched, *utterances* is empty and *extra_context* contains
            ``{"canceled": True, "cancel_word": <phrase>}``.  Otherwise the
            original utterances are returned unchanged with an empty dict.
        """
        context = context or {}
        lang = standardize_lang_tag(context.get("lang", "en-US"))
        for nevermind in self.get_cancel_words(lang):
            for utterance in utterances:
                if utterance.endswith(nevermind):
                    return [], {"canceled": True, "cancel_word": nevermind}
        return utterances, {}
