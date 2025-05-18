from typing import Union, BinaryIO, Optional
from transformers import pipeline
from abc import ABC, abstractmethod
from deepgram import Deepgram
import os

class AudioInput:
    """Class to encapsulate different types of audio inputs"""
    def __init__(
        self, 
        audio_file: Optional[Union[str, BinaryIO]] = None,
        presigned_url: Optional[str] = None
    ):
        if not audio_file and not presigned_url:
            raise ValueError("Either audio_file or presigned_url must be provided")
        self.audio_file = audio_file
        self.presigned_url = presigned_url

    @property
    def is_presigned(self) -> bool:
        return self.presigned_url is not None

class TranscribingStrategy(ABC):
    """Abstract base class for transcription strategies."""
    
    @abstractmethod
    def transcribe(self, audio_input: AudioInput) -> str:
        pass 

class HFTranscribingStrategy(TranscribingStrategy):
    def __init__(self, model_name: str = "openai/whisper-base"):
        self.transcriber = pipeline("automatic-speech-recognition",
                                  model=model_name,
                                  chunk_length_s=30,
                                  stride_length_s=5)

    def transcribe(self, audio_input: AudioInput) -> str:
        if audio_input.is_presigned:
            raise ValueError("HuggingFace strategy does not support presigned URLs")
        
        result = self.transcriber(audio_input.audio_file)
        return result["text"]

class DeepgramTranscribingStrategy(TranscribingStrategy):
    def __init__(self):
        api_key = os.environ["DEEPGRAM_API_KEY"]
        self.deepgram = Deepgram(api_key)

    def transcribe(self, audio_input: AudioInput) -> str:
        options = {
            "smart_format": True,
            "model": "nova-3",
        }

        if audio_input.is_presigned:
            source = {"url": audio_input.presigned_url}
        else:
            # Handle direct audio file input
            if hasattr(audio_input.audio_file, 'read'):
                source = {"buffer": audio_input.audio_file, "mimetype": 'audio/mp3'}
            else:
                source = {"url": audio_input.audio_file}

        result = self.deepgram.transcription.sync_prerecorded(source, options)
        return result['results']['channels'][0]['alternatives'][0]['transcript']