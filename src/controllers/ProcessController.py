from BaseController import BaseController
from ProjectController import ProjectController
from langchain.document_loaders import text_loader
from langchain.document_loaders import PyMuPDFLoader
from models import ProcessingEnum
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os
class ProcessController(BaseController):

    def __init__(self,project_id:str):
        super().__init__()
        self.project_id=project_id
        self.project_path=ProjectController().get_project_path(project_id)
    
    def get_file_extenstion(self,file_id:str):
        _,ext=os.path.splitext(file_id)
        return ext
    def get_file_laoder(self,file_id:str):
        ext=self.get_file_extenstion(file_id)
        file_path=os.path.join(self.project_path,file_id)
        if ext==ProcessingEnum.TXT.value:
            return text_loader(file_path,encoding='utf-8')
        if ext==ProcessingEnum.PDF.value:
            return PyMuPDFLoader(file_path)
        return None 
    def get_file_content(self,file_id:str):
        loader=self.get_file_laoder(file_id)
        return loader.load()    
    
    def precess_file_content(self,file_content:list,file_id:str,chunk_size:int=100,chunk_overlap:int=20):
        text_splitter=RecursiveCharacterTextSplitter(chunk_size=chunk_size,chunk_overlap=chunk_overlap,length_function=len)

        file_content_text=[rec.page_content for rec in file_content]
        file_content_metadata=[rec.metadata for rec in file_content]

        chunks=text_splitter.create_documents(file_content_text,metadatas=file_content_metadata)

        return chunks
  
