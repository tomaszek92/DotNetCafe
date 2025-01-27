# Job Advertisement Searcher

## Overview

The Job Advertisement Searcher is a tool designed to process and manage job advertisements. It converts HTML content to markdown, generates embeddings for text data, and stores the processed information in a Qdrant vector database for efficient searching and retrieval.

## Features

- **HTML to Markdown Conversion**: Converts job advertisement content from HTML to markdown format.
- **Embedding Generation**: Uses the Ollama library to generate embeddings for text data.
- **Qdrant Integration**: Stores processed data in a Qdrant vector database for efficient querying.

## Ollama Setup

The embedding generation relies on the Ollama library, which requires specific models to be available. Ensure you have the `mxbai-embed-large` model installed and configured. You can install it using the following command:

```bash
ollama install mxbai-embed-large
```

## Running Qdrant with Docker

To run Qdrant using Docker, you can use the following script:

```bash
# Pull the latest Qdrant Docker image
docker pull qdrant/qdrant

# Run Qdrant in a Docker container
docker run -d --name qdrant \
  -p 6333:6333 \
  qdrant/qdrant
```

This script will pull the latest Qdrant Docker image and start a container running Qdrant on port 6333.

## Installation

To install the necessary dependencies, run:
```bash
pip3 install -r requirements.txt
```

## Usage

1. **Prepare your data**: Ensure you have a CSV file containing job advertisements with columns `Id`, `Title`, and `Body`.

2. **Run the main script**: Execute the main script to process the advertisements.

```bash
python3 src/main.py
```

3. **Check the output**: Processed data will be saved in the same directory as the input CSV file, named `processed_advertisements.csv`.

## Configuration

- **Qdrant Configuration**: The QdrantManager class is configured to connect to a Qdrant instance running on `localhost` at port `6333`. Adjust these settings in `src/database/qdrant_manager.py` if needed.

## Logging

The application uses Python's logging module to provide detailed logs of the processing steps. Logs include information about the number of advertisements processed, embedding generation progress, and any errors encountered.