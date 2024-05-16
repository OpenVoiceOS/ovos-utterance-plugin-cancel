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
from os.path import join, dirname, isfile
from typing import List, Optional

from functools import lru_cache
from ovos_plugin_manager.templates.transformers import UtteranceTransformer
from ovos_utils.log import LOG
from ovos_utils.bracket_expansion import expand_options


class NevermindPlugin(UtteranceTransformer):

    def __init__(self, name="ovos-utterance-cancel", priority=15):
        super().__init__(name, priority)

    @lru_cache()
    def get_cancel_words(self, lang="en-us"):
        res_path = join(dirname(__file__), "locale", lang, "cancel.intent")
        if isfile(res_path):
            lines = list()
            with open(res_path) as f:
                for line in f.readlines():
                    if line.startswith("#"):
                        continue
                    lines.extend(expand_options(line))
            return lines
        else:
            LOG.warning(f"cancel.dialog not available for {lang}")
        return []
        
    def transform(self, utterances: List[str], context: Optional[dict] = None) -> (list, dict):
        lang = context.get("lang", "en-us")
        for nevermind in self.get_cancel_words(lang):
            for utterance in utterances:
                if utterance.endswith(nevermind):
                    return [], {"canceled": True, "cancel_word": nevermind}

        return utterances, {}
