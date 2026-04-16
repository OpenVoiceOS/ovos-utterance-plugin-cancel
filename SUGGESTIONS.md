# SUGGESTIONS — ovos-utterance-plugin-cancel

## Proposed enhancements

1. **Migrate to `pyproject.toml`** — replace `setup.py` with a `pyproject.toml` (hatchling or setuptools) for PEP 517 compliance and `uv` compatibility.

2. **Match anywhere, not just tail** — optionally match cancel phrases at any position. Would require a config flag to avoid changing default behaviour.

3. **Invalidate LRU cache on locale change** — replace `@lru_cache` with a manual dict + inotify/mtime check so locale hot-reload works without restarting OVOS.

4. **Remove Neon AI license header** — `__init__.py:1-24` contains a BSD-style header that conflicts with the Apache 2.0 licence declared in `setup.py` and `LICENSE`. Removing it (or replacing with a one-line Apache notice) would resolve the ambiguity.

5. **Add `py.typed` marker** — makes the package PEP 561-compliant for mypy consumers.
