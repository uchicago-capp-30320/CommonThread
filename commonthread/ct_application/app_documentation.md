## App Documentation

For now, the basics again:

### apps.py

A bit counterintuitive but this is more of a configuration file than an actual function holding file to the best of my understanding.

### models.py

This should really be called databaseschemas.py and is where they get collected

### admin.py

Related to models, but potentially more relevant for front-end. You can customize how a form is displayed in terms of order, grouping, etc. Looks like it might be particularly relevant for how we allow admin level users to create projects / story input forms.

## What is the Static Folder?

This is where all of our curated images would be stored.

For now, this might include:

- Website Aesthetic images (logos, fun pictures, etc)
- Data Visualization generated images (if static)

## What is the templates Folder?

It's where we store the webpage templates.

## views.py

Where we call the templates with the input from users that dictates what is displayed.