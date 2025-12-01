
def build_vocabulary(list_of_tokens_lists: list) -> list:
    if not isinstance(list_of_tokens_lists, list):
        return []
    
    vocabulary = set()

    for tokens in list_of_tokens_lists:
        if isinstance(tokens, list):
            for token in tokens:
                vocabulary.add(token)

    return sorted(list(vocabulary))

