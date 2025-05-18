import boto3
import json
from datetime import datetime, timezone
from django.conf import settings
from django.db import transaction
from typing import Dict, List
from abc import ABC, abstractmethod
from ct_application.models import Story, MLProcessingQueue
from commonthread.settings import CT_SQS_QUEUE_URL



class MLTask:
    def __init__(self, task_type: str, enabled: bool = True, story_level: bool = True):
        self.task_type = task_type
        self.enabled = enabled
        self.story_level = story_level

class QueueStrategy(ABC):
    @abstractmethod
    def add_to_queue(self, tasks: List[MLTask], story: Story) -> Dict:
        """
        Implement specific queueing logic for the tasks
        Returns: Dict with success status and task IDs
        """
        pass

class SQSStrategy(QueueStrategy):
    def __init__(self):
        self.sqs = boto3.client(
                            'sqs',
                            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                            region_name=settings.AWS_S3_REGION_NAME
                        )
        self.queue_url = CT_SQS_QUEUE_URL

    def add_to_queue(self, tasks: List[MLTask], story: Story) -> Dict:
        task_ids = {}
        
        for task in tasks:
            message = {
                'project_id': story.proj.id,
                'task_type': task.task_type,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
            if task.story_level:  
                message['story_id'] = story.id
            
            response = self.sqs.send_message(
                QueueUrl=self.queue_url,
                MessageBody=json.dumps(message)
            )
            task_ids[task.task_type] = response['MessageId']
            
        return {'success': True, 'task_ids': task_ids}

class SimpleQueueStrategy(QueueStrategy):
    def add_to_queue(self, tasks: List[MLTask], story: Story) -> Dict:
        task_ids = {}
        
        for task in tasks:
            task_ids[task.task_type] = f"{story.id}_{task.task_type}"
            
        return {'success': True, 'task_ids': task_ids}

class QueueProducer:
    def __init__(self, queue_strategy: QueueStrategy = SQSStrategy()):
        self.queue_strategy = queue_strategy
        self.tasks = {
            'tag': MLTask('tag'),
            'summary': MLTask('summary'),
            'transcription': MLTask('transcription'),
            'insight': MLTask('insight', story_level=False)
        }

    def enable_task(self, task_type: str):
        if task_type in self.tasks:
            self.tasks[task_type].enabled = True

    def disable_task(self, task_type: str):
        if task_type in self.tasks:
            self.tasks[task_type].enabled = False

    def get_enabled_tasks(self) -> List[MLTask]:
        return [task for task in self.tasks.values() if task.enabled]

    def _create_queue_entries(self, enabled_tasks: List[MLTask], story: Story) -> List[MLProcessingQueue]:
        entries = []
        for task in enabled_tasks:
            entries.append(
                MLProcessingQueue(
                    story=story if task.story_level else None,
                    project=story.proj,
                    task_type=task.task_type,
                    status='processing',
                    timestamp=datetime.now(timezone.utc)

                )
            )
        return MLProcessingQueue.objects.bulk_create(entries)

    def process_story(self, story: Story) -> Dict:
        try:
            with transaction.atomic():
                enabled_tasks = self.get_enabled_tasks()
                self._create_queue_entries(enabled_tasks, story)
                return self.queue_strategy.add_to_queue(enabled_tasks, story)

        except Exception as e:
            print(f"Failed to produce ML tasks for story {story.id}: {str(e)}")
            return {'success': False, 'error': str(e)}

 



