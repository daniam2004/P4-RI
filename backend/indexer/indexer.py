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
