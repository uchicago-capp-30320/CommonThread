### Conceptual Design

The Architecture of Common Thread is centered around the story- our base unit of data.

The story is a block of text or some recorded audio/video that is based on a prompt of some kind. Stories responding to the same or similar prompts are grouped together as projects, which are themselves grouped under organizations. Stories have tags, fields of additional information, attached to them with details like location, date, etc.

For users, this looks like this: A user creates (or joins) an organization, and then creates a project under which to collect stories. From there, they are either sharing story input forms with people or using the form themselves to enter stories. Having collected these stories, they can analyze them individually or in the project groups, for use in whatever means they are looking to use them.

### Nuts and Bolts

There are two main pieces of the architecture, with some smaller components that will be noted along the way.

1. **Svelte Frontend**

Svelte handles the visuals of displaying webpages, the forms and user input collection, and passing things such as login tokens to the user. It treats the backend as an API, sending requests and manipulating the data received as necessary for visualization on the front-end. It is also where we pass cookies/tokens to the user to enable login/authentication.

2. **Django Backend**

The Django Backend serves as the intermediary between user and data. This is where:
- Requests to store, get, or modify data are handled and pulled from/passed to the database
- Generates necessary tokens for login authetication & checks authentication when users try things
- More advanced analysis processes are run when requested

Note that as a result of our design, we are *not* using Django's views/templates default setup, but rather passing more API-style responses to the frontend.

**The PostgreSQL Database**

The Postgres database is a separate component but it's setup, design, and access are managed through the Django backend. This is done through the Models setup Django uses to set up databases for applications.

**The Login/Authentication system**

JWT Tokens manage the users and their access to their own data by passing information on which organizations users have access to, and to what level, in order to keep data private. These tokens are created on the backend, passed to and stored via the frontend, then reverified by the backend when users attempt to access certain pages.

**ML Task Scheduler**

There will be a processing trigger with a queue managed by the scheduler for ML-related analysis tasks, where the queue is implemented with the scheduler and a postgreSQL queue table. Designed to help manage tasks that might run slowly, particularly if users are specifically requesting them on the spot.

### Data Flow / Dependency

This is best described in two segments: The input and output.

For input, there is a straightforward heirarchy:

1. Users are created, information stored
2. Users create organizations (and add other users to them), information is stored.
3. Users create projects within an organization and define which tags they want to require/request for that group of stories, and that info is stored. Tags are characteristcs that might be useful or required for analysis: A location for mapping restaurant reviews, an age group for stories about children in school.
4. Users add stories to projects, where tags are assigned manually or automatically.
5. Stories and their associated tags are stored with reference to the project they are under.

--------------------------------------------------------------------------------

For output, there are many pages dealing with heirarchy of data organization or management, such as organization or project overview pages. These pages primarily draw in a straightforward manner from the database, filtering based on heirarchical association (user to org, org to project, project to story). 

Any processing or analysis will be based on stories & associated tags.

For Story-related output:

When simple data or analysis is requested:
1. The database is queried for a filtering of stories based on the organization or project they are under.
2. The tags associated with those stories are pulled, so that they can be used to sort, filter, search, and help analyze the stories.
3. The results are formatted and returned to the API request.

IE: A user wants how many stories from schoolchildren are from the high school, middle school, and elementary school respectively. The request is received from the frontend. The backend queries the database for the stories and their associated age group tag, with the Project these stories are in as the filter. The backend then formats the stories and tags appropriately and passes them to frontend, where the counts of each group within the age group tag are displayed.

For more advanced analysis, there is an additional step, which is that the results of queries to any ML API used will be stored within the database, and then requests will draw from the stored results.

