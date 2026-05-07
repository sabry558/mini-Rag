from .BaseDataModel import BaseDataModel
from models.enums import DataBaseEnum
from models.db_schemes import asset
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
            indexes=asset.Asset.get_indexes()
            for index in indexes:
                await self.collection.create_index(index["key"], name=index["name"], unique=index["unique"])  


    async def create_asset(self, new_asset: asset.Asset):
        result = await self.collection.insert_one(new_asset.model_dump(by_alias=True, exclude_unset=True))
        new_asset.id = result.inserted_id
        return new_asset


    async def get_all_project_assets(self, asset_project_id:str,asset_type:str):

        records= await self.collection.find({"asset_project_id": ObjectId(asset_project_id) if  isinstance(asset_project_id, str) else asset_project_id,
                                            "asset_type": asset_type
                                            },
                                          ).to_list(length=None)
        return [asset.Asset(**record) for record in records]
    
    async def get_asset_record(self, asset_project_id: str, asset_name: str):

        if isinstance(asset_project_id, str) and not ObjectId.is_valid(asset_project_id):
            return None

        query = {"asset_project_id": ObjectId(asset_project_id) if isinstance(asset_project_id, str) else asset_project_id}
        
        if ObjectId.is_valid(asset_name):
            query["_id"] = ObjectId(asset_name)
        else:
            query["asset_name"] = asset_name

        record = await self.collection.find_one(query)

        if record:
            return asset.Asset(**record)
        
        return None
    