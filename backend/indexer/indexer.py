import math
from collections import Counter

def build_vocabulary(list_of_tokens_lists: list) -> list:
    if not isinstance(list_of_tokens_lists, list):
        return []
    
    vocabulary = set()

    for tokens in list_of_tokens_lists:
        if isinstance(tokens, list):
            for token in tokens:
                vocabulary.add(token)

    return sorted(list(vocabulary))

def compute_tf(tokens: list, vocabulary: list) -> dict:
    if not isinstance(tokens, list) or not isinstance(vocabulary, list):
        return {}
    
    tf = {}
    total_tokens = len(tokens)

    if total_tokens == 0:
        return {term: 0 for term in vocabulary}
    
    for term in vocabulary:
        count = tokens.count(term)
        tf[term] = count / total_tokens
    
    return tf

def compute_idf(list_of_tokens_lists: list, vocabulary: list) -> dict:
    """
    IDF = log(N / (1 + df)) + 1
    """
    if not isinstance(list_of_tokens_lists, list) or not isinstance(vocabulary, list):
        return {}

    N = len(list_of_tokens_lists)

    # Inicializamos df = 0 para cada término del vocabulario
    df = {term: 0 for term in vocabulary}

    # Contar cuántos documentos contienen cada término
    for tokens in list_of_tokens_lists:
        if not isinstance(tokens, list):
            continue
        unique_tokens = set(tokens)
        for token in unique_tokens:
            if token in df:
                df[token] += 1

    # Calcular IDF
    idf = {}
    for term in vocabulary:
        term_df = df.get(term, 0)
        idf_val = math.log(N / (1 + term_df)) + 1
        idf[term] = idf_val

    return idf

def compute_tfidf(tokens: list, vocabulary: list, idf: dict) -> dict:
    if not isinstance(tokens, list) or not isinstance(vocabulary, list) or not isinstance(idf, dict):
        return {}

    total_tokens = len(tokens)
    tfidf = {}

    counts = Counter(tokens)

    for term in vocabulary:
        # TF normalizado
        if total_tokens > 0:
            tf = counts.get(term, 0) / total_tokens
        else:
            tf = 0

        # IDF del término
        idf_val = idf.get(term, 0)

        # TF-IDF
        tfidf[term] = tf * idf_val

    return tfidf

def select_relevant_terms(tfidf: dict, k: int = 5) -> list:
    if not isinstance(tfidf, dict):
        return []

    sorted_terms = sorted(tfidf.items(), key = lambda x: x[1], reverse = True)

    top_terms = [term for term, score in sorted_terms[:k]]

    return top_terms

def build_inverted_index(documents: list) -> dict:
    if not isinstance(documents, list):
        return {}
    
    inverted = {}

    for doc in documents:
        if not isinstance(doc, dict):
            continue

        doc_id = doc.get("id")
        tfidf_dict = doc.get("tfidf")

        if not isinstance(doc_id, str) or not isinstance(tfidf_dict, dict):
            continue

        for term, weight in tfidf_dict.items():
            if term not in inverted:
                inverted[term] = {}
            inverted[term][doc_id] = weight
    
    return inverted

def vectorize_document(tfidf: dict, vocabulary: list) -> list:
    if not isinstance(tfidf, dict) or not isinstance(vocabulary, list):
        return []
    
    vector = []

    for term in vocabulary:
        value = tfidf.get(term, 0.0)
        vector.append(value)
    
    return vector

def cosine_similarity(vec1: list, vec2: list) -> float:
    if not isinstance(vec1, list) or not isinstance(vec2, list):
        return 0.0
    if len(vec1) != len(vec2):
        return 0.0
    
    dot = sum(a * b for a, b in zip(vec1, vec2))

    norm1 = math.sqrt(sum(a * a for a in vec1))
    norm2 = math.sqrt(sum(b * b for b in vec2))

    if norm1 == 0 or norm2 == 0:
        return 0.0
    
    return dot / (norm1 * norm2)

