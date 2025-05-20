from typing import List, Dict
from transformers import pipeline
from abc import ABC, abstractmethod


class TaggingStrategy(ABC):
    """Protocol defining the interface for tagging implementations"""

    # gets story text returns a dictionary of tag name,value pairs
    @abstractmethod
    def get_tags(self, story_text: str) -> List[Dict[str, str]]:
        pass


# example implementation of a tagging strategy
class HFTaggingStrategy(TaggingStrategy):
    def __init__(
        self,
        aggregation_strategy: str = "simple",
        model_name: str = "dslim/bert-base-NER",
        tokenizer_name: str = "dslim/bert-base-NER",
    ):

        ner = pipeline(
            "ner",
            model=model_name,
            tokenizer=tokenizer_name,
            aggregation_strategy=aggregation_strategy,
        )

        self.ner = ner

    def get_tags(self, story_text: str) -> List[Dict[str, str]]:
        ner_results = self.ner(story_text)
        tags = [{"word": r["word"], "label": r["entity_group"]} for r in ner_results]
        return tags
