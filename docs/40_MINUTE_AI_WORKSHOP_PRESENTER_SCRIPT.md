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

**Say:**

"The shared helper is like a toolbox. Instead of building the same tool eight times, we build one tool and let every script use it. The helper contains common work such as opening different file types, breaking records into chunks, reading configuration values, and writing results to a predictable output folder. Keeping this code in one place matters because a bug fixed in the helper benefits every example. It also teaches an important software habit: put repeated work in one reusable function instead of copying and pasting it into many files."

"Use the helper whenever several scripts need the same operation. In a real project, this is where you might add a new file type or standardize metadata such as filename, page, supplier, or document category. Change it carefully because many scripts depend on it; add a new function when possible instead of unexpectedly changing an existing function."

---

## 10-15 minutes: Parse a document without AI

Use a small text file first.

```powershell
.\.venv\Scripts\python scripts/01_parser_no_ai.py sample_data/guide.txt
```

**Say:**

"Parsing means reading a file and turning it into text that a computer can work with. For a text file, this is straightforward. For a PDF, the parser reads pages. For a spreadsheet, it reads rows and columns. For a Word document, it reads paragraphs."

"This step is important because an AI model cannot reason over a PDF file or spreadsheet object by itself. Before search or generation can happen, we turn the file into a common language: text plus information about where that text came from. Think of this as unpacking a suitcase. The original file is the suitcase, and parsing takes out the individual items while keeping labels that tell us where each item belonged. If parsing loses text or location information, every later step inherits that problem."

"The program receives a filename from the command line, calls the shared `parse_file` function, receives a list of records, and writes those records as JSON. JSON is easy for both people and programs to inspect. The script does not call an AI model or contact MongoDB, which makes it fast, inexpensive, and easy to debug."

Open `workshop_output/01_parsed_records.json`.

Point out:

- `text` is the readable content.
- `page`, `row`, `paragraph`, or `slide` tells us where the content came from.
- This location information becomes useful later when we show citations.

**When to use this script:**

Use it when you want to test whether your file can be read before adding AI or a database. This is the first troubleshooting step when an application produces empty answers: ask whether the useful words ever made it through the parser. It is also useful when building a new project because you can learn the shape of the input before deciding what metadata your database needs.

**What to change:**

Change only the input filename at first. If your file type is unsupported, add a parser for that file type in `workshop_common.py` or use a document parsing library. If your spreadsheet has unusual headers, first inspect the output and then add a small conversion rule. In a business project, you may also add document IDs, authors, dates, or access labels here so those values travel with the text.

---

## 15-19 minutes: Chunk the document without AI

Run:

```powershell
.\.venv\Scripts\python scripts/02_chunker_no_ai.py sample_data/guide.txt
```

**Say:**

"An AI model should not receive an entire book in one request. We divide the document into chunks. A chunk is a small piece of text. The overlap means that the end of one chunk is repeated at the beginning of the next. This helps keep an idea from being split apart."

"Chunking is important for two reasons. First, language models have limits on how much text they can process in one request. Second, search works better when each result is focused. If every search result contains an entire 300-page manual, the answer model has too much irrelevant material. If every result contains only one isolated word, it has too little context. Chunking is the practical compromise between precision and understanding."

"The script walks through each parsed record, splits its text into words, and creates windows of a chosen size. The metadata travels with each chunk, so a piece of text does not become anonymous. That connection later lets us say, 'This answer came from page 4 of this document.'"

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

Use it when you need predictable, inexpensive chunking and your documents have reasonably clear text. It is often the right first version for a new system because you can measure and understand it. Use an AI-assisted chunker only when you have a reason, such as documents with complicated sections that ordinary windows do not preserve well.

**What to change:**

Change `--size` and `--overlap` based on experiments, not guesses. Manuals may benefit from larger chunks; short support tickets may need very small chunks. Too much overlap creates duplicate results and increases cost. Too little overlap can separate a question from its explanation. Save a few example questions and compare which settings retrieve the correct passage.

---

## 19-24 minutes: Add AI agents

Explain that the next two scripts add AI assistance, but the basic flow remains the same.

### Parser agent

```powershell
.\.venv\Scripts\python scripts/03_parser_agent.py sample_data/guide.txt
```

The parser agent asks the model to return structured information such as a title, summary, topics, and entities.

**Say:**

"The no-AI parser tells us what words are present. The parser agent goes one step further and asks the model to organize those words. For example, it may turn a paragraph into a title, a summary, a list of topics, and named entities. This can make later filtering and display easier. The model is not discovering guaranteed truth; it is making a best effort to label the text we supplied."

"The script uses a system message to describe the job and a user message containing the record text. It requests JSON so the result has a predictable shape. Python then converts that JSON into a Python object and saves it beside the original record. The original text is preserved because AI output should be an addition, not a replacement for the source."

**Use it when:**

- Documents have inconsistent formatting
- You want labels or categories
- You need to extract names, dates, products, or topics

**Change it when:**

- Your use case needs different fields
- You need a different model provider
- Your provider does not support JSON output

**Why and when to use it:**

Use this agent when the structure of the information is valuable enough to justify an API call. Do not use it merely because AI is available. Every call can cost money, take time, and occasionally produce an incorrect label. Keep the original text, validate important fields, and use the no-AI parser when simple rules are sufficient.

Remind attendees: AI can make mistakes. Never assume extracted fields are correct without validation.

### Chunker agent

```powershell
.\.venv\Scripts\python scripts/04_chunker_agent.py sample_data/guide.txt
```

The chunker agent asks the model for a section label, then uses ordinary local chunking.

**Say:**

"Notice the important design choice: AI helps label the content, but the actual slicing is still done locally. This makes the process easier to understand and more predictable."

"This script is useful when a document contains meaningful sections that are not easy to detect with simple rules. A label such as 'installation', 'safety', or 'troubleshooting' can become metadata for filtering and can help us inspect search results. The label is only a hint. The actual chunk boundaries still come from the deterministic chunker, so we can reproduce the result and compare experiments."

**When to use it:**

Use it for messy documents where headings are inconsistent or missing. Do not use it for every document automatically. If a document already has clear headings, a local parser can usually capture them more cheaply and consistently.

**What to change:**

Change the requested label fields and prompt to match the subject area. A medical project might ask for condition and treatment labels; a support project might ask for product and issue type. Keep the instruction not to invent facts and test the labels with ambiguous examples.

---

## 24-29 minutes: Embeddings in simple terms

Open `scripts/05_embedding_agent.py` and explain:

"An embedding is a list of numbers that represents the meaning of text. Texts with similar meanings tend to have similar numerical patterns. We do not read these numbers ourselves. A search system uses them to compare meaning."

"Here is a simple analogy: imagine placing every sentence on a map. Sentences about batteries would land near other sentences about batteries, even if they use different words. An embedding model creates the coordinates for that map. The embedding agent sends each chunk to the model, receives its list of numbers, and attaches that list to the chunk. Later, it sends the user's question through the same model so the system can compare the question's location with the chunks' locations."

"This matters because keyword search can miss meaning. A question about 'overheating power cells' might need a passage that says 'battery temperature exceeded limits.' Vector search can recognize that relationship more easily than an exact word match. Embeddings are not magic, though. Poorly parsed text, poor chunks, or an unsuitable model still produce poor retrieval."

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

**When to use it:**

Use the embedding agent after parsing and chunking look correct. It is wasteful to pay for embeddings for text that was accidentally blank, duplicated, or incorrectly parsed. Re-run embeddings when the source text, chunking strategy, or embedding model changes.

---

## 29-33 minutes: MongoDB Atlas and retrieval

Explain the difference between ordinary storage and vector storage:

"MongoDB stores each chunk together with its text, embedding, filename, page, and other metadata. Atlas Vector Search lets us ask for chunks that are close in meaning to a question."

"The vector store script has two jobs. Without `--query`, it reads a file, creates chunks, obtains embeddings, and inserts documents into the configured collection. With `--query`, it embeds the question and sends an Atlas `$vectorSearch` request. Each stored document contains both evidence and labels. Metadata is not decoration; it makes results useful, filterable, and explainable."

"MongoDB Atlas is a cloud service, so this is the first demonstration that needs network access and credentials. The database name in `.env` determines where the data goes. A separate database or collection for each workshop group prevents one group's exercises from mixing with another group's documents."

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

Use it when debugging and evaluating. Before asking an AI to answer, confirm that the search found the right information. If retrieval is wrong, a better prompt will not fix the underlying problem. Retrieval is also useful for a search-only application, such as a document browser or a support engineer's evidence panel.

**What to change:**

Add metadata filters for your use case, such as `supplier_id`, `product`, `department`, or `document_type`. Change `top_k` when you need more or fewer passages, but remember that sending more passages to the answer model increases cost and can introduce distractions.

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

"Notice what the final script does not do: it does not ask the AI to answer from memory first. It supplies retrieved context and gives the model boundaries: use the evidence, admit when the evidence is insufficient, and identify sources. This reduces unsupported answers, although it does not eliminate them. A serious application would also validate citations, protect sensitive documents, log retrieval results, and evaluate answers with a test set."

**When to use it:**

Use the complete pipeline when the individual steps are already working. If you start here and receive a poor answer, you will not know whether parsing, chunking, embedding, retrieval, or prompting caused the problem. The staged scripts are separate so beginners can inspect the handoff between each stage.

---

## 36-38 minutes: Diagnosis scripts

Explain the diagnosis folder.

### `scripts/diagnosis/09_check_environment.py`

"This asks: is my setup ready? It checks the API, MongoDB Atlas, the database, the collection, and the vector index."

"This is important because setup errors are often mistaken for code errors. The script prints whether a dependency is reachable, but it does not print the secret itself. Run it before the workshop or whenever someone says, 'Nothing works.' It gives us a short list of likely causes before we start changing application code."

### `scripts/diagnosis/10_inspect_vector_store.py`

"This asks: what is inside my vector store? It shows counts, models, dimensions, metadata, and short text previews."

"This is important because successful insertion does not prove that the right information was stored. The script can reveal an empty collection, the wrong embedding dimensions, missing filenames, or text that was accidentally blank. Use it after ingestion and before retrieval. It is similar to opening a refrigerator to check what is actually there instead of assuming the grocery delivery arrived correctly."

### `scripts/diagnosis/11_check_vector_search_health.py`

"This asks: can the system actually perform vector search? It checks the index and can run a live test query."

"That is a stronger check than merely finding an index by name: it tests the path the application will actually use. Use it when Atlas is reachable but search results are empty, or whenever you change the embedding model or Atlas index configuration."

### `scripts/diagnosis/17_mock_rag_pipeline.py`

```powershell
.\.venv\Scripts\python scripts/diagnosis/17_mock_rag_pipeline.py sample_data/guide.txt "What does this guide explain?"
```

"This is the no-cloud version. It uses keyword overlap instead of embeddings and an AI model. It is not a production replacement, but it teaches the shape of the RAG process without needing credentials."

"This script is important for teaching because nobody should have to wait for an API key, billing account, network permission, or database administrator before learning the central idea. It parses a local file, creates chunks, compares words in the question with words in each chunk, and prints the highest-overlap passages. The search is deliberately simple, so attendees can understand the algorithm and see why semantic embeddings are useful later."

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

**Say:**

"Integration does not mean dropping every file into a new application and hoping the imports work. First identify the new application's entry point, configuration system, database layer, and test strategy. Then connect one stage at a time. A help-desk project might map documents to product and ticket metadata. A research project might map them to paper, author, and page. The reusable pattern stays the same, but the data contract around it changes."

"Start with a small sample and prove each handoff. Check parsed text before chunking. Check chunks before embeddings. Check stored documents before retrieval. Check retrieved evidence before generation. This makes failures visible and teaches a habit that applies to every software system: test the smallest useful piece before combining everything."

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

Explain that these are decisions, not just technical details. Chunk size changes search quality; metadata changes what can be filtered and cited; the embedding model changes the required Atlas dimensions; and the prompt changes how the answer is written. Participants should write down these decisions before asking Copilot to edit their project.

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

**Explain how to work with Copilot:**

"The first prompt asks Copilot to inspect before changing anything. That matters because Copilot needs to understand the existing project instead of assuming it has the same folders as this workshop repository. The second prompt gives it boundaries: make small edits, use the project's patterns, protect secrets, and run tests. Treat Copilot like a very fast assistant whose work you review. Ask it to explain what changed, inspect the diff, and run the application with sample data before trusting the result."

"Do not ask Copilot to copy this whole repository into an application. Give it the use case, input types, database, output format, and constraints. Ask for inspection first, then approve a plan, then request one small implementation step. This produces code that belongs in the new project instead of a pile of files with broken imports."

### Closing message

"The important lesson is that an AI application is not only a prompt. It is a pipeline. We prepare the information, represent it for search, retrieve evidence, and then ask the model to explain that evidence. Once you understand each step, you can adapt the same pattern to manuals, support tickets, quality events, research papers, or any other document collection."

## Questions to ask the audience

- What file type will your project ingest?
- What metadata will help you filter or cite results?
- What should the system do when it cannot find enough evidence?
- How will you test whether retrieval found the correct chunk?
- Which part of the pipeline should remain deterministic?
