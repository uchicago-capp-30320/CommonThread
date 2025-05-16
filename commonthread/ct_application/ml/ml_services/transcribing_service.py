from typing import Union, BinaryIO  
from ..ml_pipelines.transcribing_pipeline import HFTranscribingStrategy, TranscribingStrategy
from ct_application.models import Story
from commonthread.settings import CT_BUCKET_STORY_AUDIO
import boto3

def get_story_audio(story_id: int) -> BinaryIO:

    story = Story.objects.get(id=story_id)
    s3_client = boto3.client('s3')
    bucket_name = CT_BUCKET_STORY_AUDIO  
    file_key = story.audio_file
    
    response = s3_client.get_object(Bucket=bucket_name, Key=file_key)
    return response['Body']

class TranscribingService:
    def __init__(self, transcribing_strategy: TranscribingStrategy=HFTranscribingStrategy()):
        self.transcribing_strategy = transcribing_strategy

    def _get_transcribed_text(self, story_id: int) -> str:
        audio_file = get_story_audio(story_id)
        return self.transcribing_strategy.transcribe(audio_file)

    def process_story_transcription(self, story_id: int) -> bool:
        transcribed_text = self._get_transcribed_text(story_id)
        story = Story.objects.get(id=story_id)
        story.transcription = transcribed_text
        story.save()
        return True
