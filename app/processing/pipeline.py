from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from flask import current_app

from app.extensions import db
from app.models import Contour, ProcessedImage, ProcessingJob, SourceImage, Tool
from app.processing.contour_extraction import ContourExtractionService
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

        background_width_mm = job.source_image.background_width_mm or 210.0
        background_height_mm = job.source_image.background_height_mm or 297.0
        detector = PageDetectionService()
        result = detector.detect(
            source_path,
            expected_width_mm=background_width_mm,
            expected_height_mm=background_height_mm,
        )
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
                page_width_mm=background_width_mm,
                page_height_mm=background_height_mm,
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

            contour_overlay_path = (
                storage_root
                / "users"
                / str(job.user_id)
                / "tools"
                / str(job.tool_id)
                / "contours"
                / f"outer_contour_overlay_job_{job.id}.png"
            )
            aligned_contour_path = (
                storage_root
                / "users"
                / str(job.user_id)
                / "tools"
                / str(job.tool_id)
                / "contours"
                / f"aligned_outer_contour_job_{job.id}.png"
            )
            job.current_step = "extract_contours"
            job.progress_percent = 85
            db.session.commit()

            contour_result = ContourExtractionService().extract_outer_contour_overlay(
                image_path=corrected_path,
                mask_path=mask_path,
                output_path=contour_overlay_path,
                pixels_per_mm=correction.pixels_per_mm,
                aligned_output_path=aligned_contour_path,
            )
            warnings = segmentation.warnings + contour_result.warnings
            if not contour_result.warnings:
                db.session.add(
                    ProcessedImage(
                        processing_job_id=job.id,
                        image_type="contour_overlay",
                        file_path=contour_overlay_path.relative_to(storage_root).as_posix(),
                        width_px=correction.width_px,
                        height_px=correction.height_px,
                    )
                )
                db.session.add(
                    ProcessedImage(
                        processing_job_id=job.id,
                        image_type="aligned_contour_preview",
                        file_path=aligned_contour_path.relative_to(storage_root).as_posix(),
                        width_px=contour_result.width_px,
                        height_px=contour_result.height_px,
                    )
                )
                Contour.query.filter_by(tool_id=job.tool_id, is_active=True).update({"is_active": False})
                db.session.add(
                    Contour(
                        tool_id=job.tool_id,
                        processing_job_id=job.id,
                        contour_type="outer_detected",
                        geometry_data=contour_result.geometry_data,
                        width_mm=contour_result.width_mm,
                        height_mm=contour_result.height_mm,
                        area_mm2=contour_result.area_mm2,
                        perimeter_mm=contour_result.perimeter_mm,
                        is_active=True,
                    )
                )

            job.current_step = "completed" if not warnings else "extract_contours"
            job.progress_percent = 100 if not warnings else 85
            job.error_code = ",".join(warnings) if warnings else None
            if warnings:
                job.status = "completed_with_warning"
                job.error_message = "Werkzeugmaske und Kontur wurden erzeugt, enthalten aber Warnungen."
                job.tool.status = "warning"
            else:
                job.status = "completed"
                job.error_message = "Aussenkontur wurde erkannt und als rote Overlay-Vorschau erzeugt."
                job.tool.status = "ready"
        else:
            job.status = "failed"
            job.current_step = "detect_page"
            job.progress_percent = 20
            job.error_code = ",".join(result.warnings) or "page_not_found"
            job.error_message = "Hintergrund konnte nicht sicher erkannt werden."
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
