"""

This module has 2 main functions:

1. Update the database table (MLProcessingQueue) with 3 tasks, each being in pending state.
2. Build the task dictionary with story_id,project_id,org_id and the task_type.(story_id wont exist for project insight task)
currently thinking of each task (tag, summary, inisght) as a separate task.
"""



class MLProducerService:
    def __init__(self):
        pass

    def update_table(self, story: Story) -> None:
        pass

    def enqueue_tasks(self, story: Story) -> None:
        pass
