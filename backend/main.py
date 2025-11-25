from fastapi import FastAPI, Body
from processing.processing import lexical_analysis as lexical_fn
from processing.processing import tokenize as tokenize_fn
from processing.processing import remove_stopwords as remove_stopwords_fn
from processing.processing import meaningful_tokens as meaningful_tokens_fn

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

@app.post("/remove_stopwords")
def remove_stopwords_endpoint(tokens: list = Body(...)):
    clean = remove_stopwords_fn(tokens)
    return {"clean_tokens": clean}

@app.post("/meaningful_tokens")
def meaningful_tokens_endpoint(tokens: list = Body(...)):
    clean = meaningful_tokens_fn(tokens)
    return {"meaningful_tokens": clean}