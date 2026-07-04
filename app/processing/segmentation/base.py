from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class SegmentationResult:
    mask_path: str | None = None
    confidence: float | None = None
    warnings: list[str] = field(default_factory=list)
    width_px: int | None = None
    height_px: int | None = None
    foreground_area_px: int = 0


class SegmentationBackend:
    def segment(self, image_path: str) -> SegmentationResult:
        raise NotImplementedError
