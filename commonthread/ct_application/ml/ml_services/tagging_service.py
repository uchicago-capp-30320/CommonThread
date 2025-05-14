from typing import List, Protocol,Dict
from django.db import transaction
from ct_application.models import Story, Tag, StoryTag

class TaggingStrategy(Protocol):
    """Protocol defining the interface for tagging implementations"""
    #gets story text returns a dictionary of tag name,value pairs
    def get_tags(self, story_text: str) -> List[Dict[str, str]]:
        pass

class TaggingService:
    def __init__(self, tagging_strategy: TaggingStrategy):

        self.tagging_strategy = tagging_strategy

    def _get_ml_tags_for_story(self, story_text: str) -> List[Dict[str, str]]:

        return self.tagging_strategy.get_tags(story_text)

    @transaction.atomic
    def process_story_tags(self, story: Story) -> List[Tag]:
        
        suggested_tags = self._get_ml_tags_for_story(story.content)
        
        created_tags = []
        
        for tag_name,tag_value in suggested_tags:
            
            tag, created = Tag.objects.get_or_create(
                name=tag_name,
                value=tag_value,
                created_by = "ML_created"
            )
            
            
            StoryTag.objects.get_or_create(
                story=story,
                tag=tag
            )
            
            created_tags.append(tag)
        
        return created_tags
