from __future__ import annotations

from app.models import ProcessingJob


class ProcessingJobService:
    def mark_queued(self, job: ProcessingJob) -> ProcessingJob:
        job.status = "queued"
        job.current_step = "validate_image"
        job.progress_percent = 0
        return job
