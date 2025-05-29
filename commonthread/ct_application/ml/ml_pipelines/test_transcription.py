# test_transcription.py
from transcribing_pipeline import (
    DeepgramTranscribingStrategy,
    AudioInput,
)

# def test_hf_transcription():
#     # Initialize the HuggingFace transcription strategy
#     transcriber = HFTranscribingStrategy()  # Uses default "openai/whisper-base" model

#     try:
#         audio_file_path = "./audio.mp4"
#         audio_input = AudioInput(audio_file=audio_file_path)

#         print("\nStarting HuggingFace Transcription...")
#         print("-" * 50)
#         transcribed_text = transcriber.transcribe(audio_input)
#         print("Transcription Result:")
#         print(transcribed_text)
#         print("-" * 50)

#     except Exception as e:
#         print(f"An error occurred with HF transcription: {str(e)}")


def test_deepgram_transcription():
    # Initialize the Deepgram transcription strategy
    transcriber = DeepgramTranscribingStrategy()

    try:
        # For local file:
        audio_file_path = "./audio.mp4"
        audio_input = AudioInput(audio_file=audio_file_path)

        # For presigned URL (uncomment to test):
        # presigned_url = "your_presigned_url_here"
        # audio_input = AudioInput(presigned_url=presigned_url)

        print("\nStarting Deepgram Transcription...")
        print("-" * 50)
        transcribed_text = transcriber.transcribe(audio_input)
        print("Transcription Result:")
        print(transcribed_text)
        print("-" * 50)

    except Exception as e:
        print(f"An error occurred with Deepgram transcription: {str(e)}")


def main():
    # Test both transcription strategies
    # test_hf_transcription()
    test_deepgram_transcription()


if __name__ == "__main__":
    main()
