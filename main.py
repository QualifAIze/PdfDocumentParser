from io import BytesIO

from fastapi import FastAPI
from fastapi import UploadFile, File, status, HTTPException

from models import PDFResponse
from preprocess_pdf import PreprocessPDF

app = FastAPI()


@app.post("/parse", response_model=PDFResponse, status_code=status.HTTP_201_CREATED)
async def parse_document_to_tree(file: UploadFile = File(...)) -> PDFResponse:
    if file.content_type != "application/pdf":
        raise HTTPException(400, detail="Invalid document type")

    bytes_content = await file.read()
    bytes_stream = BytesIO(bytes_content)
    preprocessor = PreprocessPDF(bytes_stream, file.filename)
    processed_pdf = preprocessor.process()

    toc = processed_pdf['subsections'][0]
    toc_with_content = processed_pdf['subsections'][1]

    response = PDFResponse(original_file_name=processed_pdf['title'], toc=toc, toc_with_content=toc_with_content)
    return response
