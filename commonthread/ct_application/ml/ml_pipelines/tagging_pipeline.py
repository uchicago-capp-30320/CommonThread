from typing import List
from ..ml_services.tagging_service import TaggingStrategy


#example implementation of a tagging strategy
class MLTaggingStrategy(TaggingStrategy):
    def __init__(self):

        pass

    def get_tags(self, story_text: str) -> List[str]:

        pass