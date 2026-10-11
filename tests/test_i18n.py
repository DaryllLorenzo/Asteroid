# ---------------------------------------------------
# Project: Asteroid
# Author: Daryll Lorenzo Alfonso
# Year: 2025
# License: MIT License
# ---------------------------------------------------

"""Translation catalogue integrity.

`tr()` resolves by exact-string lookup against `es.json`, and English is the
source language: there is no `en.json`, and a missing key simply returns the
argument unchanged. A string therefore only reaches the Spanish UI if it is
present in the catalogue byte for byte.

Call sites whose argument is *not* a literal (f-strings, variables) are out of
scope by construction: their key depends on runtime values and cannot be
checked statically.
"""

from __future__ import annotations

import ast
import json
from pathlib import Path

from app.i18n import load_language
from app.i18n import tr

APP_ROOT = Path(__file__).resolve().parent.parent / "app"
CATALOGUE_PATH = APP_ROOT / "i18n" / "es.json"

# Strings that are wrapped in tr() but absent from es.json, i.e. they currently
# render untranslated. Listing them here keeps the catalogue test green while
# still failing on any *new* omission. Removing an entry once the string is
# translated makes this test fail until the list is updated.
KNOWN_UNTRANSLATED = {"Node"}


def _literal_tr_arguments() -> dict[str, set[str]]:
    """Map each source file to the set of literals passed to tr()."""
    found: dict[str, set[str]] = {}
    for source in sorted(APP_ROOT.rglob("*.py")):
        tree = ast.parse(source.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Name)
                and node.func.id == "tr"
                and node.args
                and isinstance(node.args[0], ast.Constant)
                and isinstance(node.args[0].value, str)
            ):
                found.setdefault(source.name, set()).add(node.args[0].value)
    return found


def _missing_keys() -> dict[str, set[str]]:
    catalogue = json.loads(CATALOGUE_PATH.read_text(encoding="utf-8"))
    return {
        name: literals - set(catalogue) - KNOWN_UNTRANSLATED
        for name, literals in _literal_tr_arguments().items()
        if literals - set(catalogue) - KNOWN_UNTRANSLATED
    }


class TestTranslationCatalogue:
    def test_catalogue_is_valid_json(self) -> None:
        data = json.loads(CATALOGUE_PATH.read_text(encoding="utf-8"))
        assert isinstance(data, dict)
        assert data, "es.json is empty"

    def test_catalogue_entries_are_non_empty_strings(self) -> None:
        data = json.loads(CATALOGUE_PATH.read_text(encoding="utf-8"))
        for key, value in data.items():
            assert isinstance(value, str), key
            assert value.strip(), key

    def test_every_literal_is_translated(self) -> None:
        """No call site may introduce a new untranslated string."""
        assert _missing_keys() == {}

    def test_known_untranslated_list_is_accurate(self) -> None:
        """The allow-list must track reality in both directions."""
        catalogue = json.loads(CATALOGUE_PATH.read_text(encoding="utf-8"))
        still_missing = {
            text
            for literals in _literal_tr_arguments().values()
            for text in literals & KNOWN_UNTRANSLATED
            if text not in catalogue
        }
        assert still_missing == KNOWN_UNTRANSLATED

    def test_source_language_fallback(self) -> None:
        """With no catalogue loaded, tr() returns its argument unchanged."""
        load_language("en")
        assert tr("An untranslated sentence") == "An untranslated sentence"

    def test_lookup_is_exact_match(self) -> None:
        """A near-miss does not resolve, so wording must match byte for byte."""
        load_language("es")
        catalogue = json.loads(CATALOGUE_PATH.read_text(encoding="utf-8"))
        key = (
            "Cannot add an Actor/Agent inside another Actor/Agent's subcanvas."
            " Subcanvases are for Tropos elements"
            " (Goals, Resources, Plans, Softgoals)."
        )

        assert key in catalogue
        assert tr(key) == catalogue[key]
        assert tr(key.lower()) == key.lower()
        assert tr(f"{key} ") == f"{key} "
