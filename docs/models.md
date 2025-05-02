The name and purpose of attributes, including types, relationships, and other constraints.
Brief explanations of any key concepts useful to provide context for the data model.

User

| Name              | Type                 | Description               |
| ----------------- | -------------------- | ------------------------- |
| user              | ForeignKey(User)     | the creator of this image |
| uploaded_at       | DateTime             | time uploaded (UTC)       |
| moderation_status | ModerationStatusEnum | PUBLIC, HIDDEN, REMOVED   |

UserLogin

| Name              | Type                 | Description               |
| ----------------- | -------------------- | ------------------------- |
| user              | ForeignKey(User)     | the creator of this image |
| uploaded_at       | DateTime             | time uploaded (UTC)       |
| moderation_status | ModerationStatusEnum | PUBLIC, HIDDEN, REMOVED   |

Organization

| Name              | Type                 | Description               |
| ----------------- | -------------------- | ------------------------- |
| user              | ForeignKey(User)     | the creator of this image |
| uploaded_at       | DateTime             | time uploaded (UTC)       |
| moderation_status | ModerationStatusEnum | PUBLIC, HIDDEN, REMOVED   |

Project

| Name              | Type                 | Description               |
| ----------------- | -------------------- | ------------------------- |
| user              | ForeignKey(User)     | the creator of this image |
| uploaded_at       | DateTime             | time uploaded (UTC)       |
| moderation_status | ModerationStatusEnum | PUBLIC, HIDDEN, REMOVED   |

Story

| Name              | Type                 | Description               |
| ----------------- | -------------------- | ------------------------- |
| user              | ForeignKey(User)     | the creator of this image |
| uploaded_at       | DateTime             | time uploaded (UTC)       |
| moderation_status | ModerationStatusEnum | PUBLIC, HIDDEN, REMOVED   |

Tag

| Name              | Type                 | Description               |
| ----------------- | -------------------- | ------------------------- |
| user              | ForeignKey(User)     | the creator of this image |
| uploaded_at       | DateTime             | time uploaded (UTC)       |
| moderation_status | ModerationStatusEnum | PUBLIC, HIDDEN, REMOVED   |

StoryTag

| Name              | Type                 | Description               |
| ----------------- | -------------------- | ------------------------- |
| user              | ForeignKey(User)     | the creator of this image |
| uploaded_at       | DateTime             | time uploaded (UTC)       |
| moderation_status | ModerationStatusEnum | PUBLIC, HIDDEN, REMOVED   |

ProjectTag

| Name              | Type                 | Description               |
| ----------------- | -------------------- | ------------------------- |
| user              | ForeignKey(User)     | the creator of this image |
| uploaded_at       | DateTime             | time uploaded (UTC)       |
| moderation_status | ModerationStatusEnum | PUBLIC, HIDDEN, REMOVED   |

OrgUser

| Name              | Type                 | Description               |
| ----------------- | -------------------- | ------------------------- |
| user              | ForeignKey(User)     | the creator of this image |
| uploaded_at       | DateTime             | time uploaded (UTC)       |
| moderation_status | ModerationStatusEnum | PUBLIC, HIDDEN, REMOVED   |