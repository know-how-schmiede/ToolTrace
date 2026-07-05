from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation


@dataclass(frozen=True)
class BackgroundPreset:
    key: str
    name: str
    width_mm: float
    height_mm: float

    @property
    def label(self) -> str:
        return f"{self.name} ({format_mm_as_cm(self.width_mm)} x {format_mm_as_cm(self.height_mm)} cm)"


DEFAULT_BACKGROUND_PRESETS = [
    BackgroundPreset("light_table_a4", "Leuchttisch A4", 313.0, 215.0),
    BackgroundPreset("light_table_a5", "Leuchttisch A5", 215.0, 158.0),
    BackgroundPreset("light_table_a3", "Leuchttisch A3", 430.0, 313.0),
]


def format_mm_as_cm(value_mm: float) -> str:
    value = Decimal(str(value_mm)) / Decimal("10")
    return f"{value.normalize():f}".replace(".", ",")


def cm_to_mm(value: str) -> float:
    normalized = (value or "").strip().replace(",", ".")
    try:
        parsed = Decimal(normalized)
    except InvalidOperation as exc:
        raise ValueError("ungueltige_groesse") from exc
    if parsed <= 0 or parsed > 200:
        raise ValueError("ungueltige_groesse")
    return float(parsed * Decimal("10"))


def default_background_presets_json() -> list[dict]:
    return [
        {"key": preset.key, "name": preset.name, "width_mm": preset.width_mm, "height_mm": preset.height_mm}
        for preset in DEFAULT_BACKGROUND_PRESETS
    ]


def user_background_presets(user) -> list[BackgroundPreset]:
    raw_presets = user.background_presets_json or default_background_presets_json()
    presets: list[BackgroundPreset] = []
    defaults_by_key = {preset.key: preset for preset in DEFAULT_BACKGROUND_PRESETS}
    for raw in raw_presets:
        key = str(raw.get("key", "")).strip()
        default = defaults_by_key.get(key)
        name = str(raw.get("name") or (default.name if default else key)).strip()
        try:
            width_mm = float(raw.get("width_mm"))
            height_mm = float(raw.get("height_mm"))
        except (TypeError, ValueError):
            continue
        if key and name and width_mm > 0 and height_mm > 0:
            presets.append(BackgroundPreset(key, name, width_mm, height_mm))
    return presets or DEFAULT_BACKGROUND_PRESETS


def background_choices_for_user(user) -> list[tuple[str, str]]:
    return [(preset.key, preset.label) for preset in user_background_presets(user)]


def selected_background_for_user(user, key: str) -> BackgroundPreset:
    presets = user_background_presets(user)
    for preset in presets:
        if preset.key == key:
            return preset
    return presets[0]
