"""

This module has 2 main functions:
1. Keep listening to the sqs queue
2  Process the message and update the database table (MLProcessingQueue) with the task status.
This module WILL have to query the DB to get the text contents based on the story_id or project_id in the sqs message.
"""
from ..ml.ml_services.summarizing_service import SummarizingService
from ..ml.ml_services.tagging_service import TaggingService
from ..ml.ml_services.transcribing_service import TranscribingService   
from ..ml.ml_services.insight_service import InsightService
from ..models import Story
from typing import List

#helper functions
def get_story_text(story_id: int) -> str:
    story = Story.objects.get(id=story_id)
    return story.text_content

def get_all_story_text(project_id: int) -> List[str]:
    stories = Story.objects.filter(proj_id=project_id)
    return [story.text_content for story in stories]

def get_story_audio(story_id: int) -> str:
    story = Story.objects.get(id=story_id)
    return story.audio_file


class MLWorkerService:
    def __init__(self):
        pass
    def process_messages(self):
        pass
    #helpers will make use of the tagging_service, summary_service, insight_service
    tagging_service = TaggingService()
    summary_service = SummarizingService()
    insight_service = InsightService()
    transcribing_service = TranscribingService()
    


    