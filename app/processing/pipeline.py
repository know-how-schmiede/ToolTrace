from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from flask import current_app

from app.extensions import db
from app.models import ProcessedImage, ProcessingJob, SourceImage, Tool
from app.processing.page_detection import PageDetectionService
from app.processing.perspective import PerspectiveCorrectionService
from app.processing.segmentation.opencv_backend import OpenCVSegmentationBackend


class ToolProcessingPipeline:
    steps = (
        "validate_image",
        "detect_page",
        "correct_perspective",
        "segment_tool",
        "clean_mask",
        "extract_contours",
        "convert_to_mm",
        "align_contour",
        "generate_preview",
        "completed",
    )

    def enqueue_placeholder(self, *, tool: Tool, source_image: SourceImage, user_id: int) -> ProcessingJob:
        job = ProcessingJob(
            tool_id=tool.id,
            source_image_id=source_image.id,
            user_id=user_id,
            status="queued",
            current_step=self.steps[0],
            progress_percent=0,
        )
        tool.status = "processing"
        db.session.add(job)
        db.session.commit()
        return job

    def run(self, processing_job_id: int) -> None:
        job = db.session.get(ProcessingJob, processing_job_id)
        if job is None:
            raise ValueError("processing_job_not_found")
        if job.source_image is None:
            raise ValueError("source_image_not_found")

        job.status = "running"
        job.current_step = "detect_page"
        job.progress_percent = 20
        job.started_at = datetime.now(timezone.utc)
        db.session.commit()

        storage_root = Path(current_app.config["STORAGE_PATH"]).resolve()
        source_path = (storage_root / job.source_image.original_path).resolve()
        if storage_root not in source_path.parents or not source_path.is_file():
            self._mark_failed(job, "source_image_missing", "Das Quellbild wurde nicht gefunden.")
            return

        preview_path = (
            storage_root
            / "users"
            / str(job.user_id)
            / "tools"
            / str(job.tool_id)
            / "processed"
            / f"page_detected_job_{job.id}.png"
        )

        detector = PageDetectionService()
        result = detector.detect(source_path)
        preview_width, preview_height = detector.write_preview(source_path, result, preview_path)

        job.source_image.page_detection_score = result.score
        processed_image = ProcessedImage(
            processing_job_id=job.id,
            image_type="page_detected",
            file_path=preview_path.relative_to(storage_root).as_posix(),
            width_px=preview_width,
            height_px=preview_height,
        )
        db.session.add(processed_image)

        if result.found:
            job.current_step = "correct_perspective"
            job.progress_percent = 40
            db.session.commit()

            corrected_path = (
                storage_root
                / "users"
                / str(job.user_id)
                / "tools"
                / str(job.tool_id)
                / "processed"
                / f"perspective_corrected_job_{job.id}.png"
            )
            correction = PerspectiveCorrectionService().correct(
                source_path,
                result.corners,
                corrected_path,
                current_app.config["PROCESSING_PIXELS_PER_MM"],
            )
            db.session.add(
                ProcessedImage(
                    processing_job_id=job.id,
                    image_type="perspective_corrected",
                    file_path=corrected_path.relative_to(storage_root).as_posix(),
                    width_px=correction.width_px,
                    height_px=correction.height_px,
                )
            )
            job.current_step = "segment_tool"
            job.progress_percent = 65
            db.session.commit()

            mask_path = (
                storage_root
                / "users"
                / str(job.user_id)
                / "tools"
                / str(job.tool_id)
                / "masks"
                / f"cleaned_mask_job_{job.id}.png"
            )
            segmentation = OpenCVSegmentationBackend().segment(corrected_path, mask_path)
            job.source_image.segmentation_score = segmentation.confidence
            db.session.add(
                ProcessedImage(
                    processing_job_id=job.id,
                    image_type="cleaned_mask",
                    file_path=mask_path.relative_to(storage_root).as_posix(),
                    width_px=segmentation.width_px,
                    height_px=segmentation.height_px,
                )
            )

            job.status = "completed_with_warning"
            job.current_step = "clean_mask"
            job.progress_percent = 75
            job.error_code = ",".join(segmentation.warnings) if segmentation.warnings else None
            if segmentation.warnings:
                job.error_message = "Werkzeugmaske wurde erzeugt, enthaelt aber Warnungen."
                job.tool.status = "warning"
            else:
                job.error_message = "Werkzeugmaske wurde aus dem perspektivisch entzerrten Bild erzeugt. Konturerkennung ist der naechste Verarbeitungsschritt."
                job.tool.status = "processing"
        else:
            job.status = "failed"
            job.current_step = "detect_page"
            job.progress_percent = 20
            job.error_code = ",".join(result.warnings) or "page_not_found"
            job.error_message = "DIN-A4-Blatt konnte nicht sicher erkannt werden."
            job.tool.status = "warning"
        job.finished_at = datetime.now(timezone.utc)
        db.session.commit()

    def _mark_failed(self, job: ProcessingJob, code: str, message: str) -> None:
        job.status = "failed"
        job.error_code = code
        job.error_message = message
        job.finished_at = datetime.now(timezone.utc)
        job.tool.status = "error"
        db.session.commit()
