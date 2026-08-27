# 40-Minute AI Workshop Presenter Script

## Workshop title

**Build Your First RAG Application: From Documents to Answers**

## Audience

This workshop assumes little or no software experience. The goal is not to memorize code. The goal is to understand the journey from a document to a useful answer.

## What attendees will learn

By the end, attendees should understand:

- What a RAG application is
- Why documents must be parsed and divided into chunks
- What embeddings and vector search do
- How MongoDB Atlas stores and finds document chunks
- How to run the scripts in this repository
- How to adapt the scripts to another project
- How to ask GitHub Copilot to help integrate the scripts safely

## Before people arrive

Have these ready:

- Python installed
- Git installed
- VS Code and GitHub Copilot
- This repository cloned locally
- A small, non-sensitive text, CSV, or PDF file
- Optional: an OpenAI-compatible API key
- Optional: a separate MongoDB Atlas database and vector index

Tell attendees not to use passwords, customer data, private company documents, certificates, or API keys in the workshop files.

---

## 0-5 minutes: Welcome and the problem

**Say:**

"Imagine that you have 500 company documents. A person asks, 'What does our safety guide say about batteries?' A normal chatbot may not know the answer because the information is inside our documents. We need to give the AI the right information at the right time."

"This repository demonstrates a pattern called RAG. RAG means Retrieval-Augmented Generation. That sounds complicated, but the idea is simple: first find useful information, then ask the AI to answer using that information."

Draw this on the screen:

```text
Your documents -> find useful passages -> AI writes an answer
```

Explain that RAG is not the same as training a new AI model. We are giving the model reference material during the question.

**Ask the audience:**

"If you were answering a question from a very large book, would you read the whole book every time, or would you look up the relevant pages first?"

Connect their answer to retrieval.

---

## 5-10 minutes: Tour the repository

Open the README and explain the repository in three layers.

### Layer 1: No-AI learning scripts

- `scripts/01_parser_no_ai.py` reads a file and extracts text.
- `scripts/02_chunker_no_ai.py` divides that text into smaller pieces.

These scripts need no API key. They are the best starting point because attendees can see the basic process without cloud services.

### Layer 2: AI-powered scripts

- `scripts/03_parser_agent.py` asks an AI to organize extracted text.
- `scripts/04_chunker_agent.py` asks an AI to label meaningful sections.
- `scripts/05_embedding_agent.py` turns text into numerical representations.

An agent is simply a program that performs a task, sometimes by asking an AI model for help.

### Layer 3: Search and RAG scripts

- `scripts/06_vector_store_mongodb_atlas.py` stores and searches vectors.
- `scripts/07_retrieval_agent.py` finds the most relevant chunks.
- `scripts/08_rag_pipeline.py` retrieves context and asks the AI for an answer with citations.

### Shared helper

- `scripts/workshop_common.py` contains reusable building blocks for parsing, chunking, normalization, configuration, and writing JSON output.

Explain that shared code prevents every example from repeating the same logic.

---

## 10-15 minutes: Parse a document without AI

Use a small text file first.

```powershell
.\.venv\Scripts\python scripts/01_parser_no_ai.py sample_data/guide.txt
```

**Say:**

"Parsing means reading a file and turning it into text that a computer can work with. For a text file, this is straightforward. For a PDF, the parser reads pages. For a spreadsheet, it reads rows and columns. For a Word document, it reads paragraphs."

Open `workshop_output/01_parsed_records.json`.

Point out:

- `text` is the readable content.
- `page`, `row`, `paragraph`, or `slide` tells us where the content came from.
- This location information becomes useful later when we show citations.

**When to use this script:**

Use it when you want to test whether your file can be read before adding AI or a database.

**What to change:**

Change only the input filename at first. If your file type is unsupported, add a parser for that file type in `workshop_common.py` or use a document parsing library.

---

## 15-19 minutes: Chunk the document without AI

Run:

```powershell
.\.venv\Scripts\python scripts/02_chunker_no_ai.py sample_data/guide.txt
```

**Say:**

"An AI model should not receive an entire book in one request. We divide the document into chunks. A chunk is a small piece of text. The overlap means that the end of one chunk is repeated at the beginning of the next. This helps keep an idea from being split apart."

Show the output file `workshop_output/02_chunks.json`.

Explain:

- `size` controls the maximum number of words in a chunk.
- `overlap` controls repeated words between chunks.
- Smaller chunks can be more precise.
- Larger chunks preserve more context.
- There is no perfect value for every project.

Run an experiment:

```powershell
.\.venv\Scripts\python scripts/02_chunker_no_ai.py sample_data/guide.txt --size 50 --overlap 10
```

**When to use this script:**

Use it when you need predictable, inexpensive chunking and your documents have reasonably clear text.

---

## 19-24 minutes: Add AI agents

Explain that the next two scripts add AI assistance, but the basic flow remains the same.

### Parser agent

```powershell
.\.venv\Scripts\python scripts/03_parser_agent.py sample_data/guide.txt
```

The parser agent asks the model to return structured information such as a title, summary, topics, and entities.

**Use it when:**

- Documents have inconsistent formatting
- You want labels or categories
- You need to extract names, dates, products, or topics

**Change it when:**

- Your use case needs different fields
- You need a different model provider
- Your provider does not support JSON output

Remind attendees: AI can make mistakes. Never assume extracted fields are correct without validation.

### Chunker agent

```powershell
.\.venv\Scripts\python scripts/04_chunker_agent.py sample_data/guide.txt
```

The chunker agent asks the model for a section label, then uses ordinary local chunking.

**Say:**

"Notice the important design choice: AI helps label the content, but the actual slicing is still done locally. This makes the process easier to understand and more predictable."

---

## 24-29 minutes: Embeddings in simple terms

Open `scripts/05_embedding_agent.py` and explain:

"An embedding is a list of numbers that represents the meaning of text. Texts with similar meanings tend to have similar numerical patterns. We do not read these numbers ourselves. A search system uses them to compare meaning."

Run only if credentials are configured:

```powershell
.\.venv\Scripts\python scripts/05_embedding_agent.py sample_data/guide.txt
```

Explain the configuration in `.env.example`:

- `OPENAI_API_KEY` allows the script to call the model provider.
- `OPENAI_EMBEDDING_MODEL` chooses the embedding model.
- `OPENAI_BASE_URL` can point to an OpenAI-compatible provider.

**Critical rule:**

"The embedding model and the Atlas vector index must agree about dimensions. If the model returns 1536 numbers, the index must be configured for 1536 dimensions. If you change the model, check the dimensions again."

Never place the real `.env` file in GitHub.

---

## 29-33 minutes: MongoDB Atlas and retrieval

Explain the difference between ordinary storage and vector storage:

"MongoDB stores each chunk together with its text, embedding, filename, page, and other metadata. Atlas Vector Search lets us ask for chunks that are close in meaning to a question."

Show the variables:

```env
MONGODB_URI=...
MONGODB_DATABASE=ai_workshop_demo
MONGODB_VECTOR_COLLECTION=rag_chunks
MONGODB_VECTOR_INDEX=vector_index
```

Emphasize database isolation: each project or workshop group should use its own database or collection.

Run ingestion:

```powershell
.\.venv\Scripts\python scripts/06_vector_store_mongodb_atlas.py sample_data/guide.txt
```

Run retrieval:

```powershell
.\.venv\Scripts\python scripts/07_retrieval_agent.py "What does this guide explain?"
```

Explain the retrieval result:

- The score estimates how closely a chunk matches the question.
- The text is the evidence.
- The metadata tells us where the evidence came from.

**When to use retrieval by itself:**

Use it when debugging. Before asking an AI to answer, confirm that the search found the right information. If retrieval is wrong, a better prompt will not fix the underlying problem.

---

## 33-36 minutes: Complete RAG pipeline

Run:

```powershell
.\.venv\Scripts\python scripts/08_rag_pipeline.py "What does this guide explain?"
```

Explain the flow one step at a time:

```text
Question
  -> question embedding
  -> Atlas vector search
  -> relevant chunks
  -> prompt containing those chunks
  -> AI answer with source references
```

The system prompt tells the AI:

- Use only the supplied context
- Say when the context is insufficient
- Cite sources using `[SOURCE N]`

**Say:**

"This is the point where retrieval and generation meet. Retrieval finds the evidence. Generation turns the evidence into a helpful response. Keeping these two jobs separate makes the system easier to test."

---

## 36-38 minutes: Diagnosis scripts

Explain the diagnosis folder.

### `scripts/diagnosis/09_check_environment.py`

"This asks: is my setup ready? It checks the API, MongoDB Atlas, the database, the collection, and the vector index."

### `scripts/diagnosis/10_inspect_vector_store.py`

"This asks: what is inside my vector store? It shows counts, models, dimensions, metadata, and short text previews."

### `scripts/diagnosis/11_check_vector_search_health.py`

"This asks: can the system actually perform vector search? It checks the index and can run a live test query."

### `scripts/diagnosis/17_mock_rag_pipeline.py`

```powershell
.\.venv\Scripts\python scripts/diagnosis/17_mock_rag_pipeline.py sample_data/guide.txt "What does this guide explain?"
```

"This is the no-cloud version. It uses keyword overlap instead of embeddings and an AI model. It is not a production replacement, but it teaches the shape of the RAG process without needing credentials."

---

## 38-40 minutes: Integration into another project

Use this simple integration recipe:

1. Copy or clone the repository.
2. Install `requirements.txt`.
3. Start with scripts 01 and 02 using the project’s own files.
4. Decide what metadata matters: filename, page, supplier, product, category, or date.
5. Configure the model provider in `.env`.
6. Create a separate MongoDB Atlas database and vector collection.
7. Create an Atlas vector index with dimensions matching the embedding model.
8. Run ingestion once.
9. Test retrieval before testing generation.
10. Adapt the final prompt and output format to the project’s use case.

### What usually changes

- File types and column names
- Chunk size and overlap
- Metadata fields
- Embedding model
- Chat model
- MongoDB database and collection names
- Atlas vector index dimensions
- Prompt instructions
- Output format and citations

### What usually stays the same

```text
parse -> chunk -> embed -> store -> retrieve -> generate
```

### Ready-to-copy GitHub Copilot prompt

```text
I am integrating the RAG scripts from this repository into my project.
First inspect my project structure and identify the current application entry point,
configuration system, database layer, and tests. Do not edit files yet.

My use case is: [describe the use case].
My input files are: [list file types].
My desired answer format is: [describe output].
My database is: MongoDB Atlas, using a separate database named [database name].

After inspecting the project, propose the smallest integration plan. Preserve my
existing architecture and naming conventions. Keep parsing, chunking, embedding,
retrieval, and answer generation as separate components. Never copy secrets or
production data. Identify every environment variable and Atlas index setting I need.
```

After Copilot responds, use this implementation prompt:

```text
Implement the approved RAG integration plan. Add one small change at a time.
Reuse existing project patterns. Inject the model client and database dependency
rather than creating hidden global clients. Add metadata needed for citations.
Create tests using mocked embeddings, mocked MongoDB, or an in-memory store so the
tests do not require API keys or Atlas. After each edit, run the narrowest relevant
test and report failures before continuing. Do not modify unrelated files.
```

### Closing message

"The important lesson is that an AI application is not only a prompt. It is a pipeline. We prepare the information, represent it for search, retrieve evidence, and then ask the model to explain that evidence. Once you understand each step, you can adapt the same pattern to manuals, support tickets, quality events, research papers, or any other document collection."

## Questions to ask the audience

- What file type will your project ingest?
- What metadata will help you filter or cite results?
- What should the system do when it cannot find enough evidence?
- How will you test whether retrieval found the correct chunk?
- Which part of the pipeline should remain deterministic?
