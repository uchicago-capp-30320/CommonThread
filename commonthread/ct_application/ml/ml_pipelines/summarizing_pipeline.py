from abc import ABC, abstractmethod
from typing import List
from transformers import pipeline
import requests
import os

PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API")


class SummarizingStrategy(ABC):
    """Protocol defining the interface for summarizing implementations"""

    @abstractmethod
    def summarize_text(self, text: str) -> str:
        pass

    @abstractmethod
    def summarize_multiple(self, texts: List[str]) -> List[str]:
        pass


class LocalSummarizingStrategy(SummarizingStrategy):
    def __init__(
        self, model_name="sshleifer/distilbart-cnn-12-6", min_ratio=0.2, max_ratio=0.6
    ):
        self.summarizer = pipeline(
            "summarization", model=model_name, tokenizer=model_name
        )
        self.tokenizer = self.summarizer.tokenizer
        self.min_ratio = min_ratio
        self.max_ratio = max_ratio

    def summarize_text(self, text: str) -> str:
        try:
            tokens = self.tokenizer.encode(
                text, truncation=True, max_length=1024, return_tensors="pt"
            )
            decoded_input = self.tokenizer.decode(tokens[0], skip_special_tokens=True)

            input_tokens = len(tokens[0])
            min_length = max(20, int(input_tokens * self.min_ratio))
            max_length = max(min_length + 20, int(input_tokens * self.max_ratio))

            summary = self.summarizer(
                decoded_input,
                max_length=max_length,
                min_length=min_length,
                do_sample=False,
                no_repeat_ngram_size=3,
                length_penalty=1.2,
                num_beams=4,
            )
            return summary[0]["summary_text"]
        except Exception as e:
            print(f"Error summarizing text: {e}")
            return ""

    # TODO remove if never used, because the signature is different
    def summarize_multiple(self, texts: List[str]) -> List[str]:
        return [self.summarize_text(text) for text in texts]


class CollectiveSummarizingStrategy(SummarizingStrategy):
    def __init__(self, api_key: str = PERPLEXITY_API_KEY, model: str = "sonar-pro"):
        """
        :param api_key: Perplexity API key
        :param model: Name of the model to use (e.g., sonar-small-online, gpt-4, etc.)
        """
        self.api_key = api_key
        self.model = model
        self.api_url = "https://api.perplexity.ai/chat/completions"

    def summarize_text(self, text: str) -> str:
        # Not implemented for collective summarizer as it's meant for multiple texts
        raise NotImplementedError(
            "CollectiveSummarizingStrategy is meant for summarizing multiple texts"
        )

    def summarize_multiple(self, texts: List[str]) -> str:
        combined_input = "\n\n".join(
            [f"Story {i+1}: {text}" for i, text in enumerate(texts)]
        )

        prompt = (
            "Below is a collection of story summaries. Analyze them and provide a concise overview "
            "of common themes, patterns, and insights that emerge across the stories. "
            "Limit your response to 3-5 bullet points, each under 20 words.\n\n"
            f"{combined_input}"
        )

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        data = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.5,
        }

        response = requests.post(self.api_url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
