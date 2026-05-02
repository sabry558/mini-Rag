from fastapi import FastAPI, APIRouter
base_router = APIRouter()
@base_router.get("/")
def main():
    return{"message":"hello world"}