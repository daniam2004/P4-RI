from fastapi import FastAPI, Body
from processing.processing import lexical_analysis as lexical_fn
from processing.processing import tokenize as tokenize_fn
from processing.processing import remove_stopwords as remove_stopwords_fn
from processing.processing import meaningful_tokens as meaningful_tokens_fn
from processing.processing import stem_tokens as stem_tokens_fn
from indexer.indexer import build_vocabulary as build_vocabulary_fn
from indexer.indexer import compute_tf as compute_tf_fn
from indexer.indexer import compute_idf as compute_idf_fn, compute_tfidf as compute_tfidf_fn
from indexer.indexer import select_relevant_terms as select_relevant_terms_fn
from indexer.indexer import build_inverted_index as build_inverted_index_fn
from indexer.indexer import vectorize_document as vectorize_document_fn

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

@app.post("/lemmatize")
def lemmatize_endpoint(tokens: list = Body(...)):
    stemmed = stem_tokens_fn(tokens)
    return {"stemmed_tokens": stemmed}

@app.post("/vocabulary")
def vocabulary_endpoint(documents: list = Body(...)):
    vocab = build_vocabulary_fn(documents)
    return {"vocabulary": vocab}

@app.post("/tf")
def tf_endpoint(document_tokens: list = Body(...), vocabulary: list = Body(...)):
    tf = compute_tf_fn(document_tokens, vocabulary)
    return {"tf": tf}

@app.post("/idf")
def idf_endpoint(documents: list = Body(...), vocabulary: list = Body(...)):
    idf = compute_idf_fn(documents, vocabulary)
    return {"idf": idf}

@app.post("/tfidf")
def tfidf_endpoint(document_tokens: list = Body(...), vocabulary: list = Body(...), idf: dict = Body(None)):
    if idf is None:
        return {"error": "Se requiere un diccionario IDF"}
    
    tfidf = compute_tfidf_fn(document_tokens, vocabulary, idf)
    return {"tfidf": tfidf}

@app.post("/relevant_terms")
def relevant_terms_endpoint(tfidf: dict = Body(...), k: int = 5):
    selected = select_relevant_terms_fn(tfidf, k)
    return {"relevant_terms": selected}

@app.post("/inverted_index")
def inverted_index_endpoint(documents: list = Body(...)):
    index = build_inverted_index_fn(documents)
    return {"inverted_index": index}

@app.post("/vectorize")
def vectorize_endpoint(tfidf: dict = Body(...), vocabulary: list = Body(...)):
    vector = vectorize_document_fn(tfidf, vocabulary)
    return {"vector": vector}