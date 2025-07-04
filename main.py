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

    subsections = processed_pdf['subsections']
    subsections_count = len(subsections)

    response = PDFResponse(
        document_name=processed_pdf['document_name'],
        subsections_count=subsections_count,
        subsections=subsections
    )
    return response