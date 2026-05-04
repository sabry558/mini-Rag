from .BaseDataModel import BaseDataModel
from db_schemes import project
from enums import DataBaseEnum
class ProjectModel(BaseDataModel):
    def __init__(self, db_client:object):
        super().__init__(db_client)
        self.collection = self.db_client.get_collection(DataBaseEnum.PROJECTS.value)
    async def create_project(self, project:project):
        result = await self.collection.insert_one(project.dict(by_alias=True, exclude_unset=True))
        project._id=result.inserted_id
        return project

    async def get_project_or_create_one(self, project_id:str):
        record=self.collection.find_one({"project_id": project_id})

        if record is None:
            new_project=project(project_id=project_id)
            return await self.create_project(new_project)
        return project(**record)

    async def get_project_all_projects(self,page:int=1,page_size:int=1):
        total_documents=await self.collection.count_documents({})

        total_pages=total_documents//page_size
        if total_documents%page_size!=0:
            total_pages+=1
        cursor=self.collection.find().skip((page-1)*page_size).limit(page_size)
        projects=[project(**record) async for record in cursor]
        return projects,total_pages    


       