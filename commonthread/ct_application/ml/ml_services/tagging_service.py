from typing import List, Dict, Optional
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from ct_application.models import Story, Tag, StoryTag
from ..ml_pipelines.tagging_pipeline import HFTaggingStrategy, TaggingStrategy
import logging

logger = logging.getLogger(__name__)


def get_story_text(story_id: int) -> Optional[str]:
    try:
        story = Story.objects.get(id=story_id)
        return story.text_content
    except ObjectDoesNotExist:
        logger.error(f"Story with id {story_id} not found")
        return None


class TaggingService:
    def __init__(self, tagging_strategy: TaggingStrategy = HFTaggingStrategy()):

        self.tagging_strategy = tagging_strategy

    def _get_ml_tags_for_story(self, story_text: str) -> List[Dict[str, str]]:

        return self.tagging_strategy.get_tags(story_text)

    @transaction.atomic
    def process_story_tags(self, story_id: int) -> bool:

        story_text = get_story_text(story_id)
        if story_text is None:
            logger.error(f"Story with id {story_id} has no text content")
            return False
        try:
            suggested_tags = self._get_ml_tags_for_story(story_text)

            created_tags = []

            for tag in suggested_tags:
                tag_name = tag["label"]
                tag_value = tag["word"]

                tag, _ = Tag.objects.get_or_create(
                    name=tag_name, value=tag_value, created_by="computer",required=False
                )

                story = Story.objects.get(id=story_id)
                StoryTag.objects.get_or_create(story=story, tag=tag)

                created_tags.append(tag)
            logger.info(f"Created {len(created_tags)} tags for story {story_id}")
            return True

        except Exception as e:
            logger.error(f"Error processing tags for story {story_id}: {str(e)}")
            return False
