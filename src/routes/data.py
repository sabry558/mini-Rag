from fastapi import FastAPI, APIRouter, Depends, UploadFile,status
import os
from helpers.config import get_settings, settings
from controllers import DataController,ProcessController
from fastapi.responses import JSONResponse  
import aiofiles
from models import ResponseSignal
import logging
from schemes.data import ProcessRequest


logger = logging.getLogger('uvicorn.error')    

data_router=APIRouter(prefix="/api/v1/data",tags=['api_v1','data'])


@data_router.post('/upload/{project_id}')
async def upload_data(project_id:str,file:UploadFile,
                      app_settings: settings = Depends(get_settings)):
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
    return JSONResponse(content={"signal": ResponseSignal.FILE_UPLOAD_SUCCESS.value,'file_id':file_id})        


@data_router.post('/process/{project_id}')

async def process_endpoint(project_id:str,request:ProcessRequest):
    
    file_id=request.file_id
    chunk_size=request.chunk_size
    chunk_overlap=request.chunk_overlap
    process_controller=ProcessController(project_id)
    file_content=process_controller.get_file_content(file_id)
    chunks=process_controller.precess_file_content(file_content,file_id,chunk_size,chunk_overlap)   

    if chunks is None or len(chunks)==0:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content={"signal": ResponseSignal.FILE_PROCESSING_FAILED.value})

    return JSONResponse(content={"signal": ResponseSignal.FILE_PROCESSING_SUCCESS.value,'chunks':chunks}) 