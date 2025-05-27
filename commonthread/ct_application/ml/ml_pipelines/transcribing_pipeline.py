from typing import Union, BinaryIO, Optional
from transformers import pipeline
from abc import ABC, abstractmethod
from deepgram import DeepgramClient, PrerecordedOptions
import os

DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")


# this is an encapsulated class for audio file or presigned url
class AudioInput:
    def __init__(
        self,
        audio_file: Optional[Union[str, BinaryIO]] = None,
        presigned_url: Optional[str] = None,
    ):
        if not audio_file and not presigned_url:
            raise ValueError("Either audio_file or presigned_url must be provided")
        self.audio_file = audio_file
        self.presigned_url = presigned_url

    @property
    def is_presigned(self) -> bool:
        return self.presigned_url is not None


class TranscribingStrategy(ABC):

    @abstractmethod
    def transcribe(self, audio_input: AudioInput) -> str:
        pass


class HFTranscribingStrategy(TranscribingStrategy):
    def __init__(self, model_name: str = "openai/whisper-base"):
        self.transcriber = pipeline(
            "automatic-speech-recognition",
            model=model_name,
            chunk_length_s=30,
            stride_length_s=5,
        )

    def transcribe(self, audio_input: AudioInput) -> str:
        if audio_input.is_presigned:
            raise ValueError("HuggingFace strategy does not support presigned URLs")

        result = self.transcriber(audio_input.audio_file)
        return result["text"]


class DeepgramTranscribingStrategy(TranscribingStrategy):
    def __init__(self):
        if not DEEPGRAM_API_KEY:
            raise ValueError("DEEPGRAM_API_KEY environment variable is not set")
        self.deepgram = DeepgramClient(DEEPGRAM_API_KEY)

    def transcribe(self, audio_input: AudioInput) -> str:
        options = PrerecordedOptions(
            smart_format=True,
            paragraphs=True,
            model="nova-3",
        )

        if audio_input.is_presigned:
            source = {"url": audio_input.presigned_url}
            response = self.deepgram.listen.rest.v("1").transcribe_url(source, options)
        else:
            if hasattr(audio_input.audio_file, "read"):
                buffer_data = audio_input.audio_file.read()
                payload = {
                    "buffer": buffer_data,
                }
                response = self.deepgram.listen.rest.v("1").transcribe_file(
                    payload, options
                )
            else:
                with open(audio_input.audio_file, "rb") as file:
                    buffer_data = file.read()
                payload = {
                    "buffer": buffer_data,
                }
                response = self.deepgram.listen.rest.v("1").transcribe_file(
                    payload, options
                )

        return response.results.channels[0].alternatives[0].transcript
