from typing import Union, BinaryIO, Optional
from ..ml_pipelines.transcribing_pipeline import (
    HFTranscribingStrategy, 
    TranscribingStrategy,
    DeepgramTranscribingStrategy,
    AudioInput
)
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
    def __init__(self, transcribing_strategy: TranscribingStrategy = HFTranscribingStrategy()):
        self.transcribing_strategy = transcribing_strategy

    def _get_transcribed_text(self, story_id: int, use_presigned: bool = False) -> str:
        if use_presigned:
            # Assume get_presigned_url is a helper function that exists
            presigned_url = get_presigned_url(story_id)
            audio_input = AudioInput(presigned_url=presigned_url)
        else:
            audio_file = get_story_audio(story_id)
            audio_input = AudioInput(audio_file=audio_file)
            
        return self.transcribing_strategy.transcribe(audio_input)

    def process_story_transcription(self, story_id: int, use_presigned: bool = False) -> bool:
        transcribed_text = self._get_transcribed_text(story_id, use_presigned)
        story = Story.objects.get(id=story_id)
        story.transcription = transcribed_text
        story.save()
        return True