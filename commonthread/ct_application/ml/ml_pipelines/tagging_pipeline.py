from typing import List
from ..ml_services.tagging_service import TaggingStrategy
from transformers import pipeline


#example implementation of a tagging strategy
class MLTaggingStrategy(TaggingStrategy):
    def __init__(self, aggregation_strategy: str = "simple", 
                 model_name: str = "dslim/bert-base-NER",
                 tokenizer_name: str = "dslim/bert-base-NER"):
        
        ner = pipeline("ner", 
                       model=model_name, 
                       tokenizer=tokenizer_name,
                       aggregation_strategy=aggregation_strategy)
                       
        self.ner = ner

    def get_tags(self, story_text: str) -> List[str]:
        ner_results = self.ner(story_text)
        tags = [result['word'] for result in ner_results]
        return tags