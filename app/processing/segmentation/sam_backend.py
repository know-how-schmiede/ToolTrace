from .base import SegmentationBackend, SegmentationResult


class SamSegmentationBackend(SegmentationBackend):
    def segment(self, image_path: str) -> SegmentationResult:
        raise NotImplementedError("Segment Anything ist fuer spaetere Versionen vorgesehen.")
