from .base import SegmentationBackend, SegmentationResult


class OpenCVSegmentationBackend(SegmentationBackend):
    def segment(self, image_path: str) -> SegmentationResult:
        raise NotImplementedError("OpenCV-Segmentierung ist noch nicht implementiert.")
