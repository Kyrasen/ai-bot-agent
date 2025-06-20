from fastapi import UploadFile
from pathlib import Path
from config import VECTOR_STORE_DIR
from deps import embedding_model
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
import os

'''
    处理用户上传的文件并将其进行文档分割，然后存入到数据库中
'''

async def process_pdf_upload(pdf_file: UploadFile):
    upload_path = Path("uploaded") / pdf_file.filename
    os.makedirs("uploaded", exist_ok=True)
    with open(upload_path, "wb") as f:
        f.write(await pdf_file.read())

    loader = PyPDFLoader(str(upload_path))
    docs = RecursiveCharacterTextSplitter(chunk_size=50, chunk_overlap=20).split_documents(loader.load())

    index_path = Path(VECTOR_STORE_DIR) / "index.faiss"
    if index_path.exists():
        db = FAISS.load_local(VECTOR_STORE_DIR, embedding_model, allow_dangerous_deserialization=True)
        db.add_documents(docs)
        db.save_local(VECTOR_STORE_DIR)  # 别忘了更新保存
    else:
        db = FAISS.from_documents(docs, embedding_model)
        db.save_local(VECTOR_STORE_DIR)

    print("[INFO]: 文档解析完成")



