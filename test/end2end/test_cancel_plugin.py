"""End-to-end ovoscope tests for ``ovos-utterance-plugin-cancel``.

Three scenarios:

* the cancel transformer fires on a suffix-matched utterance
  (positive path);
* the cancel transformer is **not** invoked when the plugin is
  disabled in config — the utterance falls through to intent failure
  (negative gate: proves the positive test is observing the plugin
  itself, not some unrelated component);
* a plain utterance with no cancel suffix passes through to the skill
  unchanged (smoke).
"""
import json
import os
import tempfile
from unittest import TestCase

from ovos_bus_client.message import Message
from ovos_bus_client.session import Session
from ovos_config.config import Configuration
from ovos_config.models import LocalConf
from ovos_utils.log import LOG
from ovoscope import End2EndTest, get_minicroft


# The entry-point name under which this plugin is registered. The
# OVOS UtteranceTransformersService loads a plugin only when this name
# appears (with ``active: True``) in ``Configuration().utterance_transformers``
# — ``ovos_core/transformers.py:29``.
PLUGIN_NAME = "ovos-utterance-cancel-plugin"


class _CancelPluginTestBase(TestCase):
    """Common boot / teardown.

    MiniCroft's ``isolate_config=True`` clears the user's XDG configs
    **and** calls ``Configuration.reload()``, which would wipe any
    in-memory override done in ``setUp``. Each subclass writes its
    desired config to a temp file and prepends it to
    ``Configuration.xdg_configs`` before booting MiniCroft with
    ``isolate_config=False`` — the highest-precedence source wins on
    reload."""

    skill_id = "ovos-skill-hello-world.openvoiceos"
    plugin_active: bool = True

    def setUp(self):
        LOG.set_level("DEBUG")
        self._tmp_conf = self._write_config(
            {"utterance_transformers": {
                PLUGIN_NAME: {"active": self.plugin_active}}})
        self._orig_xdg = Configuration.xdg_configs[:]
        Configuration.xdg_configs = (
            [LocalConf(self._tmp_conf)] + Configuration.xdg_configs)
        Configuration.reload()

        self.minicroft = get_minicroft(
            [self.skill_id], isolate_config=False)

    def tearDown(self):
        if self.minicroft:
            self.minicroft.stop()
        Configuration.xdg_configs = self._orig_xdg
        Configuration.reload()
        os.unlink(self._tmp_conf)
        LOG.set_level("CRITICAL")

    @staticmethod
    def _write_config(data: dict) -> str:
        fd, path = tempfile.mkstemp(prefix="cancel-plugin-test-",
                                    suffix=".json")
        with os.fdopen(fd, "w") as fh:
            json.dump(data, fh)
        return path

    @staticmethod
    def _utterance(text: str, session: Session) -> Message:
        return Message(
            "recognizer_loop:utterance",
            {"utterances": [text], "lang": session.lang},
            {"session": session.serialize(),
             "source": "A", "destination": "B"})


class TestCancelPluginEnabled(_CancelPluginTestBase):
    """The OVOS default config ships this plugin enabled; assert that
    explicitly here as well to keep the test future-proof against
    upstream config changes."""

    plugin_active = True

    # --- positive: cancel fires --------------------------------------------

    def test_cancel_mid_sentence(self):
        """An utterance ending with a cancel phrase is dropped before
        intent matching — the cancel sequence is emitted instead."""
        session = Session("123")
        session.lang = "en-US"
        message = self._utterance(
            "can you tell me the...ummm...oh, nevermind that", session)

        End2EndTest(
            minicroft=self.minicroft,
            skill_ids=[self.skill_id],
            source_message=message,
            final_session=session,
            expected_messages=[
                message,
                Message("mycroft.audio.play_sound", {"uri": "snd/cancel.mp3"}),
                Message("ovos.utterance.cancelled", {}),
                Message("ovos.utterance.handled", {}),
            ],
        ).execute(timeout=10)

    def test_cancel_suffix_on_arbitrary_utterance(self):
        """The suffix fires regardless of whether the leading utterance
        would have matched a skill."""
        session = Session("123")
        session.lang = "en-US"
        message = self._utterance("hello world cancel command", session)

        End2EndTest(
            minicroft=self.minicroft,
            skill_ids=[self.skill_id],
            source_message=message,
            expected_messages=[
                message,
                Message("mycroft.audio.play_sound", {"uri": "snd/cancel.mp3"}),
                Message("ovos.utterance.cancelled", {}),
                Message("ovos.utterance.handled", {}),
            ],
        ).execute(timeout=10)

    # --- skip-prefix veto (issue #7 partial fix) ---------------------------

    def test_blacklist_prefix_vetoes_cancel(self):
        """An utterance starting with a phrase from ``cancel.blacklist``
        bypasses the cancel suffix match even when it ends in a cancel
        word (OVOS-INTENT-2 §4.3 blacklist role).

        Partial fix for issue #7: utterances *about* the cancel word
        (define / spell / pronounce / what-is / how-do-you / ...) are
        not commands to cancel."""
        session = Session("123")
        session.lang = "en-US"
        # ``nevermind that`` IS in en-US/cancel.voc — without the
        # blacklist prefix, ``hello world nevermind that`` fires the
        # cancel sequence (see test_cancel_suffix_on_arbitrary_utterance).
        # ``spell`` as a blacklist prefix vetoes it.
        message = self._utterance("spell nevermind that", session)

        End2EndTest(
            minicroft=self.minicroft,
            skill_ids=[self.skill_id],
            source_message=message,
            expected_messages=[
                message,
                # No cancel sequence — intent failure (hello-world
                # doesn't register a "spell" intent in this rig).
                Message("mycroft.audio.play_sound", {"uri": "snd/error.mp3"}),
                Message("complete_intent_failure", {}),
                Message("ovos.utterance.handled", {}),
            ],
        ).execute(timeout=10)

    # --- smoke: passthrough --------------------------------------------------

    def test_passthrough_without_cancel_word(self):
        """An utterance with no cancel suffix is not intercepted.

        ``hello world`` doesn't match any registered intent in this
        minimal test rig, so the expected outcome is intent-failure
        (``snd/error.mp3``) — the point being that the cancel
        sequence (``ovos.utterance.cancelled``) is **absent**, which
        the strict ovoscope message-type + count checks enforce."""
        session = Session("123")
        session.lang = "en-US"
        message = self._utterance("hello world", session)

        End2EndTest(
            minicroft=self.minicroft,
            skill_ids=[self.skill_id],
            source_message=message,
            expected_messages=[
                message,
                Message("mycroft.audio.play_sound", {"uri": "snd/error.mp3"}),
                Message("complete_intent_failure", {}),
                Message("ovos.utterance.handled", {}),
            ],
        ).execute(timeout=10)


class TestCancelPluginDisabled(_CancelPluginTestBase):
    """Negative gate. With the plugin explicitly disabled, the same
    cancel-suffix utterance is **not** intercepted: it falls through
    to intent matching and lands on the intent-failure error sound.
    This proves the positive test above is observing the plugin
    itself, not some unrelated component."""

    plugin_active = False

    def test_cancel_suffix_falls_through_when_disabled(self):
        session = Session("123")
        session.lang = "en-US"
        message = self._utterance(
            "can you tell me the...ummm...oh, nevermind that", session)

        End2EndTest(
            minicroft=self.minicroft,
            skill_ids=[self.skill_id],
            source_message=message,
            expected_messages=[
                message,
                # No cancel sequence — intent failure plays the error
                # sound and emits handled.
                Message("mycroft.audio.play_sound", {"uri": "snd/error.mp3"}),
                Message("complete_intent_failure", {}),
                Message("ovos.utterance.handled", {}),
            ],
        ).execute(timeout=10)
