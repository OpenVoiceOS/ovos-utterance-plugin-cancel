# AI Transparency Log

## 2026-04-16

**AI Model:** claude-sonnet-4-6  
**Actions Taken:**
- Added unit tests (`test/unittests/test_plugin.py`) covering transform, cancel detection, language fallback, and LRU cache behaviour.
- Created `docs/index.md` with architecture description and source citations.
- Rewrote `README.md` with badges, install instructions, and developer quickstart.
- Created `FAQ.md` with common questions and source citations.
- Created `AUDIT.md` and `SUGGESTIONS.md`.
- Modernized GitHub Actions workflows: updated `TigreGotico/gh-automations` refs from `@master` to `@dev`, replaced deprecated `set-output` with `$GITHUB_OUTPUT`, removed redundant `create-release` step from stable workflow, replaced `python setup.py` invocations with `python -m build`.

**Oversight:** Human review before merge.
