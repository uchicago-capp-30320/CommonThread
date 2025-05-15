"""

This module has 2 main functions:
1. Keep listening to the sqs queue
2  Process the message and update the database table (MLProcessingQueue) with the task status.
This module WILL have to query the DB to get the text contents based on the story_id or project_id in the sqs message.
"""


class MLWorkerService:
    def __init__(self):
        pass
    def process_messages(self):
        pass
    #helpers will make use of the tagging_service, summary_service, insight_service