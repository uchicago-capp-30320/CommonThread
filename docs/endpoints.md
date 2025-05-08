# API Endpoint Documentation

## Table of Contents

- [Users](#users)
  - POST /users/create
  - POST /users/log_in
  - GET /users/{user_id}
- [Organizations](#organizations)
  - POST /orgs/create
  - POST /orgs/add_user
  - GET /orgs/{org_id}
  - GET /orgs/{org_id}/admin
- [Projects](#projects)
  - POST /projects/create
  - GET /projects/{project_id}
- [Tags](#tags)
  - GET /tags
- [Stories](#stories)
  - POST /stories/create
  - GET /stories
  - GET /stories/{story_id}

---

## Users

### 1. POST /users/create

**Description:**  
Creates a new user account.

**Parameters:**  
- `display_name` (required) - User's display name  
- `username` (required) - User's email address  
- `password` (required) - User's password  

**Actions:**  
- Add new record to User table  
- Add new record to Login table  
- Send email confirmation  

**Response:**  
- User ID  
- Redirect to `/log_in` if successful  

**HTTP Status:** 201 Created

---

### 2. POST /users/log_in

**Description:**  
Authenticates a user and creates session tokens.

**Parameters:**  
- `username` (required) - User's email address  
- `password` (required) - User's password  

**Actions:**  
- Validate credentials in Login table  
- Create token for authentication  

**Response:**  
- Access and refresh tokens  

**HTTP Status:** 200 OK

---

### 3. GET /users/{user_id}

**Description:**  
Retrieves a user's profile information.

**Parameters:**  
- `user_id` (required) - User ID  
- `org_id` (optional) - Organization ID  
- `project_id` (optional) - Project ID  

**Actions:**  
- Gets a user from the User table  

**Response:**  
- A single User object  

**HTTP Status:** 201 Created

---

## Organizations

### 4. POST /orgs/create

**Description:**  
Creates a new organization.

**Parameters:**  
- `organization_name` (required) - Name of the organization  
- `access_token` (required) - Authentication token  

**Actions:**  
- Add new record for Org in Organizations table  

**Response:**  
- Organization ID  

**HTTP Status:** 201 Created

---

### 5. POST /orgs/add_user

**Description:**  
Adds users to an organization.

**Parameters:**  
- `organization_id` (required) - Organization ID  
- `valid_users` (required) - List of users to add  
- `user_permission` (optional) - Permission level for users  
- `access_token` (required) - Authentication token  

**Actions:**  
- Add new records for valid users in OrgUser table  

**Response:**  
- User ID  

**HTTP Status:** 201 Created

---

### 6. GET /orgs/{org_id}

**Description:**  
Retrieves organization dashboard data.

**Parameters:**  
- `org_id` (required) - Organization ID  
- `user_id` (required) - User ID  

**Actions:**  
- Queries the Projects table and the Stories table by User ID and Org ID  

**Response:**  
- List of Projects and Stories with tags  

**Note:** This endpoint is still TBD.

---

### 7. GET /orgs/{org_id}/admin

**Description:**  
Retrieves organization administration data.

**Parameters:**  
- `org_id` (required) - Organization ID  

**Actions:**  
- Query the Users table  
- Update permission status  

**Response:**  
- Data frame with UserIDs and Authorization Levels

---

## Projects

### 8. POST /projects/create

**Description:**  
Creates a new project.

**Parameters:**  
- `org_id` (required) - Organization ID  
- `project_name` (required) - Project name  
- `creator` (required) - User creating the project  
- `necessary_fields_story_tags` (required) - Required tags for stories  
- `optional_fields_story_tags` (optional) - Optional tags for stories  
- `session_token` (required) - Authentication token  

**Actions:**  
- Add a new record for the project in the Project table  
- Add new records for tags in the Tag table  
- Add new records to the ProjectTag table  

**Response:**  
- Project ID  

**HTTP Status:** 201 Created

---

### 9. GET /projects/{project_id}

**Description:**  
Retrieves project dashboard data.

**Parameters:**  
- `project_id` (required) - Project ID  

**Actions:**  
- Get project table data  

**Response:**  
- TBD

---

## Tags

### 10. GET /tags

**Description:**  
Retrieves tags associated with a project.

**Parameters:**  
- `project_id` (required) - Project ID  

**Response:**  
- All required and optional tags  

**Notes:**  
Used to populate the frontend form.

---

## Stories

### 11. POST /stories/create

**Description:**  
Creates a new story entry.

**Parameters:**  
- `content` (required) - Story content  
- `curator` (required) - User creating the entry  
- `storyteller` (required) - Person telling the story  
- `date` (required) - Date of the story  
- `required_fields` (required) - Required tag fields  
- `optional_fields` (optional) - Optional tag fields  

**Actions:**  
- Add a new record to the Story table  
- Add new records to the StoryTag table  

**Response:**  
- Story ID  

**HTTP Status:** 201 Created

---

### 12. GET /stories

**Description:**  
Retrieves a list of stories.

**Parameters:**  
- `org_id` (required) - Organization ID  
- `project_id` (optional) - Project ID  

**Actions:**  
- Query the Story table and the StoryTag table  

**Response:**  
- List of stories with specific details  

**HTTP Status:** 201 Created

---

### 13. GET /stories/{story_id}

**Description:**  
Retrieves a single story.

**Parameters:**  
- `story_id` (required) - Story ID  

**Actions:**  
- Query the Story table and related StoryTag records  

**Response:**  
- A single story object  

**HTTP Status:** 201 Created
