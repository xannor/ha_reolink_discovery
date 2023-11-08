"""Generate translations/en.json from strings.json"""
import json
import os
from pathlib import Path
import re
import sys
from typing import cast

import homeassistant

#from script.translations import develop
class develop:
    @staticmethod
    def flatten_translations(translations):
        """Flatten all translations."""
        stack = [iter(translations.items())]
        key_stack = []
        flattened_translations = {}
        while stack:
            for k, v in stack[-1]:
                key_stack.append(k)
                if isinstance(v, dict):
                    stack.append(iter(v.items()))
                    break
                elif isinstance(v, str):
                    common_key = "::".join(key_stack)
                    flattened_translations[common_key] = v
                    key_stack.pop()
            else:
                stack.pop()
                if key_stack:
                    key_stack.pop()

        return flattened_translations

    @staticmethod
    def substitute_translation_references(integration_strings, flattened_translations):
        """Recursively processes all translation strings for the integration."""
        result = {}
        for key, value in integration_strings.items():
            if isinstance(value, dict):
                sub_dict = develop.substitute_translation_references(value, flattened_translations)
                result[key] = sub_dict
            elif isinstance(value, str):
                result[key] = develop.substitute_reference(value, flattened_translations)

        return result

    @staticmethod
    def substitute_reference(value, flattened_translations):
        """Substitute localization key references in a translation string."""
        matches = re.findall(r"\[\%key:([a-z0-9_]+(?:::(?:[a-z0-9-_])+)+)\%\]", value)
        if not matches:
            return value

        new = value
        for key in matches:
            if key in flattened_translations:
                new = new.replace(
                    f"[%key:{key}%]",
                    # New value can also be a substitution reference
                    develop.substitute_reference(
                        flattened_translations[key], flattened_translations
                    ),
                )
            else:
                print(f"Invalid substitution key '{key}' found in string '{value}'")
                sys.exit(1)

        return new
#from script.translations.upload import FILENAME_FORMAT
FILENAME_FORMAT = re.compile(r"strings\.(?P<suffix>\w+)\.json")

COMPONENTS_DIR = Path(__file__).parent.parent / "custom_components"

HASS_STRINGS = Path(homeassistant.__file__).parent / "strings.json"

translations: dict[str, any] = json.loads(HASS_STRINGS.read_text())
translations["component"] = {}

for path in COMPONENTS_DIR.glob(f"*{os.sep}strings*.json"):
    component = path.parent.name
    match = FILENAME_FORMAT.search(path.name)
    platform = match.group("suffix") if match else None

    parent: dict[str, any] = translations["component"].setdefault(component, {})

    if platform:
        platforms: dict[str, any] = parent.setdefault("platform", {})
        parent = platforms.setdefault(platform, {})

    parent.update(json.loads(path.read_text()))

flattened_translations = develop.flatten_translations(translations)

for integration in cast(dict[str, any], translations["component"]).keys():
    integration_strings = translations["component"][integration]

    translations["component"][integration] = develop.substitute_translation_references(
        integration_strings, flattened_translations
    )

    transdir = (COMPONENTS_DIR / integration) / "translations"

    if not transdir.is_dir():
        transdir.mkdir(parents=True)
    (transdir / "en.json").write_text(
        json.dumps(translations["component"][integration])
    )
