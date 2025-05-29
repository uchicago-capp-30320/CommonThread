from typing import BinaryIO
import logging
from ..ml_pipelines.transcribing_pipeline import (
    TranscribingStrategy,
    DeepgramTranscribingStrategy,
    AudioInput,
)
from ct_application.models import Story
from commonthread.settings import CT_BUCKET_STORY_AUDIO
from ct_application.utils import generate_s3_presigned

logger = logging.getLogger(__name__)


def get_story_presigned_url(story_id: int) -> BinaryIO:
    story = Story.objects.get(id=story_id)
    bucket = CT_BUCKET_STORY_AUDIO
    key = str(story.audio_content)

    presigned = generate_s3_presigned(
        bucket_name=bucket, key=key, operation="download", expiration=300
    )
    return presigned["url"]


class TranscribingService:
    def __init__(
        self,
        transcribing_strategy: TranscribingStrategy = DeepgramTranscribingStrategy(),
    ):
        self.transcribing_strategy = transcribing_strategy

    def process_story_transcription(
        self, story_id: int, use_presigned: bool = True
    ) -> bool:
        """
        Fetch the story audio (either via presigned URL or temp file),
        run the ASR pipeline, and save the transcript back onto the Story.
        """
        try:
            audio_source = get_story_presigned_url(story_id)
            audio_input = AudioInput(presigned_url=audio_source)
            transcribed_text = self.transcribing_strategy.transcribe(audio_input)
            
            # Overwrite the Story.text_content with the transcription
            story = Story.objects.get(id=story_id)
            story.text_content = transcribed_text
            story.save(update_fields=["text_content"])
            logger.info(f"Saved transcription into text_content for story {story_id}")

        except Exception as e:
            logger.exception(f"Failed to process transcription for story {story_id},{str(e)}")
            return False
