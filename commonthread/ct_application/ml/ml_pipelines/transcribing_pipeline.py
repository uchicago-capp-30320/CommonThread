from typing import Union, BinaryIO
from transformers import pipeline
from abc import ABC, abstractmethod



class TranscribingStrategy(ABC):
    """Abstract base class for transcription strategies."""
    
    @abstractmethod
    def transcribe(self, audio_input: Union[str, BinaryIO]) -> str:

        pass 

class HFTranscribingStrategy(TranscribingStrategy):
    def __init__(self, model_name: str = "openai/whisper-base"):

        self.transcriber = pipeline("automatic-speech-recognition",
                                  model=model_name,
                                  chunk_length_s=30,
                                  stride_length_s=5)

    def transcribe(self, audio_input: Union[str, BinaryIO]) -> str:

        result = self.transcriber(audio_input)
        return result["text"] 