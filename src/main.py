from fastapi import FastAPI
from routes import base,data
from motor.motor_asyncio import AsyncIOMotorClient
from helpers.config import get_settings
from stores.llm.LLMProviderFactory import LLMProviderFactory
app = FastAPI()

async def startup_db_client():
    settings=get_settings()
    app.mongodb_conn = AsyncIOMotorClient(settings.MONGODB_URL)
    app.db_client = app.mongodb_conn[settings.MONGO_DATABASE_NAME]


    llm_factory=LLMProviderFactory(config=settings)

    app.generation_client=llm_factory.create(settings.GENERATION_BACKEND)
    app.generation_client.set_generartion_model(settings.GENERATION_MODEL_ID)

    app.embedding_client=llm_factory.create(settings.EMBEDDING_BACKEND)
    app.embedding_client.set_embedding_model(settings.EMBEDDING_MODEL_ID, settings.EMBEDDING_MODEL_SIZE)


async def shutdown_db_client():
    app.mongodb_conn.close()   

app.router.lifespan.on_startup.append(startup_db_client)

app.router.lifespan.on_shutdown.append(shutdown_db_client)     
app.include_router(base.base_router)
app.include_router(data.data_router)