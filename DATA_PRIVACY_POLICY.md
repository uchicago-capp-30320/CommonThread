# CommonThread Privacy Policy 

## What information does CommonThread have from me?
To provide quality service and manage access, CommonThread stores data related to your user profile. This includes the name, email, and password you provide when creating an account. In addition, CommonThread manages the data related to the organizations, projects and stories that you create, including all text, images, and audio materials that you upload. 

To secure your information and authenticate that only you can login and see the stories you have uploaded, CommonThread uses authentication cookies that are unique to you and are only used within the CommonThread  website. 

## What information does CommonThread not have from me?
CommonThread does not track your activities in other websites or parts of the internet (tracking cookies) nor it handles any financial information.


## How long will CommonThread have my information?
CommonThread will store your data until you decide to delete it or the organization shuts down its operations. If the latter happens, CommonThread will notify you so you can obtain a personal copy of your data. 

## How does CommonThread handle my information? 

- User, project, and story data and metadata are stored in a remote server only accessible to the CommonThread IT team. 
- Audiovisual media (images and audio) is stored using cloud storage provided by AWS. 
- CommonThread uses an ensemble of AI/ML methodologies to enable the generation of story and project level summaries as well as audio transcription.
    - Story-Level summarization is performed locally using Hugging Face’s distilbart-cnn-12-6 model, with no data ever departing our servers
    - Project-Level insight generation is performed using Perplexity AI’s Sonar model via their public api. This requires sending story summaries to Perplexity’s servers. 
    - Tagging service uses a locally hosted natural language processing model (dslim/bert-base-NER) from Hugging Face’s Transformers library. All tagging operations are performed on our own servers, and no data is sent to third-party services for this purpose. This ensures that user-submitted content remains private and secure during processing.
    - For transcription, CommonThread uses Deepgram. Deepgram API operates under Regulation (EU) 2016/679 (the “EU GDPR“) or, where applicable, the “UK GDPR” as defined in the UK Data Protection Act (collectively “GDPR”).  The API does not store any data in the long term but store it for the short time when the transcription is running on their cloud service. They do not share or sell nor see your data. 


## Who has access to your information? 

The CommonThread IT team has access to all data strictly for technical support purposes. Besides them, only you and the people in the organizations you are part of can see your user data.

## What if you don’t want CommonThread to have your data? 
You can always delete any information you have uploaded to CommonThread, including your account, user data, organizations, projects, and individual stories. 

## What happens if your data is breached? 
Despite all security measures, the internet is a contentious place filled with malicious actors that want to access private information, which means that data breaches are always a risk. If CommonThread were to fall victim of a data breach and your data ends up being exposed, CommonThread will let you know of the incident and the information that was exposed. 
