from pydantic import BaseModel, Field
from typing import Optional
from bson.objectid import ObjectId  
from datetime import datetime

class Asset(BaseModel):
    id: Optional[ObjectId] = Field(default=None, alias="_id")
    asset_project_id: ObjectId
    asset_type: str
    asset_name: str
    asset_size: int
    asset_config: dict=Field(default=None)
    asset_pushed_at:datetime=Field(default_factory=datetime.utcnow)

    model_config = {
        "arbitrary_types_allowed": True
    }


    @classmethod
    def get_indexes(cls):
        return[
            {
                "key": [("asset_project_id", 1)],
                'name': "asset_project_id_index_1",
                "unique": False
            },
                        {
                "key": [("asset_project_id", 1),("asset_name", 1)],
                'name': "asset_project_id_name_index_1",
                "unique": True
            }

        ]     