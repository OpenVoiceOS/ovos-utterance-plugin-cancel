# ovos-utterance-plugin-cancel

[![PyPI](https://img.shields.io/pypi/v/ovos-utterance-plugin-cancel)](https://pypi.org/project/ovos-utterance-plugin-cancel/)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)

An [OpenVoiceOS](https://openvoiceos.org) utterance transformer plugin that cancels an utterance when the user says a cancel/nevermind phrase at the end.

**Example:** *"Hey Mycroft, can you tell me the weather in… ugh, nevermind that"* → utterance is dropped, no skill fires.

## Installation

```bash
pip install ovos-utterance-plugin-cancel
```

## How it works

The plugin runs before skill matching. It checks whether the utterance tail matches any phrase from `locale/<lang>/cancel.intent`. On a match, it returns an empty utterance list with context `{"canceled": True, "cancel_word": "<phrase>"}`.

Language selection is automatic via `langcodes.closest_match`. Phrases support bracket-expansion syntax (e.g. `cancel (it|that)`).

## Supported languages

`ca-ES` · `da-DK` · `de-DE` · `en-US` · `es-ES` · `fr-FR` · `gl-ES` · `it-IT` · `nl-NL` · `pt-BR` · `pt-PT`

To add a language, create `ovos_utterance_plugin_cancel/locale/<lang>/cancel.intent` with one phrase per line.

## Configuration

This plugin is **enabled by default** in `ovos-config` alongside the other standard utterance transformers:

```json
"utterance_transformers": {
    "ovos-utterance-normalizer": {},
    "ovos-utterance-plugin-cancel": {},
    "ovos-utterance-corrections-plugin": {}
}
```

To disable it, add `"enable": false` to your config:

```json
"utterance_transformers": {
    "ovos-utterance-plugin-cancel": {"enable": false}
}
```

## Development

```bash
git clone https://github.com/OpenVoiceOS/ovos-utterance-plugin-cancel
cd ovos-utterance-plugin-cancel
pip install -e ".[dev]"
uv run pytest test/ -v --cov=ovos_utterance_plugin_cancel
```

## Credits

- [@penrods](https://github.com/MycroftAI/mycroft-core/pull/1274) — original Mycroft PR
- [NeonGecko](https://github.com/NeonGeckoCom/neon-utterance-plugin-cancel) — original plugin
