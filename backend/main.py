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
from indexer.indexer import cosine_similarity as cosine_similarity_fn
from indexer.indexer import search_query as search_query_fn

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

@app.post("/similarity")
def similarity_endpoint(vec1: list = Body(...), vec2: list = Body(...)):
    similarity = cosine_similarity_fn(vec1, vec2)
    return {"similarity": similarity}

@app.post("/search")
def search_endpoint(query_vector: list = Body(...), document_vectors: dict = Body(...)):
    results = search_query_fn(query_vector, document_vectors)
    return {"search_results": results}

@app.post("/full_search")
def full_search_endpoint(query: str = Body(...), documents: list = Body(...)):
    
    # Procesar consulta
    q_clean = lexical_fn(query)
    q_tokens = tokenize_fn(q_clean)
    q_tokens = remove_stopwords_fn(q_tokens)
    q_tokens = meaningful_tokens_fn(q_tokens)

    # Procesar documentos
    processed_docs = []
    for doc in documents:
        doc_id = doc.get("id")
        tokens = doc.get("tokens", [])

        if not isinstance(doc_id, str) or not isinstance(tokens, list):
            continue

        tokens = [t.lower() for t in tokens]
        tokens = remove_stopwords_fn(tokens)
        tokens = meaningful_tokens_fn(tokens)
        tokens = stem_tokens_fn(tokens)

        processed_docs.append({
            "id": doc_id,
            "tokens": tokens
        })
    
    # Construir vocabulario
    vocab = set(q_tokens)
    for doc in processed_docs:
        vocab.update(doc["tokens"])
    vocab = sorted(list(vocab))

    # TF documentos
    docs_tf = {
        doc["id"]: compute_tf_fn(doc["tokens"], vocab)
        for doc in processed_docs
    }

    # TF consulta
    q_tf = compute_tf_fn(q_tokens, vocab)

    # IDF global
    all_token_lists = [doc["tokens"] for doc in processed_docs]
    all_token_lists.append(q_tokens)
    idf = compute_idf_fn(all_token_lists, vocab)

    # TF-IDF documentos
    docs_tfidf = {
        doc_id: compute_tfidf_fn(tf, vocab, idf)
        for doc_id, tf in docs_tf.items()
    }

    # TF-IDF consulta
    q_tfidf = compute_tfidf_fn(q_tf, vocab, idf)

    # Vectorizar
    docs_vectors = {
        doc_id: vectorize_document_fn(tfidf, vocab)
        for doc_id, tfidf in docs_tfidf.items()
    }
    q_vector = vectorize_document_fn(q_tfidf, vocab)

    # Similitud
    ranking = {
        doc_id: cosine_similarity_fn(q_vector, vec)
        for doc_id, vec in docs_vectors.items()
    }

    # Ordenar resultados
    ranking = dict(sorted(ranking.items(), key = lambda x: x[1], reverse = True))

    return {
        "query_processed": q_tokens,
        "vocabulary": vocab,
        "ranking": ranking
    }