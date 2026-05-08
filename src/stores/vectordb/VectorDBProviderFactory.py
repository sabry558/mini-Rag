from providers import QdrantDBProvider
from VectorDBEnums import VectorDBEnums
from controllers.BaseController import BaseController
class VectorDBProviderFactory:

    def __init__(self, config):
        self.config=config
        self.base_controller=BaseController()

    def create(self, provider_name:str):
        if provider_name==VectorDBEnums.QDRANT.value:
            return QdrantDBProvider(db_path=self.base_controller.get_database_path(self.config.VECTOR_DB_PATH),DistanceMethod=self.config.VECTOR_DB_DISTANCE_METHOD)
        
        return None


