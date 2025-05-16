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
    transcribing_service.process_story_transcription(story_id) #this pattern to be used for all services



    