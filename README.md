# Helpful Scripts for an AI Workshop

A progressive, runnable RAG starter kit. Begin with the no-AI scripts; add an OpenAI-compatible API and MongoDB Atlas for the later exercises.

## Workshop progression

1. `scripts/01_parser_no_ai.py` - extract text and metadata from local files.
2. `scripts/02_chunker_no_ai.py` - split text into deterministic chunks.
3. `scripts/03_parser_agent.py` - optionally use an LLM to turn a document into structured records.
4. `scripts/04_chunker_agent.py` - optionally use an LLM to identify semantic sections before chunking.
5. `scripts/05_embedding_agent.py` - create embeddings with an OpenAI-compatible API.
6. `scripts/06_vector_store_mongodb_atlas.py` - write and search vectors in MongoDB Atlas.
7. `scripts/07_retrieval_agent.py` - retrieve relevant chunks with metadata filters.
8. `scripts/08_rag_pipeline.py` - complete retrieve-and-answer RAG flow with citations.

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

The first two scripts require no API keys or database. Use synthetic or non-sensitive workshop files in `sample_data/`.

For the AI scripts, configure `.env`:

```env
OPENAI_API_KEY=your-key
OPENAI_CHAT_MODEL=gpt-4o-mini
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
MONGODB_URI=mongodb+srv://...
MONGODB_DATABASE=ai_workshop_demo
MONGODB_VECTOR_COLLECTION=rag_chunks
MONGODB_VECTOR_INDEX=vector_index
```

Use a dedicated Atlas database for the workshop. Never commit `.env`, API keys, certificates, production documents, or personal data.

## Examples

```powershell
.\.venv\Scripts\python scripts\01_parser_no_ai.py sample_data/guide.txt
.\.venv\Scripts\python scripts\02_chunker_no_ai.py sample_data/guide.txt
.\.venv\Scripts\python scripts\06_vector_store_mongodb_atlas.py sample_data/guide.txt
.\.venv\Scripts\python scripts\08_rag_pipeline.py "What does this guide explain?"
```

Run script 06 once to ingest a file into Atlas, then run script 08 with a question.

Scripts write JSON to `workshop_output/`, which is ignored by Git. Run tests with `python -m pytest`.

## Atlas vector index

Create an Atlas Vector Search index named `vector_index` on `rag_chunks` with:

- Path: `embedding`
- Dimensions: `1536` for `text-embedding-3-small`
- Similarity: `cosine`

If you use another embedding model, update the dimensions and `.env` value together.
