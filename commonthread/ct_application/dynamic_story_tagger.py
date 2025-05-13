# dynamic_story_tagging.py

from transformers import pipeline

def main():
    print("Before creating pipeline")
    ner_pipeline = pipeline("ner", aggregation_strategy="simple",model="dbmdz/bert-large-cased-finetuned-conll03-english")
    print("After creating pipeline")

    print("hey")
    text = "Praveen and Jacob tried to solve the Machine Learning problem in their app, they are MSCAPP students of UChicago"

    entities = ner_pipeline(text)

    for entity in entities:
        print(f"Entity: {entity['word']}, Label: {entity['entity_group']}, Score: {entity['score']:.2f}")

if __name__ == "__main__":
    main()