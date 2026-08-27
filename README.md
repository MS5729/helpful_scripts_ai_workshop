# Helpful Scripts for an AI Workshop

A progressive, runnable RAG starter kit. Begin with the no-AI scripts; add an OpenAI-compatible API and MongoDB Atlas for the later exercises.

Presenter guide: [40-minute AI workshop presenter script](docs/40_MINUTE_AI_WORKSHOP_PRESENTER_SCRIPT.md)

## Workshop progression

1. `scripts/01_parser_no_ai.py` - extract text and metadata from local files.
2. `scripts/02_chunker_no_ai.py` - split text into deterministic chunks.
3. `scripts/03_parser_agent.py` - optionally use an LLM to turn a document into structured records.
4. `scripts/04_chunker_agent.py` - optionally use an LLM to identify semantic sections before chunking.
5. `scripts/05_embedding_agent.py` - create embeddings with an OpenAI-compatible API.
6. `scripts/06_vector_store_mongodb_atlas.py` - write and search vectors in MongoDB Atlas.
7. `scripts/07_retrieval_agent.py` - retrieve relevant chunks with metadata filters.
8. `scripts/08_rag_pipeline.py` - complete retrieve-and-answer RAG flow with citations.

## Diagnosis and beginner utilities

These scripts make the workshop easier to teach and troubleshoot:

- `scripts/diagnosis/09_check_environment.py` - checks API access, Atlas connectivity, collection, and vector index without printing secrets.
- `scripts/diagnosis/10_inspect_vector_store.py` - shows counts, embedding dimensions, models, metadata, and safe text previews.
- `scripts/diagnosis/11_check_vector_search_health.py` - checks the Atlas index and can run a live vector-search query.
- `scripts/diagnosis/17_mock_rag_pipeline.py` - demonstrates parsing, chunking, retrieval, and source references without API keys or MongoDB.

Try the no-cloud demo first:

```powershell
.\\.venv\\Scripts\\python scripts/diagnosis/17_mock_rag_pipeline.py sample_data/guide.txt "What does this guide explain?"
```

After configuring `.env`, diagnose the cloud setup:

```powershell
.\\.venv\\Scripts\\python scripts/diagnosis/09_check_environment.py
.\\.venv\\Scripts\\python scripts/diagnosis/10_inspect_vector_store.py
.\\.venv\\Scripts\\python scripts/diagnosis/11_check_vector_search_health.py --query "What does this guide explain?"
```

Script 11 is the runtime check: script 09 checks the general environment, script 10 inspects stored data, and script 11 verifies that Atlas can actually serve vector search.

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
