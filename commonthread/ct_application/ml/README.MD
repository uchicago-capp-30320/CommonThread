# CommonThread ML Server

Automated story processing with transcription, summarization, and tagging services.

## Services

- **Transcription**: Audio to text using Deepgram/Whisper
- **Summarization**: Story and project-level summaries  
- **Tagging**: Automatic keyword and entity extraction

## Running the ML Server

```bash
# Module notation
python -m ct_application.cloud.consumer_service

# Script notation
python ct_application/cloud/consumer_service.py
```

## Environment Variables

```bash
DEEPGRAM_API_KEY=your_deepgram_api_key
CT_BUCKET_STORY_AUDIO=your_s3_bucket_name
```

## Dependencies

```bash
uv sync  # Install all dependencies including ML packages
```

## Usage

ML services automatically process stories when uploaded:

1. Audio upload triggers transcription
2. Text content generates tags
3. Summaries created for stories and projects

## API

```bash
GET /api/ml/status/{story_id}  # Check processing status
```

## Testing

```bash
pytest ct_application/ml/
```
```