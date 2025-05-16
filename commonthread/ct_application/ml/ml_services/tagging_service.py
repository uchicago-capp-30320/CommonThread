from typing import List,Dict
from django.db import transaction
from ct_application.models import Story, Tag, StoryTag
from ..ml_pipelines.tagging_pipeline import HFTaggingStrategy, TaggingStrategy



def get_story_text(story_id: int) -> str:
    story = Story.objects.get(id=story_id)
    return story.text_content


class TaggingService:
    def __init__(self, tagging_strategy: TaggingStrategy = HFTaggingStrategy()):

        self.tagging_strategy = tagging_strategy

    def _get_ml_tags_for_story(self, story_text: str) -> List[Dict[str, str]]:

        return self.tagging_strategy.get_tags(story_text)

    @transaction.atomic
    def process_story_tags(self, story_id: int) -> bool:
        
        story_text = get_story_text(story_id)
        suggested_tags = self._get_ml_tags_for_story(story_text)
        
        created_tags = []
        
        for tag in suggested_tags:
            tag_name = tag["word"]
            tag_value = tag["label"]
            
            tag, _ = Tag.objects.get_or_create(
                name=tag_name,
                value=tag_value,
                created_by = "ML_created"
            )
            
            story = Story.objects.get(id=story_id)
            StoryTag.objects.get_or_create(
                story=story,
                tag=tag
            )
            
            created_tags.append(tag)
        print(f"Created {len(created_tags)} tags for story {story_id}")
        return True
