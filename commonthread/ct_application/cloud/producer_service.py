import boto3
import json
import logging
from datetime import datetime
from django.conf import settings
from django.db import transaction
from typing import Dict, List
from abc import ABC, abstractmethod
from ct_application.models import Story, MLProcessingQueue


logger = logging.getLogger(__name__)

class MLTask:
    def __init__(self, task_type: str, enabled: bool = True, story_level: bool = True):
        self.task_type = task_type
        self.enabled = enabled
        self.story_level = story_level

# Abstract class for task producers
class QueueProducer(ABC):
    def __init__(self):
        self.tasks = {
            'tag': MLTask('tag'),
            'summary': MLTask('summary'),
            'insight': MLTask('insight', story_level=False) #insight is a project level task
        }

    def enable_task(self, task_type: str):
        if task_type in self.tasks:
            self.tasks[task_type].enabled = True

    def disable_task(self, task_type: str):
        if task_type in self.tasks:
            self.tasks[task_type].enabled = False

    def get_enabled_tasks(self) -> List[MLTask]:
        return [task for task in self.tasks.values() if task.enabled]

    @abstractmethod
    def add_to_queue(self, story: Story) -> Dict:  
        pass


class SQSQueueProducer(QueueProducer):
    def __init__(self):
        super().__init__()  
        self.sqs = boto3.client(
            'sqs',
            aws_access_key_id=settings.AWS_ACCESS_KEY,
            aws_secret_access_key=settings.AWS_SECRET_KEY,
            region_name=settings.AWS_REGION
        )
        self.queue_url = settings.SQS_QUEUE_URL

    def _create_queue_entries(self, story: Story) -> List[MLProcessingQueue]:
        entries = []
        
        for task in self.get_enabled_tasks():
            entries.append(
                MLProcessingQueue(
                    story=story if task.story_level else None,
                    project=story.proj,
                    task_type=task.task_type,
                    status='processing',
                    timestamp=datetime.now()
                )
            )
        
        return MLProcessingQueue.objects.bulk_create(entries)

    def add_to_queue(self, story: Story) -> Dict:
        try:
            with transaction.atomic():
                processing_tasks = self._create_queue_entries(story)
                task_ids = {}
                
                for task in processing_tasks:
                    message = {
                        'task_id': str(task.id),
                        'project_id': story.proj.id,
                        'task_type': task.task_type,
                        'timestamp': datetime.now().isoformat()
                    }
                    
                    if self.tasks[task.task_type].story_level:
                        message['story_id'] = story.id
                    
                    response = self.sqs.send_message(
                        QueueUrl=self.queue_url,
                        MessageBody=json.dumps(message)
                    )
                    task_ids[task.task_type] = response['MessageId']

                return {'success': True, 'task_ids': task_ids}

        except Exception as e:
            logger.error(f"Failed to produce ML tasks for story {story.id}: {str(e)}")
            return {'success': False, 'error': str(e)}

 
