from .BaseController import BaseController
from models.db_schemes import Project
from models.db_schemes import DataChunk
from typing import List
from stores.llm.LLMEnums import DocumentTypeEnum
import json
class NlpController(BaseController):

    def __init__(self,vectordb_client,generation_client,embedding_client):
        super().__init__()
        self.vectordb_client=vectordb_client
        self.generation_client=generation_client
        self.embedding_client=embedding_client

    def create_collection_name(self,project_id:str):
        return f"collection_{project_id}".strip()
    
    def reset_vector_db_collection(self,project:Project):
        collection_name=self.create_collection_name(project_id=project.id)
        return self.vectordb_client.delete_collection(collection_name=collection_name)


    def get_vector_db_collection_info(self,project:Project):
        collection_name=self.create_collection_name(project_id=project.id)
        collection_info=self.vectordb_client.get_collection_info(collection_name=collection_name)
        return json.loads(
            json.dumps(collection_info,default=lambda x: x.__dict__)
        )
    
    def index_into_vector_db(self,project:Project,chunks:List[DataChunk],chunk_ids:List[int]=None,do_reset:bool=False):
        collection_name=self.create_collection_name(project_id=project.id)
        if do_reset:
            self.reset_vector_db_collection(project=project)

        texts=[chunk.chunk_text for chunk in chunks]    
        metadatas=[chunk.chunk_metadata for chunk in chunks]

        vectors=[self.embedding_client.embed_text(text,DocumentTypeEnum.DOCUMENT.value) for text in texts]

        _=self.vectordb_client.create_collection(collection_name=collection_name,vector_size=self.embedding_client.embedding_size,do_reset=do_reset)

        self.vectordb_client.insert_many(collection_name=collection_name,texts=texts,vectors=vectors,record_ids=chunk_ids,metadata=metadatas)

        return True

    def search_vector_db_collection(self,project:Project,text:str,limit:int=5):
        collection_name=self.create_collection_name(project_id=project.id)
        query_vector=self.embedding_client.embed_text(text,DocumentTypeEnum.QUERY.value)
        if not query_vector:
            return False
        search_results=self.vectordb_client.search_by_vector(collection_name=collection_name,query_vector=query_vector,limit=limit)
        if not search_results:
            return False
        return json.loads(
            json.dumps(search_results,default=lambda x: x.__dict__)
        )
