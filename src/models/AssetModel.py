from .BaseDataModel import BaseDataModel
from enums import DataBaseEnum
from db_schemes import asset
from bson import ObjectId
class AssetModel(BaseDataModel):
    def __init__(self, db_client:object):
        super().__init__(db_client)
        self.collection = self.db_client.get_collection(DataBaseEnum.COLLECTION_ASSET_NAME.value)

    @classmethod 
    async def create_instance(cls, db_client:object):
        instance=cls(db_client)
        await instance.init_collection()
        return instance    
    
    async def init_collection(self):
        all_collection=await self.db_client.list_collection_names()
        if DataBaseEnum.COLLECTION_ASSET_NAME.value not in all_collection:
            self.collection=await self.db_client.create_collection(DataBaseEnum.COLLECTION_ASSET_NAME.value)  
            indexes=asset.get_indexes()
            for index in indexes:
                await self.collection.create_index(index["key"], name=index["name"], unique=index["unique"])  


    async def create_asset(self, asset:asset):
        result = await self.collection.insert_one(asset.dict(by_alias=True, exclude_unset=True))
        asset.id=result.inserted_id
        return asset

    async def get_all_project_assets(self, asset_project_id:str):

        return await self.collection.find({"asset_project_id": ObjectId(asset_project_id) if  isinstance(asset_project_id, str) else asset_project_id}).to_list(length=None)
        assets=[asset(**record) async for record in cursor]
        return assets           