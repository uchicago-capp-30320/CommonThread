![RepoName](https://img.shields.io/badge/CommonThread-8A2BE2)
![Stars](https://img.shields.io/github/stars/uchicago-capp-30320/CommonThread?&color=yellow)
![Files](https://img.shields.io/github/directory-file-count/uchicago-capp-30320/CommonThread) 

![CommonThread Banner with a logo of four hands forming a ball of yarn](CommonThread_Banner.png)

--------------

CommonThread is an open-source collaborative tool that enables users to turn stories into insights. Community-based organizations, journalists, researchers, and community members alike can use the tool to efficiently gather stories, aggregate them, and understand common threads to draw insights for action.

## Set Up :hammer:

To set up a local development environment, follow these steps:

1. **Install UV**: If you haven't already, install UV
2. **Sync the Environment**: After installing UV, you need to sync the environment. This will set up the necessary configurations and dependencies for your project. Run the following command:
```bash
uv sync
```
3. **To add a new package**: If you need to add a new package, you can do so by running:
```bash
uv add <package_name>
``` 

## Settin Up Your .env and SECRET_KEY :key:
1. **See the .env.example file**: The `.env.example` file contains a template for the environment variables you need to set up. 
2. **Copy this file and rename it to `.env`**: This will be your actual environment file where you will set your variables. You can do this by running:
```bash
cp .env.example .env
```
3. **Set the SECRET_KEY**: Open the `.env` file and set the `SECRET_KEY` variable. This key is sent to you privately.


## Project Structure :card_index_dividers:

```bash
CommonThread
├── commonthread    # Backend folder 
│   ├── commonthread       
│   ├── auth      
│   ├── public    
│   ├── ct_application      
│   │   ├── auth      
│   │   ├── public    
│   │   ├── org
│   │   │   ├── migrations
│   │   │   ├── static
│   │   │   └── templates
│   │   ├── preprocessor
│   │   ├── ml
│   │   ├── db
│   ├── tests
│   └── run  
└── frontend
    ├── public
    ├── org
    │   ├── migrations
    │   ├── static
    │   └── templates
    ├── shared
    └── assets
```

![Repo structure](diagram.svg)

## Issue Tracker :mag:
Check our [issue tracker](https://github.com/orgs/uchicago-capp-30320/projects/10/views/1).
