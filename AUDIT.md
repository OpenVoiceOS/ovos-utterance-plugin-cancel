# AUDIT — ovos-utterance-plugin-cancel

## Known Issues

| Severity | File | Line | Issue |
|----------|------|------|-------|
| Medium | `__init__.py` | 44 | `os.listdir` on locale dir is called inside `lru_cache` — directory scan happens once per language per process, but adding locale files at runtime won't be reflected. |
| Medium | `__init__.py` | 68 | Only `utterance.endswith(phrase)` is checked — phrases mid-sentence are not caught. Intentional but undocumented. |
| Low | `setup.py` | — | Uses legacy `setup.py`; should migrate to `pyproject.toml`. |
| Low | `setup.py` | 87 | Classifiers list Python 3.4/3.5/3.6; package requires 3.10+ (OVOS ecosystem). |
| Low | `__init__.py` | 1-24 | Neon AI BSD-style license header; file is Apache 2.0. Header should be removed or updated. |

## Technical Debt

- `scripts/` (prepare/sync translations) deleted from working tree but not committed — requires a commit to clean up.
- `translations/` JSON files deleted from working tree — same pending commit needed.
- Old lowercase locale paths (`ca-es`, `de-de`, …) staged as deleted; cleanup commit required.
