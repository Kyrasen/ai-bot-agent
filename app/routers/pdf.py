from fastapi import APIRouter, UploadFile, File
from document_utils import process_pdf_upload

router = APIRouter()

@router.post("/upload_pdf")
async def upload_pdf(pdf_file: UploadFile = File(...)):
    await process_pdf_upload(pdf_file)
    return {"message": "PDF文档已成功上传并入库"}



