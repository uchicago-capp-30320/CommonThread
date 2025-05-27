"""
This module has 2 main functions:
1. Keep listening to the sqs queue
2  Process the message and update the database table (MLProcessingQueue) with the task status.
"""

import os
import django
import json
import boto3
import logging
import time
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "commonthread.settings")
django.setup()

# THIS HAS TO BE BELOW THE DJANGO SETUP
from ..ml.ml_services.summarizing_service import SummarizingService #noqa: E402
from ..ml.ml_services.tagging_service import TaggingService #noqa: E402
from ..ml.ml_services.transcribing_service import TranscribingService #noqa: E402
from ..models import MLProcessingQueue, Story, Project #noqa: E402
from commonthread.settings import CT_SQS_QUEUE_URL #noqa: E402


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


sqs = boto3.client("sqs", region_name="us-east-1")


class MLWorkerService:
    def __init__(self):
        self.tagging_service = TaggingService()
        self.summarizing_service = SummarizingService()
        self.transcribing_service = TranscribingService()

    def _dispatch(self, body: dict):
        """
        Shared dispatch logic for a single job payload.
        """
        job_id = body.get("job_id")
        task_type = body.get("task_type")
        story_id = body.get("story_id", None)
        project_id = body.get("project_id", None)

        logger.info("Dispatching job_id=%s, type=%s", job_id, task_type)

        self._create_queue_entries(body, status="processing")
        success = False
        try:
            if task_type == "transcription":
                success = self.transcribing_service.process_story_transcription(
                    story_id
                )
            elif task_type == "tag":
                success = self.tagging_service.process_story_tags(story_id)

            elif task_type == "summarization":
                success = self.summarizing_service.process_project_summary(project_id)

            else:
                logger.error("Unknown task_type %s for job_id=%s", task_type, job_id)

        except Exception:
            logger.exception(
                "Error processing task_type=%s, job_id=%s: %s",
                task_type,
                job_id,
            )
        self._create_queue_entries(body, status="completed" if success else "failed")


    def _create_queue_entries(
        self, task_body: dict, status: str
    ) -> MLProcessingQueue:
        """
        Update or Create a metadata entry for the given task body
        timestamp and status.
        """
        story_id = task_body.get("story_id")
        project_id = task_body.get("project_id")

        try:
            story = Story.objects.get(id=story_id) if story_id else None
            project = Project.objects.get(id=project_id) if project_id else None
        except ObjectDoesNotExist as e:
            logger.error(f"Failed to create queue entry: {str(e)}")
            raise

        #update the status of the task for existing task
        entry, _ = MLProcessingQueue.objects.update_or_create(
            story=story,
            project=project,
            task_type=task_body.get("task_type"),
            defaults={
                "status": status,
                "timestamp": timezone.now(),
            }
        )
        return entry

    def process_messages(
        self, use_lambda: bool = False, event: dict = None, context=None
    ):
        """
        Entry point for processing ML tasks.

        If use_lambda=True, handles an SQS-triggered Lambda event.
        Otherwise, starts a long-poll loop on the configured SQS queue.
        """
        if use_lambda:
            # Lambda mode
            records = event.get("Records", []) if event else []
            logger.info("Lambda mode: processing %d records", len(records))
            for record in records:
                try:
                    body = json.loads(record.get("body", "{}"))
                    self._dispatch(body)
                except Exception:
                    logger.exception(
                        "Failed to dispatch Lambda record %s", record.get("messageId")
                    )
                    raise
            return {"status": "ok"}

        if not CT_SQS_QUEUE_URL:
            logger.error("CT_SQS_QUEUE_URL not set. Exiting.")
            return
        logger.info("Starting SQS poll loop on %s", CT_SQS_QUEUE_URL)
        while True:
            resp = sqs.receive_message(
                QueueUrl=CT_SQS_QUEUE_URL,
                MaxNumberOfMessages=10,
                WaitTimeSeconds=20,
            )
            messages = resp.get("Messages", [])
            for msg in messages:
                receipt = msg.get("ReceiptHandle")
                try:
                    body = json.loads(msg.get("Body", "{}"))
                    self._dispatch(body)
                    sqs.delete_message(QueueUrl=CT_SQS_QUEUE_URL, ReceiptHandle=receipt)
                    logger.info("Deleted message job_id=%s", body.get("job_id"))
                except Exception:
                    logger.exception(
                        "Failed to process message id=%s", msg.get("MessageId")
                    )
            time.sleep(1)


if __name__ == "__main__":
    MLWorkerService().process_messages()
