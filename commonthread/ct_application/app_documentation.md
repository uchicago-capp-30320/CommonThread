## CommonThread Backend Documentation

### The Important Notes

Because the backend functions basically entirely as an API called upon by the Svelte frontend, we do not make use of templates or use views in the standard Django way. Instead, all of our endpoints only return data, with visuals dealt with entirely by the frontend. 

## views.py

This is the bulk of the application, covering all endpoints that the frontend can hit. 

## utils.py

Contains functions used in multiple places or that are not purely API calls, such as JWT token functions and error handling

### models.py

Secretly DatabaseSchema.py. This is where the database schemas are specified, and other components of the backend can call these models as objects. The migrations folder tracks updates to these schemas over time.

### cloud and ml folders

Contains the components necessary for the machine learning functionalities.

### tests folder

Contains pytest tests used to ensure code is functioning properly.


### Less Important Things

### apps.py, admin.py, static folder
apps.py has some basic configuration. admin.py and the static/templates folders are unused due to the nature of our project.



