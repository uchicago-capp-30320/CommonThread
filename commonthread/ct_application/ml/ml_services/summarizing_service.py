from ct_application.models import Story, Project
from ..ml_pipelines.summarizing_pipeline import (
    LocalSummarizingStrategy,
    CollectiveSummarizingStrategy,
)
from typing import List
import logging

logger = logging.getLogger(__name__)


class SummarizingService:
    def __init__(self):
        self.local_strategy = LocalSummarizingStrategy()
        self.collective_strategy = CollectiveSummarizingStrategy()

    def get_or_generate_story_summaries(self, project_id: int) -> List[str]:
        summaries = []
        stories = Story.objects.filter(proj_id=project_id)

        for story in stories:
            if story.summary:
                summaries.append(story.summary)
            else:
                generated_summary = self.local_strategy.summarize_text(
                    story.text_content
                )
                story.summary = generated_summary
                story.save(update_fields=["summary"])
                summaries.append(generated_summary)

        return summaries

    def process_project_summary(self, project_id: int) -> bool:
        try:
            project = Project.objects.get(id=project_id)
            story_summaries = self.get_or_generate_story_summaries(project_id)

            if not story_summaries:
                logger.warning(f"No stories found for project {project_id}.")
                return False

            trend_summary = self.collective_strategy.summarize_multiple(story_summaries)
            project.insight = trend_summary
            project.save(update_fields=["insight_json"])
            return True

        except Project.DoesNotExist:
            logger.error(f"Project with ID {project_id} does not exist.")
            return False
        except Exception as e:
            logger.error(f"Error processing project summary: {e}", exc_info=True)
            return False
