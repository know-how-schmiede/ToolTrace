from .base import SegmentationBackend, SegmentationResult


class YoloSegmentationBackend(SegmentationBackend):
    def segment(self, image_path: str) -> SegmentationResult:
        raise NotImplementedError("YOLO-Segmentierung ist fuer spaetere Versionen vorgesehen.")
