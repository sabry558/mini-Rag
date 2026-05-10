from fastapi import FastAPI, APIRouter, Depends, UploadFile,status,Request
import os
from helpers.config import get_settings, settings
from fastapi.responses import JSONResponse  
import logging
from models.ProjectModel import ProjectModel
from models.ChunkModel import ChunkModel
from routes.schemes.nlp_schema import PushRequest, SearchRequest
from controllers.NlpController import NlpController
from models.enums.ResponseEnum import ResponseSignal
    

logger = logging.getLogger('uvicorn.error') 
nlp_router=APIRouter(prefix="/api/v1/nlp",tags=['api_v1','nlp'])


@nlp_router.post("/index/push/{project_id}")
async def index_project(request:Request,project_id:str,push_request:PushRequest):
    project_model = await ProjectModel.create_instance(
        db_client=request.app.db_client
    )

    project = await project_model.get_project_or_create_one(
        project_id=project_id
    )

    if not project:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"signal": ResponseSignal.PROJECT_NOT_FOUND.value})

    nlp_controller=NlpController(
        vectordb_client=request.app.vectordb_client,
        generation_client=request.app.generation_client,
        embedding_client=request.app.embedding_client
    )
    
    chunk_model=await ChunkModel.create_instance(
        db_client=request.app.db_client )
    
    has_records=True
    page_number=1
    inserted_items_count=0
    idx=0
    while(has_records):
        chunks=await chunk_model.get_chunks_by_project_id(project_id=project.id, page=page_number)
        if not chunks or len(chunks)==0:
            has_records=False
            break
        page_number += 1

        chunk_ids=list(range(idx,idx+len(chunks)))
        idx+=len(chunks)
        
        is_inserted=nlp_controller.index_into_vector_db(project=project,chunks=chunks,chunk_ids=chunk_ids,do_reset=push_request.do_reset)

        if not is_inserted:
            return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,content={"signal": ResponseSignal.INDEXING_FAILED.value})
        inserted_items_count += len(chunks)


    return JSONResponse(status_code=status.HTTP_200_OK,content={"signal": ResponseSignal.INDEXING_SUCCESS.value
                                                                ,"indexed_items_count": inserted_items_count
                                                                })    

@nlp_router.get("/index/info/{project_id}")

async def get_project_index_info(request:Request,project_id:str):

    project_model = await ProjectModel.create_instance(
        db_client=request.app.db_client
    )

    project = await project_model.get_project_or_create_one(
        project_id=project_id
    )

    if not project:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"signal": ResponseSignal.PROJECT_NOT_FOUND.value})



    nlp_controller=NlpController(
        vectordb_client=request.app.vectordb_client,
        generation_client=request.app.generation_client,
        embedding_client=request.app.embedding_client
    )

    index_info=nlp_controller.get_vector_db_collection_info(project=project)

    if index_info is None:
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,content={"signal": ResponseSignal.FETCHING_INDEX_INFO_FAILED.value})

    return JSONResponse(status_code=status.HTTP_200_OK,content={"signal": ResponseSignal.FETCHING_INDEX_INFO_SUCCESS.value
                                                                ,"index_info": index_info
                                                                })

@nlp_router.post("/index/search/{project_id}")
async def search_index(request:Request,project_id:str,search_request:SearchRequest):
    project_model = await ProjectModel.create_instance(
        db_client=request.app.db_client
    )

    project = await project_model.get_project_or_create_one(
        project_id=project_id
    )

    if not project:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"signal": ResponseSignal.PROJECT_NOT_FOUND.value})

    nlp_controller=NlpController(
        vectordb_client=request.app.vectordb_client,
        generation_client=request.app.generation_client,
        embedding_client=request.app.embedding_client)
    
    result=nlp_controller.search_vector_db_collection(project=project,text=search_request.query_text,limit=search_request.limit)

    if not result:
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,content={"signal": ResponseSignal.SEARCHING_INDEX_FAILED.value})
    
    return JSONResponse(status_code=status.HTTP_200_OK,content={"signal": ResponseSignal.SEARCHING_INDEX_SUCCESS.value
                                                                ,"search_results": result})