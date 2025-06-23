# test_tagging.py

from tagging_pipeline import HFTaggingStrategy


def test_tagging_pipeline():
    # Initialize the tagging strategy
    tagger = HFTaggingStrategy()

    # Test cases with different types of entities
    test_cases = [
        "John and Mary went to Microsoft headquarters in Seattle.",
        "Apple CEO Tim Cook announced new products at their California office.",
        "The World Health Organization reported new findings from their research in Geneva.",
        "President Biden met with Chancellor Scholz in Berlin yesterday.",
    ]

    # Process each test case and print results
    for i, text in enumerate(test_cases, 1):
        print(f"\nTest Case {i}:")
        print(f"Text: {text}")
        print("Tags:")
        tags = tagger.get_tags(text)
        for tag in tags:
            print(tag)
        print("-" * 50)


if __name__ == "__main__":
    print("Testing Tagging Pipeline...")
    try:
        test_tagging_pipeline()
        print("\nTesting completed successfully!")
    except Exception as e:
        print(f"\nAn error occurred: {str(e)}")
