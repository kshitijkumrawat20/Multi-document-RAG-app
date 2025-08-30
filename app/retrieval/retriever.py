from app.schemas.request_models import ClauseHit

class Retriever:
    def __init__(self, pinecone_index, query = None, metadata = None, namespace=None):
        self.pinecone_index = pinecone_index
        self.query = query
        self.metadata = metadata
        self.namespace = namespace


    def retrieval_from_pinecone_vectoreStore(self, top_k= 3):
        """
        Retrieve the top matching chunks from Pinecone.
        
        Args:
            pinecone_index: Your Pinecone index object.
            embedding: The vector embedding of the query.
            top_k: How many chunks to retrieve.
            filter_meta: Optional metadata filter dict.
        
        Returns:
            List of documents stored in pinecone store.
        """
        res = self.pinecone_index.query(
            vector= self.query,
            top_k =top_k ,
            include_metadata = True, 
            include_values = False, 
            filter = self.metadata,
            namespace = self.namespace
            )
        # hits= []
        # for match in res['matches']:
        #     hits.append(ClauseHit(
        #         doc_id=match['metadata']['doc_id'],
        #         page=match['metadata'].get('page', -1),
        #         chunk_id=match['metadata'].get('chunk_id', ''),
        #         text=match['metadata']['text'],
        #         metadata=match['metadata'],
        #         score=match['score']
        #     ))
        # return hits
        return res
    