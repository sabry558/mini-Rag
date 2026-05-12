from ..LLMInterface import LLMInterface
from ..LLMEnums import COHEREEnums,DocumentTypeEnum
import cohere
import logging
class CoHereProvider(LLMInterface):

    def __init__(self,api_key:str,default_max_input_characters:int=1000,default_max_output_tokens:int=1000,default_temperature:float=0.1):
        
        self.api_key = api_key

        self.default_max_input_characters = default_max_input_characters
        self.default_max_output_tokens = default_max_output_tokens
        self.default_temperature = default_temperature
        
        self.generation_model_id=None
        self.embedding_model_id=None
        self.embedding_size=None

        self.client = cohere.Client(api_key=self.api_key)

        self.enums=COHEREEnums()  
         
        self.logger = logging.getLogger(__name__)
        

    def set_generartion_model(self,model_id:str):
        self.generation_model_id = model_id
        self.logger.info(f"Set generation model to {model_id}")


    def set_embedding_model(self, model_id:str, embedding_size:int):
        self.embedding_model_id = model_id
        self.embedding_size = embedding_size
        self.logger.info(f"Set embedding model to {model_id} with size {embedding_size}")    

    def process_text(self,text:str):
        return text[:self.default_max_input_characters].strip()    
    
    def generate_text(self, prompt:str, chat_history:list=[], max_output_tokens:int=None, temperature:float = None):
        if not self.client:
           self.logger.error("Cohere client not initialized")
           return None
        if not self.generation_model_id:
            self.logger.error("Generation model for cohere not set")
            return None
        max_output_tokens = max_output_tokens if max_output_tokens is not None else self.default_max_output_tokens
        temperature = temperature if temperature is not None else self.default_temperature
        
        response = self.client.chat(model=self.generation_model_id,chat_history=chat_history, message=self.process_text(prompt), max_tokens=max_output_tokens, temperature=temperature)
        
        if not response or not response.text :
            self.logger.error("No response returned from Cohere")
            return None
        return response.text
    
    def embed_text(self, text, document_type=None):
        if not self.client:
           self.logger.error("Cohere client not initialized")
           return None
        
        if not self.embedding_model_id:
            self.logger.error("Embedding model for cohere not set")
            return None
        
        input_type=COHEREEnums.DOCUMENT
        if document_type==DocumentTypeEnum.QUERY:
            input_type=COHEREEnums.QUERY

        response=self.client.embed(model=self.embedding_model_id, texts=[self.process_text(text)], input_type=input_type,embedding_types=['float'])

        if not response or not response.embeddings or not response.embeddings.float:
            self.logger.error("No embedding returned from Cohere")
            return None
        
        return response.embeddings.float[0]
    
    def construct_prompt(self, prompt:str, role:str):
         return{'role':role,'text':self.process_text(prompt)}