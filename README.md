![GitHub License](https://img.shields.io/github/license/uchicago-capp-30320/CommonThread?color=133335)
![Files](https://img.shields.io/github/directory-file-count/uchicago-capp-30320/CommonThread?color=%23d0fdb9) 
![GitHub Issues or Pull Requests](https://img.shields.io/github/issues-closed/uchicago-capp-30320/CommonThread?color=%2356bcb3)
![Contributors](https://img.shields.io/github/contributors/uchicago-capp-30320/CommonThread)

![CommonThread Banner with a logo of four hands forming a ball of yarn](CommonThread_Banner.png)

--------------

**CommonThread** is an open-source collaborative tool that enables users to turn stories into insights. Community-based organizations, journalists, researchers, and community members alike can use the tool to efficiently gather stories, aggregate them, and understand common threads to draw insights for action.


## Tech Stack :toolbox:
![GIT](https://img.shields.io/badge/GIT-E44C30?style=for-the-badge&logo=git&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)
![AWS](https://img.shields.io/badge/AWS-%23FF9900.svg?style=for-the-badge&logo=amazon-aws&logoColor=white)
![Python](https://img.shields.io/badge/Python-FFD43B?style=for-the-badge&logo=python&logoColor=blue)
![Django](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=green)
![JSON](https://img.shields.io/badge/json-5E5C5C?style=for-the-badge&logo=json&logoColor=white)
![JWT](https://img.shields.io/badge/JWT-black?style=for-the-badge&logo=JSON%20web%20tokens)
![npm](https://img.shields.io/badge/npm-CB3837?style=for-the-badge&logo=npm&logoColor=white)
![HTML](https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white)
![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white)
![JS](https://img.shields.io/badge/JavaScript-323330?style=for-the-badge&logo=javascript&logoColor=F7DF1E)
![Svelte](https://img.shields.io/badge/Svelte-4A4A55?style=for-the-badge&logo=svelte&logoColor=FF3E00)
![Bulma](https://img.shields.io/badge/Bulma-00D1B2?style=for-the-badge&logo=Bulma&logoColor=white)
![Pytest](https://img.shields.io/badge/pytest-%23ffffff.svg?style=for-the-badge&logo=pytest&logoColor=2f9fe3)
![GitHub Actions](https://img.shields.io/badge/github%20actions-%232671E5.svg?style=for-the-badge&logo=githubactions&logoColor=white)
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)

## Set Up 

### Backend :hammer:

To set up a local development environment, follow these steps:

1. **Install UV**: If you haven't already, install UV
2. **Sync the Environment**: After installing UV, you need to sync the environment. This will set up the necessary configurations and dependencies for your project. Run the following command:
```bash
$ uv sync
```
3. **To add a new package**: If you need to add a new package, you can do so by running:
```bash
$ uv add <package_name>
``` 

### Frontend :art:
You can find detailed directions to manage the frontend environment and launch the web server locally [here](https://github.com/uchicago-capp-30320/CommonThread/tree/main/frontend).

### Secrets :key:
To configure your `.env` and `SECRET_KEY`:
1. **See the .env.example file**: The `.env.example` file contains a template for the environment variables you need to set up. 
2. **Copy this file and rename it to `.env`**: This will be your actual environment file where you will set your variables. You can do this by running:
```bash
$ cp .env.example .env
```
3. **Set the SECRET_KEY**: Open the `.env` file and set the `SECRET_KEY` variable. This key is sent to you privately.


## Project Structure :card_index_dividers:

```bash
CommonThread
├── commonthread
│   ├── commonthread
│   │   └── __pycache__
│   └── ct_application
│       ├── __pycache__
│       ├── functions
│       ├── migrations
│       ├── static
│       ├── templates
│       └── tests
│           ├── backend
│           └── frontend
└── frontend
    ├── src
    │   ├── components
    │   │   └── story
    │   ├── lib
    │   │   ├── assets
    │   │   │   ├── illustrations
    │   │   │   └── logos
    │   │   └── components
    │   │       └── story
    │   └── routes
    │       ├── about
    │       ├── login
    │       ├── org
    │       │   └── [org_name]
    │       │       ├── [story_id]
    │       │       ├── dashboard
    │       │       └── org-admin
    │       ├── signup
    │       └── stories
    │           └── new
    └── static
```


## Issue Tracker :mag:
Check our [issue tracker](https://github.com/orgs/uchicago-capp-30320/projects/10/views/1).

## Team and credits :writing_hand:
This project was built under the supervision of [James Turk](https://github.com/jamesturk) for the [Software Engineering for Civic Tech](https://github.com/uchicago-capp-30320) course, part of the MS in Computational Analysis and Public Policy at the University of Chicago. The developer team (presented in alphabetical order) includes: 

Contributor      | Roles |
:------------:   | :-------------: |
Austin Steinhart | Front-End Lead and Architect
Fatima Irfan     | Data Engineering Lead and Back-end Engineer
Jacob Trout      | Back-end Engineer and ML Specialist 
Onur Büyükkalkan | Back-end Lead and Data Engineer
Paul Soltys      | Chief Architect and Data Engineer
Praveen Chandar  | ML Specialist, Back-end and Front-end Engineer
Regina I. Medina | QA Specialist, Back-end and Front-end Engineer

Branding resources and customized illustrations designed by [Pili Medina :cat2:](mailto:pilar.eunice.mr@gmail.com). 

--------------
