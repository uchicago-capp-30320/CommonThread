"""

This module has 2 main functions:
1. Keep listening to the sqs queue
2  Process the message and update the database table (MLProcessingQueue) with the task status.
"""
from ..ml.ml_services.summarizing_service import SummarizingService
from ..ml.ml_services.tagging_service import TaggingService
from ..ml.ml_services.transcribing_service import TranscribingService   
from ..ml.ml_services.insight_service import InsightService

from ..models import Story
from typing import List

import os
import json
import boto3
import logging
import time

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

QUEUE_URL = os.getenv("CT_SQS_QUEUE_URL")
sqs = boto3.client("sqs", region_name="us-east-1")


class MLWorkerService:
    def __init__(self):
        self.tagging_service = TaggingService()
        self.summary_service = SummarizingService()
        self.insight_service = InsightService()
        self.transcribing_service = TranscribingService()

    def _dispatch(self, body: dict):
        """
        Shared dispatch logic for a single job payload.
        """
        job_id = body.get("job_id")
        task_type = body.get("task_type")
        story_id = body.get("story_id")
        logger.info("Dispatching job_id=%s, type=%s", job_id, task_type)
        if task_type == "transcribe_audio":
            self.transcribing_service.process_story_transcription(story_id)
        elif task_type == "extract_tags":
            self.tagging_service.process_story_tagging(story_id)
        elif task_type == "summarize":
            self.summary_service.process_story_summarization(story_id)
        elif task_type == "extract_insights":
            self.insight_service.process_story_insights(story_id)
        else:
            logger.error("Unknown task_type %s for job_id=%s", task_type, job_id)
    def process_messages(self, use_lambda: bool = False, event: dict = None, context=None):
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
                    logger.exception("Failed to dispatch Lambda record %s", record.get("messageId"))
                    raise
            return {"status": "ok"}

        # Poll mode
        if not QUEUE_URL:
            logger.error("AWS_SQS_QUEUE_URL not set. Exiting.")
            return
        logger.info("Starting SQS poll loop on %s", QUEUE_URL)
        while True:
            resp = sqs.receive_message(
                QueueUrl=QUEUE_URL,
                MaxNumberOfMessages=10,
                WaitTimeSeconds=20,
            )
            messages = resp.get("Messages", [])
            for msg in messages:
                receipt = msg.get("ReceiptHandle")
                try:
                    body = json.loads(msg.get("Body", "{}"))
                    self._dispatch(body)
                    sqs.delete_message(QueueUrl=QUEUE_URL, ReceiptHandle=receipt)
                    logger.info("Deleted message job_id=%s", body.get("job_id"))
                except Exception:
                    logger.exception("Failed to process message id=%s", msg.get("MessageId"))
            time.sleep(1)

if __name__ == "__main__":
    MLWorkerService().process_messages()