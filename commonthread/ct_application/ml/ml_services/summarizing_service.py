from transformers import pipeline
from typing import List
import requests
from django.conf import settings
import os
from ct_application.models import Story, Project

PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API")

class LocalSummarizer:
    def __init__(self, model_name="sshleifer/distilbart-cnn-12-6", min_ratio=0.2, max_ratio=0.6):
        self.summarizer = pipeline("summarization", model=model_name, tokenizer=model_name)
        self.tokenizer = self.summarizer.tokenizer
        self.min_ratio = min_ratio
        self.max_ratio = max_ratio

    def summarize_story(self, story: str) -> str:
        try:
            tokens = self.tokenizer.encode(story, truncation=True, max_length=1024, return_tensors="pt")
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
            return summary[0]['summary_text']
        except Exception as e:
            print(f"Error summarizing story: {e}")
            return ""

    def summarize_all(self, stories: List[str]) -> List[str]:
        return [self.summarize_story(story) for story in stories]

class CollectiveSummarizer:
    def __init__(self, api_key: str, model: str = "sonar-pro"):
        """
        :param api_key: Perplexity API key
        :param model: Name of the model to use (e.g., sonar-small-online, gpt-4, etc.)
        """
        self.api_key = api_key
        self.model = model
        self.api_url = "https://api.perplexity.ai/chat/completions" 

    def summarize_trends(self, summarized_stories: List[str]) -> str:
        """
        Summarizes collective themes and trends from a list of summarized stories.

        :param summarized_stories: A list of summarized story strings
        :return: A string summary of collective insights and themes
        """
        combined_input = "\n\n".join(
            [f"Story {i+1}: {summary}" for i, summary in enumerate(summarized_stories)]
        )

        prompt = (
            "Below is a collection of story summaries. Analyze them and provide a concise overview "
            "of common themes, patterns, and insights that emerge across the stories. "
            "Limit your response to 3-5 bullet points, each under 20 words.\n\n"
            f"{combined_input}"
        )

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        data = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.5
        }

        response = requests.post(self.api_url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    
class ProjectSummarizer:
    def __init__(self, story_summarizer, trend_summarizer):
        """
        :param story_summarizer: An instance of LocalSummarizer
        :param trend_summarizer: An instance of CollectiveSummarizer
        """
        self.story_summarizer = story_summarizer
        self.trend_summarizer = trend_summarizer
        self.perplexity_api_key = settings.PERPLEXITY_API_KEY 

    def get_project_id_from_story(self, story_id: int) -> int:
        try:
            story = Story.objects.get(id=story_id)
            return story.proj_id
        except Story.DoesNotExist:
            print(f"No story found with ID {story_id}")
            return None

    def get_or_generate_story_summaries(self, project_id: int) -> List[str]:
        summaries = []
        stories = Story.objects.filter(proj_id=project_id)

        for story in stories:
            if story.summary:
                summaries.append(story.summary)
            else:
                generated_summary = self.story_summarizer.summarize_story(story.text_content)
                story.summary = generated_summary
                story.save(update_fields=["summary"])
                summaries.append(generated_summary)

        return summaries

    def summarize_project_trends(self, project_id: int) -> str:
        try:
            project = Project.objects.get(id=project_id)
            story_summaries = self.get_or_generate_story_summaries(project_id)

            if not story_summaries:
                print(f"No stories found for project {project_id}.")
                return ""

            trend_summary = self.trend_summarizer.summarize_trends(story_summaries)
            project.insight = trend_summary
            project.save(update_fields=["insight"])

            return trend_summary

        except Project.DoesNotExist:
            print(f"Project with ID {project_id} does not exist.")
            return ""
        except Exception as e:
            print(f"Error summarizing project trends: {e}")
            return ""


