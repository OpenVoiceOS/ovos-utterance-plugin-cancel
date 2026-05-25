# # NEON AI (TM) SOFTWARE, Software Development Kit & Application Development System
# # All trademark and other rights reserved by their respective owners
# # Copyright 2008-2021 Neongecko.com Inc.
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from this
#    software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
# CONTRIBUTORS  BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA,
# OR PROFITS;  OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE,  EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
import os
from os.path import join, dirname, isfile
from functools import lru_cache
from typing import Dict, List, Optional, Tuple

from ovos_plugin_manager.templates.transformers import UtteranceTransformer
from ovos_spec_tools import closest_lang, expand, standardize_lang
from ovos_utils.log import LOG


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
        langs = [d for d in os.listdir(locale_dir)
                 if isfile(join(locale_dir, d, "cancel.intent"))]
        # closest_lang gates on the < 10 distance threshold internally and
        # returns None when no candidate is close enough.
        best_lang = closest_lang(lang, langs, max_distance=10)
        if best_lang is None:
            LOG.warning(f"cancel.intent not available for {lang}")
            return []
        res_path = join(locale_dir, best_lang, "cancel.intent")
        lines: List[str] = []
        with open(res_path) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                lines.extend(expand(line))
        return list({phrase.strip() for phrase in lines if phrase.strip()})

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
        lang = standardize_lang(context.get("lang", "en-US"))
        for nevermind in self.get_cancel_words(lang):
            for utterance in utterances:
                if utterance.endswith(nevermind):
                    return [], {"canceled": True, "cancel_word": nevermind}
        return utterances, {}
