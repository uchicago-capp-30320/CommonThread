from typing import List, Protocol
from django.db import transaction
from ct_application.models import Story, Tag, StoryTag

class TaggingStrategy(Protocol):
    """Protocol defining the interface for tagging implementations"""
    def get_tags(self, story_text: str) -> List[str]:
        pass

class TaggingService:
    def __init__(self, tagging_strategy: TaggingStrategy):

        self.tagging_strategy = tagging_strategy

    def _get_ml_tags_for_story(self, story_text: str) -> List[str]:

        return self.tagging_strategy.get_tags(story_text)

    @transaction.atomic
    def process_story_tags(self, story: Story) -> List[Tag]:
        
        suggested_tags = self._get_ml_tags_for_story(story.content)
        
        created_tags = []
        
        for tag_name in suggested_tags:
            
            tag, created = Tag.objects.get_or_create(
                name=tag_name,
                defaults={'created_by': 'ML_created'}
            )
            
            
            StoryTag.objects.get_or_create(
                story=story,
                tag=tag,
                defaults={'created_by': 'ML_created'}
            )
            
            created_tags.append(tag)
        
        return created_tags
