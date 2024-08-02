import os

from PyPDF2 import PdfReader
from docx import Document as DocxDocument

from langchain_community.document_loaders import TextLoader
 

def load_and_process_document(file_path: str):
    
    # Determine file extension
    _, file_extension = os.path.splitext(file_path)
    
    if file_extension.lower() == '.txt':
        loader = TextLoader(file_path)
        documents = loader.load()
    elif file_extension.lower() == '.pdf':
        documents = load_pdf(file_path)
    elif file_extension.lower() == '.docx':
        documents = load_docx(file_path)
    else:
        raise ValueError(f"Unsupported file type: {file_extension}")

    return documents 


def load_pdf(file_path: str):
    
    with open(file_path, 'rb') as file:
        reader = PdfReader(file)
        text = ''
        for page in reader.pages:
            text += page.extract_text() + '\n'
    return [{'text': text}]

def load_docx(file_path: str ):
    
    doc = DocxDocument(file_path)
    text = ''
    for para in doc.paragraphs:
        text += para.text + '\n'
    return [{'text': text}]