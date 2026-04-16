# ovos-utterance-plugin-cancel

An OVOS utterance transformer that suppresses utterances when the user cancels mid-sentence (e.g. *"Hey OVOS, turn on the… nevermind that"*).

## How it works

`NevermindPlugin` — `ovos_utterance_plugin_cancel/__init__.py:37`

The plugin is registered as an `UtteranceTransformer` (priority 15). Before any skill matching occurs, it checks whether each utterance **ends with** a known cancel phrase. If a match is found, the utterance list is replaced with an empty list and `{"canceled": True, "cancel_word": <phrase>}` is added to the context dict.

```
recognizer_loop:utterance
  └─ NevermindPlugin.transform()        # __init__.py:64
       ├─ get_cancel_words(lang)         # __init__.py:43  (LRU-cached per lang)
       └─ returns ([], {"canceled": True}) on match
```

## Configuration

No configuration required. The plugin auto-loads via the OVOS plugin manager entry point:

```
ovos.utterance.transformer = ovos-utterance-cancel-plugin = ovos_utterance_plugin_cancel:NevermindPlugin
```

## Locale support

Cancel phrases are loaded from `ovos_utterance_plugin_cancel/locale/<lang>/cancel.intent`. Supported languages:

| Code | Language |
|------|----------|
| ca-ES | Catalan |
| da-DK | Danish |
| de-DE | German |
| en-US | English |
| es-ES | Spanish |
| fr-FR | French |
| gl-ES | Galician |
| it-IT | Italian |
| nl-NL | Dutch |
| pt-BR | Portuguese (Brazil) |
| pt-PT | Portuguese (Portugal) |

Language matching uses `langcodes.closest_match` with a distance threshold of 10. If no locale is close enough, the plugin passes all utterances through unchanged.

## Installation

```bash
pip install ovos-utterance-plugin-cancel
```

## Running tests

```bash
uv run pytest test/ -v --cov=ovos_utterance_plugin_cancel --cov-report=term-missing
```
