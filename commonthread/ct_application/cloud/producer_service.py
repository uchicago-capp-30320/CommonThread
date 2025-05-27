"""
Producer Service for Machine Learning Task Queue Management

1. Adds tasks to the queue
2. Creates metadata entries for the tasks

"""

import boto3
import json
import logging
from datetime import datetime, timezone, UTC
from django.conf import settings
from django.db import transaction
from typing import Dict, List
from abc import ABC, abstractmethod
from ct_application.models import Story, MLProcessingQueue
from commonthread.settings import CT_SQS_QUEUE_URL

# Configure logging
logger = logging.getLogger(__name__)


class MLTask:
    """
    Represents a machine learning task with its configuration.

    Attributes:
        task_type (str): Type of ML task to be performed
        enabled (bool): Whether the task is currently enabled
        story_level (bool): Whether the task operates at story level
    """

    def __init__(self, task_type: str, enabled: bool = True, story_level: bool = True):
        self.task_type = task_type
        self.enabled = enabled
        self.story_level = story_level


class QueueStrategy(ABC):
    """Abstract base class defining the interface for queue strategies."""

    @abstractmethod
    def add_to_queue(self, tasks: List[MLTask], story: Story) -> Dict:
        """
        Implement specific queueing logic for the tasks.

        Args:
            tasks: List of MLTask objects to be queued
            story: Story object associated with the tasks

        Returns:
            Dict with success status and task IDs

        Raises:
            NotImplementedError: If the strategy doesn't implement this method
        """
        pass


class SQSStrategy(QueueStrategy):
    """AWS SQS implementation of the queue strategy."""

    def __init__(self):
        """Initialize SQS client with AWS credentials."""
        try:
            self.sqs = boto3.client(
                "sqs",
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_S3_REGION_NAME,
            )
            self.queue_url = CT_SQS_QUEUE_URL
        except Exception as e:
            logger.error(f"Failed to initialize SQS client: {str(e)}")
            raise

    def add_to_queue(self, tasks: List[MLTask], story: Story) -> Dict:
        """
        Add tasks to SQS queue.

        Args:
            tasks: List of MLTask objects to be queued
            story: Story object associated with the tasks

        Returns:
            Dict containing success status and task IDs

        Raises:
            Exception: If there's an error sending messages to SQS
        """
        task_ids = {}

        try:
            for task in tasks:
                job_id = f"{story.id}_{task.task_type}_{datetime.now(UTC).timestamp()}"
                message = {
                    "job_id": job_id,
                    "project_id": story.proj.id,
                    "task_type": task.task_type,
                }

                if task.story_level:
                    message["story_id"] = story.id

                message_group_id = f"{story.id}"
                sequence_prefix = "1" if task.task_type == "transcription" else "2"
                deduplication_id = f"{sequence_prefix}_{job_id}"
                
                response = self.sqs.send_message(
                    QueueUrl=self.queue_url,
                    MessageBody=json.dumps(message),
                    MessageGroupId=message_group_id, 
                    MessageDeduplicationId=deduplication_id
                )
                task_ids[task.task_type] = response["MessageId"]
                logger.info(
                    f"Successfully queued task {task.task_type} for story {story.id}"
                )
            return {"success": True, "task_ids": task_ids}
        
        except Exception as e:
            error_msg = (
                f"Failed to add tasks to SQS queue for story {story.id}: {str(e)}"
            )
            logger.error(error_msg)
            return {"success": False, "error": error_msg}


class SimpleQueueStrategy(QueueStrategy):
    """Simple in-memory queue strategy for testing purposes."""

    def add_to_queue(self, tasks: List[MLTask], story: Story) -> Dict:
        """
        Simulate adding tasks to a queue.

        Args:
            tasks: List of MLTask objects to be queued
            story: Story object associated with the tasks

        Returns:
            Dict containing success status and task IDs
        """
        task_ids = {}
        try:
            for task in tasks:
                task_ids[task.task_type] = f"{story.id}_{task.task_type}"
                logger.debug(
                    f"Added task {task.task_type} to simple queue for story {story.id}"
                )
            return {"success": True, "task_ids": task_ids}
        except Exception as e:
            error_msg = (
                f"Failed to add tasks to simple queue for story {story.id}: {str(e)}"
            )
            logger.error(error_msg)
            return {"success": False, "error": error_msg}


class QueueProducer:
    """
    Manages the production of ML tasks to a queue system.

    Attributes:
        queue_strategy: Strategy object for queue implementation
        tasks: Dictionary of available ML tasks
    """

    def __init__(self, queue_strategy: QueueStrategy = SQSStrategy()):
        """
        Initialize QueueProducer with a queue strategy.

        Args:
            queue_strategy: Strategy object for queue implementation (defaults to SQS)
        """
        self.queue_strategy = queue_strategy
        self.tasks = {
            "transcription": MLTask("transcription"),
            "summarization": MLTask("summarization"),
            "tag": MLTask("tag")
        }
        logger.info(
            "QueueProducer initialized with %s", queue_strategy.__class__.__name__
        )

    def enable_task(self, task_type: str) -> None:
        """Enable a specific task type."""
        if task_type in self.tasks:
            self.tasks[task_type].enabled = True
            logger.info(f"Enabled task type: {task_type}")
        else:
            logger.warning(f"Attempted to enable unknown task type: {task_type}")

    def disable_task(self, task_type: str) -> None:
        """Disable a specific task type."""
        if task_type in self.tasks:
            self.tasks[task_type].enabled = False
            logger.info(f"Disabled task type: {task_type}")
        else:
            logger.warning(f"Attempted to disable unknown task type: {task_type}")

    def get_enabled_tasks(self) -> List[MLTask]:
        """Return list of currently enabled tasks."""
        return [task for task in self.tasks.values() if task.enabled]

    def _create_queue_entries(
        self, enabled_tasks: List[MLTask], story: Story
    ) -> List[MLProcessingQueue]:
        """
        Create database entries for queued tasks.

        Args:
            enabled_tasks: List of enabled MLTask objects
            story: Story object associated with the tasks

        Returns:
            List of created MLProcessingQueue objects

        Raises:
            Exception: If database operation fails
        """
        try:
            entries = []
            for task in enabled_tasks:
                entries.append(
                    MLProcessingQueue(
                        story=story if task.story_level else None,
                        project=story.proj,
                        task_type=task.task_type,
                        status="initialized",
                        timestamp=datetime.now(UTC),
                    )
                )
            return MLProcessingQueue.objects.bulk_create(entries)
        except Exception as e:
            logger.error(
                f"Failed to create queue entries for story {story.id}: {str(e)}"
            )
            raise

    def add_to_queue(self, story: Story) -> Dict:
        """
        Process a story by creating queue entries and adding tasks to queue.

        Args:
            story: Story object to be processed

        Returns:
            Dict containing success status and additional information
        """
        try:
            #TODO: this is to disable tasks if the story has no audio or text content
            #audio_content may not be none but its could be null
            if not story.audio_content:
                logger.warning(f"Story {story.id} has no audio content")
                self.disable_task("transcription")
                if not story.text_content or story.text_content == "":
                    logger.warning(f"Story {story.id} has no text content")
                    return {"success": False, "error": "Story has no audio or text content"}

            with transaction.atomic():
                enabled_tasks = self.get_enabled_tasks()
                if not enabled_tasks:
                    logger.warning("No enabled tasks found for processing")
                    return {"success": False, "error": "No enabled tasks"}

                self._create_queue_entries(enabled_tasks, story)
                result = self.queue_strategy.add_to_queue(enabled_tasks, story)

                if result["success"]:
                    logger.info(
                        f"Successfully processed story {story.id} with {len(enabled_tasks)} tasks"
                    )
                return result

        except Exception as e:
            error_msg = f"Failed to process story {story.id}: {str(e)}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}
