from fastapi import FastAPI, APIRouter, Depends, UploadFile,status,Request
import os
from helpers.config import get_settings, settings
from controllers import DataController,ProcessController
from fastapi.responses import JSONResponse  
import aiofiles
from models import ResponseSignal
import logging
from schemes.data import ProcessRequest
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

    project_model=ProjectModel.create_instance(request.app.db_client)
    project=await project_model.get_project_or_create_one(project_id)  

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
    
    asset_model=AssetModel.create_instance(request.app.db_client)
    asset_resource=asset.Asset(
        asset_project_id=project.id,
        asset_type=AssetTypeEnum.FILE.value,
        asset_name=file_id,
        asset_size=os.path.getsize(file_path),
        asset_config={"file_path":file_path}
    )
    asset_record=await asset_model.create_asset(asset_resource)
    return JSONResponse(content={"signal": ResponseSignal.FILE_UPLOAD_SUCCESS.value,'file_id':str(asset_record.id)})        


@data_router.post('/process/{project_id}')

async def process_endpoint(request:Request,project_id:str,process_request:ProcessRequest):
    project_model=ProjectModel.create_instance(request.app.db_client)
    project=await project_model.get_project_or_create_one(project_id) 
    chunk_model=await ChunkModel.create_instance(request.app.db_client)

    file_id=process_request.file_id
    chunk_size=process_request.chunk_size
    chunk_overlap=process_request.chunk_overlap
    do_reset=process_request.do_reset


    process_controller=ProcessController(project_id)
    file_content=process_controller.get_file_content(file_id)
    chunks=process_controller.process_file_content(file_content,file_id,chunk_size,chunk_overlap)   

    if chunks is None or len(chunks)==0:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content={"signal": ResponseSignal.FILE_PROCESSING_FAILED.value})
    
    
    if do_reset:
        deleted_count=await chunk_model.delete_chunks_by_project_id(project_id)


    chunks_record=[
        DataChunk(chunk_text=chunk.page_content,
                  chunk_metadata=chunk.metadata,
                  chunk_order=i+1,
                  chunk_project_id=project.id)
        
        for i,chunk in enumerate(chunks)
    ]
    no_record_inserted=await chunk_model.insert_chunks(chunks_record)
    return JSONResponse(content={"signal": ResponseSignal.FILE_PROCESSING_SUCCESS.value,'inserted_chunks':no_record_inserted})