from __future__ import annotations

from app.extensions import db
from app.models import ProcessingJob, SourceImage, Tool


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
        raise NotImplementedError("Die OpenCV-Verarbeitung wird im naechsten Entwicklungsschritt implementiert.")
