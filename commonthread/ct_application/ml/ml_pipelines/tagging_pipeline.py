from typing import List
from ..ml_services.tagging_service import TaggingStrategy
from transformers import pipeline


#example implementation of a tagging strategy
class MLTaggingStrategy(TaggingStrategy):
    def __init__(self):
        ner = pipeline("ner", 
                       model="dslim/bert-base-NER", 
                       tokenizer="dslim/bert-base-NER",
                       aggregation_strategy="simple")
        self.ner = ner

    def get_tags(self, story_text: str) -> List[str]:
        ner_results = self.ner(story_text)
        tags = [result['word'] for result in ner_results]
        return tags