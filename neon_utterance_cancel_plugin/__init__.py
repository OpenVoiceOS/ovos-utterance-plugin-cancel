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

from neon_transformers import UtteranceTransformer
from neon_transformers.tasks import UtteranceTask
from ovos_utils.log import LOG


class Nevermind(UtteranceTransformer):
    task = UtteranceTask.TRANSFORM

    def __init__(self, name="utterance_cancel", priority=15):
        super().__init__(name, priority)

    @staticmethod
    def get_cancel_words(lang="en-us"):
        res_path = join(dirname(__file__), "res", lang, "cancel.dialog")
        if isfile(res_path):
            with open(res_path) as f:
                return [l.strip() for l in f.read().split("\n")
                        if l and not l.startswith("#")]
        else:
            LOG.warning(f"cancel.dialog not available for {lang}")
        return []

    def transform(self, utterances, context):
        lang = context.get("lang", "en-us")
        for nevermind in self.get_cancel_words(lang):
            for utterance in utterances:
                if utterance.endswith(nevermind):
                    return [], {"canceled": True, "cancel_word": nevermind}

        return utterances, {}
