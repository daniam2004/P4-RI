
def build_vocabulary(list_of_tokens_lists: list) -> list:
    if not isinstance(list_of_tokens_lists, list):
        return []
    
    vocabulary = set()

    for tokens in list_of_tokens_lists:
        if isinstance(tokens, list):
            for token in tokens:
                vocabulary.add(token)

    return sorted(list(vocabulary))

def compute_tf(tokens: list, vocabulary:list) -> dict:
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