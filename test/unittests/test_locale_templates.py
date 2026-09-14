"""Validate every locale resource line against the OVOS-INTENT-1 grammar."""
import os
import unittest

from ovos_spec_tools.expansion import expand

import ovos_utterance_plugin_cancel

PACKAGE_ROOT = os.path.dirname(ovos_utterance_plugin_cancel.__file__)
LOCALE_ROOT = os.path.join(PACKAGE_ROOT, "locale")
RESOURCE_EXTENSIONS = (".voc", ".intent", ".dialog", ".entity", ".rx")


def iter_resource_lines():
    """Yield (path, line_number, line) for every template line in locale/."""
    for dirpath, _dirs, files in os.walk(LOCALE_ROOT):
        for fname in sorted(files):
            if not fname.endswith(RESOURCE_EXTENSIONS):
                continue
            path = os.path.join(dirpath, fname)
            with open(path, encoding="utf-8") as fh:
                for lineno, line in enumerate(fh, 1):
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    yield path, lineno, line


class TestLocaleTemplates(unittest.TestCase):
    def test_locale_root_exists(self):
        self.assertTrue(os.path.isdir(LOCALE_ROOT))

    def test_all_templates_expand(self):
        failures = []
        for path, lineno, line in iter_resource_lines():
            try:
                expand(line)
            except Exception as err:
                rel = os.path.relpath(path, PACKAGE_ROOT)
                failures.append(f"{rel}:{lineno}: {line!r} -> {err}")
        self.assertEqual(
            failures, [],
            "malformed locale template lines:\n" + "\n".join(failures))


if __name__ == "__main__":
    unittest.main()
