CustomUser

| Name              | Type                 | Description               |
| ----------------- | -------------------- | ------------------------- |
| user_id              | PrimaryKey     | user's unique identifier|
| name       | varchar            | display name     |


UserLogin

| Name     | Type          | Description                 |
| -------- | ------------- | --------------------------- |
| user_id | OneToOne (ForeignKey) | links to `CustomUser`       |
| username | varchar  | login username (unique)     |
| password | varchar  | login password |


Organization

| Name              | Type                 | Description               |
| ----------------- | -------------------- | ------------------------- |
| org_id              | PrimaryKey     | organization's unique identifier |
| name       | varchar             | organization name     |


Project

| Name              | Type                 | Description               |
| ----------------- | -------------------- | ------------------------- |
| proj_id              | PrimaryKey     | project's unique identifier|
| org_id       | ForeignKey             | links to `Organization`       |
| name       | varchar             | project name     |
| curator       | ForeignKey             | links to `CustomUser`       |
| date | date | project created date   |


Story

| Name              | Type                 | Description               |
| ----------------- | -------------------- | ------------------------- |
| story_id              | PrimaryKey     | story's unique identifier |
| proj_id       | ForeignKey             | links to `Project`       |
| org_id       | ForeignKey             | links to `Organization`       |
| storyteller       | varchar             | storyteller's name      |
| curator       | ForeignKey             | links to `CustomUser`       |
| date | date | project created date   |
| content | text | story content  |
| ml_metadata | metadata | ml_metadata  |


Tag

| Name              | Type                 | Description               |
| ----------------- | -------------------- | ------------------------- |
| tag_id              | PrimaryKey     | tag unique identifier |
| name       | varchar             | tag name       |


StoryTag

| Name              | Type                 | Description               |
| ----------------- | -------------------- | ------------------------- |
| story_tag_id              | PrimaryKey    | story tag unique identifier |
| story_id              | ForeignKey     | links to `Story` |
| tag_id              | ForeignKey     | links to `Tag` |


ProjectTag

| Name              | Type                 | Description               |
| ----------------- | -------------------- | ------------------------- |
| proj_tag_id              | PrimaryKey    | project tag unique identifier |
| proj_id              | ForeignKey     | links to `Project` |
| tag_id              | ForeignKey     | links to `Tag` |


OrgUser

| Name              | Type                 | Description               |
| ----------------- | -------------------- | ------------------------- |
| org_user_id              | PrimaryKey    | project tag unique identifier |
| user_id              | ForeignKey     | links to `Organization` |
| org_id              | ForeignKey     | links to `User` |
| access       | varchar             | access level       |


ML_Story_Insights

| Name              | Type                 | Description               |
| ----------------- | -------------------- | ------------------------- |
| story_id              | OneToOne (ForeignKey) | links to `Story` |
| summary              | varchar     | ml generated summary of story |
| insight              | varchar     | ml generated insights of story |
| sentiments              | json     | ml generated sentiments of story |
| entities              | json     | ml generated entities of story |
| generated_tags              | json     | ml generated tags of story |
| translation              | varchar     | ml generated translation of story |
| model_configuration              | json     | ml model configuration of story |
