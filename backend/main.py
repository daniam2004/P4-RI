from fastapi import FastAPI
from processing.processing import lexical_analysis as lexical_fn
from processing.processing import tokenize as tokenize_fn

app = FastAPI()
@app.get("/")
def hello():
    return {"message": "Hola mundo, desde FastAPI"}

@app.post("/lexical_analysis")
def lexical_endpoint(document: str):
    cleaned = lexical_fn(document)
    return {"cleaned_text": cleaned}

@app.post("/tokenize")
def tokenize_endpoint(document: str):
    tokens = tokenize_fn(document)
    return {"tokens": tokens}

