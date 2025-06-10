
# FastAPI PDF Parser

This is a simple FastAPI application that provides a `POST` endpoint `/parse`. The endpoint accepts a PDF file via a multipart form request, parses the content of the PDF, and returns a hierarchical JSON structure with sections and their respective content.

## Features
- Accepts only PDF file.
- Extracts the content and organizes it into a hierarchical JSON structure.
- Returns the parsed content with sections identified and their text content.

## Requirements

- Python 3.7+
- FastAPI
- Uvicorn (ASGI server)
- PyMuPDF (for PDF operations)
- Conda environment

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/yourusername/fastapi-pdf-parser.git
    cd fastapi-pdf-parser
    ```

2. Create a conda environment (optional but recommended):
    ```bash
    conda create --name fastapi-pdf-parser python=3.12
    conda activate fastapi-pdf-parser
    ```

3. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

    Or install dependencies manually with conda for better environment management:
    ```bash
    conda install -c conda-forge fastapi uvicorn pymupdf
    ```

## Usage

To start the FastAPI server, run the following command:

```bash
uvicorn main:app --reload
```

By default, the API will run on `http://127.0.0.1:8000`.

### `/parse` Endpoint

- **Method**: `POST`
- **Endpoint**: `/parse`
- **Request**:
  - `file`: A PDF file (multipart/form-data). This is received as a binary payload.

#### Example Request (using `curl`):

```bash
curl -X 'POST'   'http://127.0.0.1:8000/parse'   -F 'file=@path_to_pdf_file.pdf'
```