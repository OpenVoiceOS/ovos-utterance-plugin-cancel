# FAQ — ovos-utterance-plugin-cancel

**Q: Why didn't my "nevermind" phrase get detected?**  
A: The plugin only matches phrases at the **end** of the utterance (`utterance.endswith(phrase)`). The phrase must be listed in `locale/<lang>/cancel.intent` and the language must match within a `langcodes` distance of 10.

**Q: How do I add cancel phrases for a new language?**  
A: Create `ovos_utterance_plugin_cancel/locale/<BCP-47>/cancel.intent` with one phrase per line. Bracket expansion is supported: `cancel (it|that)`.

**Q: The cache seems stale — new locale files aren't being picked up.**  
A: `get_cancel_words` is `@lru_cache`'d per language for the process lifetime — `__init__.py:43`. Restart the OVOS process after editing locale files.

**Q: What context keys does the plugin set on cancel?**  
A: `{"canceled": True, "cancel_word": "<matched phrase>"}` — `__init__.py:69`.

**Q: What is the plugin priority?**  
A: 15 (lower = earlier). Set in `NevermindPlugin.__init__` — `__init__.py:39`.

**Q: Which entry point does OVOS use to discover this plugin?**  
A: `ovos.utterance.transformer` — `setup.py:97`. The plugin key is `ovos-utterance-cancel-plugin`.
