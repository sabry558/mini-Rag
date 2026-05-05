from .BaseDataModel import BaseDataModel
from models.db_schemes import project
from models.enums import DataBaseEnum
class ProjectModel(BaseDataModel):
    def __init__(self, db_client:object):
        super().__init__(db_client)
        self.collection = self.db_client.get_collection(DataBaseEnum.COLLECTION_PROJECT_NAME.value)

    @classmethod 
    async def create_instance(cls, db_client:object):
        instance=cls(db_client)
        await instance.init_collection()
        return instance

    async def init_collection(self):
        all_collection = await self.db_client.list_collection_names()
        if DataBaseEnum.COLLECTION_PROJECT_NAME.value not in all_collection:
            self.collection = await self.db_client.create_collection(DataBaseEnum.COLLECTION_PROJECT_NAME.value)  
            indexes = project.Project.get_indexes()
            for index in indexes:
                await self.collection.create_index(index["key"], name=index["name"], unique=index["unique"])  

    async def create_project(self, proj: project.Project):
        result = await self.collection.insert_one(proj.model_dump(by_alias=True, exclude_unset=True))
        proj.id = result.inserted_id
        return proj

    async def get_project_or_create_one(self, project_id:str):
        record = await self.collection.find_one({"project_id": project_id})

        if record is None:
            new_project = project.Project(project_id=project_id)
            return await self.create_project(new_project)
        return project.Project(**record)

    async def get_project_all_projects(self,page:int=1,page_size:int=1):
        total_documents=await self.collection.count_documents({})

        total_pages=total_documents//page_size
        if total_documents%page_size!=0:
            total_pages+=1
        cursor=self.collection.find().skip((page-1)*page_size).limit(page_size)
        projects=[project(**record) async for record in cursor]
        return projects,total_pages    


       