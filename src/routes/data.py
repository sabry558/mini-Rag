from fastapi import FastAPI, APIRouter, Depends, UploadFile,status,Request
import os
from helpers.config import get_settings, settings
from controllers import DataController,ProcessController
from fastapi.responses import JSONResponse  
import aiofiles
from models import ResponseSignal
import logging
from routes.schemes.data import ProcessRequest
from models.ProjectModel import ProjectModel
from models.ChunkModel import ChunkModel
from models.db_schemes import DataChunk,asset
from models.AssetModel import AssetModel
from models.enums import AssetTypeEnum
 

logger = logging.getLogger('uvicorn.error')    

data_router=APIRouter(prefix="/api/v1/data",tags=['api_v1','data'])


@data_router.post('/upload/{project_id}')
async def upload_data(request:Request,project_id:str,file:UploadFile,
                      app_settings: settings = Depends(get_settings)):

    project_model = await ProjectModel.create_instance(request.app.db_client)
    project = await project_model.get_project_or_create_one(project_id)  

    # validate file properties
    data_controller=DataController()    
    is_valid,result_signal=data_controller.validate_uploaded_file(file)
    if not is_valid:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content={"signal": result_signal})
    
    file_path,file_id=data_controller.generate_unique_filepath(file.filename,project_id)
    try:
        async with aiofiles.open(file_path,'wb') as f:
            while chunk:=await file.read(app_settings.FILE_DEFAULT_CHUNK_SIZE):
                await f.write(chunk)
    except Exception as e:
        logger.error(f"Error while uploading file: {e}")
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content={"signal": ResponseSignal.FILE_UPLOAD_FAILED.value})
    
    asset_model = await AssetModel.create_instance(request.app.db_client)
    asset_resource=asset.Asset(
        asset_project_id=project.id,
        asset_type=AssetTypeEnum.FILE.value,
        asset_name=file.filename,
        asset_size=os.path.getsize(file_path),
        asset_config={"stored_file_id":file_id, "file_path":file_path}
    )
    asset_record=await asset_model.create_asset(asset_resource)
    return JSONResponse(content={"signal": ResponseSignal.FILE_UPLOAD_SUCCESS.value,'file_id':str(asset_record.id)})        


@data_router.post('/process/{project_id}')

async def process_endpoint(request:Request,project_id:str,process_request:ProcessRequest):
    project_model=await ProjectModel.create_instance(request.app.db_client)
    project=await project_model.get_project_or_create_one(project_id)
    asset_model = await AssetModel.create_instance(request.app.db_client)

    project_file_ids={}
    if process_request.file_id:
        asset=await asset_model.get_asset_by_project_id_and_name(project_id, process_request.file_id)
        if asset is None:
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content={"signal": ResponseSignal.FILE_ID_ERROR.value})
        project_file_ids[asset.id] = asset.asset_name
    else:
        asset_model = await AssetModel.create_instance(request.app.db_client)
        project_files = await asset_model.get_all_project_assets(project_id, AssetTypeEnum.FILE.value)
        project_file_ids={asset.id:asset.asset_name for asset in project_files}
    
    if len(project_file_ids)==0:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content={"signal": ResponseSignal.NO_FILES_ERROR.value})
    

    chunk_model=await ChunkModel.create_instance(request.app.db_client)
    chunk_size=process_request.chunk_size
    chunk_overlap=process_request.chunk_overlap
    do_reset=process_request.do_reset

    asset_model = await AssetModel.create_instance(request.app.db_client)
    if do_reset:
        _=await chunk_model.delete_chunks_by_project_id(project_id)
    no_record_inserted=0
    no_of_files=0


    for asset_id,file_id in project_file_ids.items():
        asset_record = await asset_model.get_asset_by_id(file_id)
        if not asset_record:
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content={"signal": "ASSET_NOT_FOUND"})

        stored_file_id = asset_record.asset_config.get("stored_file_id")

        process_controller=ProcessController(project_id)
        file_content=process_controller.get_file_content(stored_file_id)

        if file_content is None:
            logger.error(f"Failed to load content for file_id: {file_id} with stored_file_id: {stored_file_id}")  
            continue
        chunks=process_controller.process_file_content(file_content,stored_file_id,chunk_size,chunk_overlap)   

        if chunks is None or len(chunks)==0:
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content={"signal": ResponseSignal.FILE_PROCESSING_FAILED.value})
        
        


        chunks_record=[
            DataChunk(chunk_text=chunk.page_content,
                    chunk_metadata=chunk.metadata,
                    chunk_order=i+1,
                    chunk_project_id=project.id,
                    chunk_asset_id=asset_id
                    )
            
            for i,chunk in enumerate(chunks)
        ]
        no_record_inserted=await chunk_model.insert_many_chunks(chunks_record)
        no_of_files+=1
    return JSONResponse(content={"signal": ResponseSignal.PROCESSING_SUCCESS.value,'inserted_chunks':no_record_inserted,'processed_files':no_of_files})