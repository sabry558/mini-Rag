from fastapi import FastAPI

app = FastAPI()
@app.get("/welcome")
def main():
    return("Hello, World!")