from fastapi import FastAPI, Body
import re
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
from indexer.indexer import cosine_similarity as cosine_similarity_fn
from indexer.indexer import search_query as search_query_fn
from crawler.crawler import load_docs as load_docs_fn
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from crawler.crawler import load_docs
from crawler.crawler import (
    download_gutenberg_docs,
    download_wikipedia_docs,
    download_wikipedia_docs_html
)
from processing.processing import (
    lexical_analysis,
    tokenize,
    remove_stopwords,
    meaningful_tokens,
    stem_tokens
)
from indexer.indexer import (
    build_vocabulary,
    compute_idf,
    compute_tfidf,
    vectorize_document,
    cosine_similarity
)


app = FastAPI()
CORPUS_DOCUMENTS = []
CORPUS_TOKENS = []
VOCABULARY = []
IDF = {}
DOCUMENT_VECTORS = {}

def initialize_corpus_index():
    global CORPUS_DOCUMENTS, CORPUS_TOKENS, VOCABULARY, IDF, DOCUMENT_VECTORS

    print("Inicializando índice global del corpus...")

    # Cargar documentos
    CORPUS_DOCUMENTS = load_docs()

    if not CORPUS_DOCUMENTS:
        print("No hay documentos para indexar.")
        return
    
    # Procesarmiento lingüístico
    CORPUS_TOKENS = []
    for doc in CORPUS_DOCUMENTS:
        text = doc["text"]

        text = lexical_analysis(text)
        tokens = tokenize(text)
        tokens = remove_stopwords(tokens)
        tokens = meaningful_tokens(tokens)
        tokens = stem_tokens(tokens)

        CORPUS_TOKENS.append(tokens)

    # Vocabulario global
    VOCABULARY = build_vocabulary(CORPUS_TOKENS)

    # IDF global
    IDF = compute_idf(CORPUS_TOKENS, VOCABULARY)

    # Vectorizar documentos
    DOCUMENT_VECTORS = {}
    for doc, tokens in zip(CORPUS_DOCUMENTS, CORPUS_TOKENS):
        tfidf = compute_tfidf(tokens, VOCABULARY, IDF)
        vector = vectorize_document(tfidf, VOCABULARY)
        DOCUMENT_VECTORS[doc["id"]] = vector
    
    print("Índice global del corpus inicializado.")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permitir todas las apps (React)
    allow_credentials=True,
    allow_methods=["*"],  # Permitir POST, GET, OPTIONS...
    allow_headers=["*"],
)

initialize_corpus_index()

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

@app.post("/similarity")
def similarity_endpoint(vec1: list = Body(...), vec2: list = Body(...)):
    similarity = cosine_similarity_fn(vec1, vec2)
    return {"similarity": similarity}

@app.post("/search")
def search_endpoint(query_vector: list = Body(...), document_vectors: dict = Body(...)):
    results = search_query_fn(query_vector, document_vectors)
    return {"search_results": results}

def remove_gutenberg_header(text: str) -> str:
    lower = text.lower()

    patterns = [
        r"\*\*\*\s*start of.*?\*\*\*",
        r"start of the project gutenberg ebook",
        r"start of this project gutenberg",
    ]

    for pattern in patterns:
        match = re.search(pattern, lower, re.DOTALL)
        if match:
            return text[match.end():]
    
    return text[5000:]

class SearchRequest(BaseModel):
    query: str
    k: int = 5

def split_into_paragraphs(text: str) -> list:
    paragraphs = [
        p.strip()
        for p in text.split("\n")
        if len(p.strip()) > 50
    ]
    return paragraphs


def extract_snippet_phrase(text: str, query_phrase: str) -> str:
    if not text or not query_phrase:
        return ""
    
    clean_text = remove_gutenberg_header(text)
    paragraphs = split_into_paragraphs(clean_text)

    phrase_lower = query_phrase.lower()

    for paragraph in paragraphs:
        if phrase_lower in paragraph.lower():
            return paragraph.replace("\n", " ").strip()
        
    return ""

def extract_snippet_tokens(text: str, tokens: list) -> str:
    if not text or not tokens:
        return ""
    
    clean_text = remove_gutenberg_header(text)
    paragraphs = split_into_paragraphs(clean_text)

    for paragraph in paragraphs:
        p_lower = paragraph.lower()
        for token in tokens:
            if token in p_lower:
                return paragraph.replace("\n", " ").strip()
            
    return ""

@app.post("/full_search")
def full_search_endpoint(request: SearchRequest):
    query = request.query
    k = request.k
    if not VOCABULARY or not DOCUMENT_VECTORS:
        return {"error": "El índice del corpus no está inicializado."}
    
    # Procesar query
    q_clean = lexical_fn(query)
    q_tokens = tokenize_fn(q_clean)
    query_phrase = " ".join(q_tokens)
    q_tokens = remove_stopwords_fn(q_tokens)
    q_tokens = meaningful_tokens_fn(q_tokens)
    q_tokens = stem_tokens_fn(q_tokens)

    # TF-IDF de la query usando vocabulario e IDF GLOBAL
    q_tfidf = compute_tfidf_fn(q_tokens, VOCABULARY, IDF)
    q_vector = vectorize_document_fn(q_tfidf, VOCABULARY)

    # Comparar con documentos del corpus
    ranking = {}
    for doc_id, doc_vector in DOCUMENT_VECTORS.items():
        sim = cosine_similarity_fn(q_vector, doc_vector)
        
        if sim > 0:
            ranking[doc_id] = sim
    
    # Ordenar resultados
    ranking = dict(
        sorted(ranking.items(), key = lambda x: x[1], reverse = True)
    )

    ranking = dict(list(ranking.items())[:k])

    if ranking:
        max_score = max(ranking.values())
        if max_score > 0:
            ranking = {
                doc_id: score / max_score
                for doc_id, score in ranking.items()
            }
    results = []
    for doc_id, score in ranking.items():
        if score <= 0:
            continue

        doc = next(d for d in CORPUS_DOCUMENTS if d["id"] == doc_id)
        snippet = extract_snippet_phrase(doc["text"], query_phrase)

        if not snippet:
            snippet = extract_snippet_tokens(doc["text"], q_tokens)

        results.append({
            "doc_id": doc_id,
            "doc_name": doc["name"],
            "score": score,
            "snippet": snippet
        })

    return {
        "query": query,
        "results": results 
    }

@app.get("/status")
def status_endpoint():
    return {
        "indexed": bool(DOCUMENT_VECTORS),
        "num_documents": len(CORPUS_DOCUMENTS),
        "vocabulary_size": len(VOCABULARY),
        "vector_dimension": len(VOCABULARY)
    }

@app.get("/load_docs")
def load_docs_endpoint():
    docs = load_docs_fn()
    return {"documents": docs}

@app.get("/download_gutenberg")
def download_gutenberg_endpoint():
    download_gutenberg_docs()
    return {
        "status": "ok",
        "message": "Descarga de Project Gutenberg completada."
    }

@app.get("/download_wikipedia")
def download_wikipedia_endpoint():
    download_wikipedia_docs()
    return {
        "status": "ok",
        "message": "Artículos de wikipedia descargados."
    }

@app.get("/download_wikipedia_html")
def download_wikipedia_html_endpoint():
    download_wikipedia_docs_html()
    return {
        "status": "ok",
        "message": "Artículo de wikipedia descargados vía html"
    }

@app.get("/reindex")
def reindex_endpoint():
    initialize_corpus_index()
    return {
        "status": "ok",
        "message": "Índice global del corpus reconstruido."
    }
