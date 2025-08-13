from app.schemas.request_models import ClauseHit


def retrieval_from_pinecone_vectoreStore(pinecone_index, embeddings, top_k= 3, filter_meta = None):
    """
    Retrieve the top matching chunks from Pinecone.
    
    Args:
        pinecone_index: Your Pinecone index object.
        embedding: The vector embedding of the query.
        top_k: How many chunks to retrieve.
        filter_meta: Optional metadata filter dict.
    
    Returns:
        List of ClauseHit objects (lightweight container for chunk info).
    """
    res = pinecone_index.query(
        vector= embeddings,
        top_k =top_k ,
        include_metadata = True, 
        include_values = False, 
        filter = filter_meta 
        )
    hits= []
    for match in res['matches']:
        hits.append(ClauseHit(
            doc_id=match['metadata']['doc_id'],
            page=match['metadata'].get('page', -1),
            chunk_id=match['metadata'].get('chunk_id', ''),
            text=match['metadata']['text'],
            metadata=match['metadata'],
            score=match['score']
        ))
    return hits