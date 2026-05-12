from fastapi import FastAPI
from routes import base,data,nlp
from motor.motor_asyncio import AsyncIOMotorClient
from helpers.config import get_settings
from stores.llm.LLMProviderFactory import LLMProviderFactory
from stores.vectordb.VectorDBProviderFactory import VectorDBProviderFactory
from stores.llm.templates.template_parser import TemplateParser

app = FastAPI()

async def startup_span():
    settings=get_settings()
    app.mongodb_conn = AsyncIOMotorClient(settings.MONGODB_URL)
    app.db_client = app.mongodb_conn[settings.MONGO_DATABASE_NAME]


    llm_factory=LLMProviderFactory(config=settings)

    app.generation_client=llm_factory.create(settings.GENERATION_BACKEND)
    app.generation_client.set_generartion_model(settings.GENERATION_MODEL_ID)

    app.embedding_client=llm_factory.create(settings.EMBEDDING_BACKEND)
    app.embedding_client.set_embedding_model(settings.EMBEDDING_MODEL_ID, settings.EMBEDDING_MODEL_SIZE)


    vectordb_factory = VectorDBProviderFactory(config=settings)
    app.vectordb_client = vectordb_factory.create(provider_name=settings.VECTOR_DB_BACKEND)
    app.vectordb_client.connect()

    app.template_parser=TemplateParser(language=settings.PRIMARY_LANGUAGE,default_language=settings.DEFAULT_LANGUAGE)


async def shutdown_span():
    app.mongodb_conn.close()
    app.vectordb_client.disconnect()   

 

app.on_event("startup")(startup_span)
app.on_event("shutdown")(shutdown_span)

app.include_router(base.base_router)
app.include_router(data.data_router)
app.include_router(nlp.nlp_router)