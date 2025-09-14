# from app.schemas.request_models import ClauseHit

class Retriever:
    def __init__(self, pinecone_index, query = None, metadata = None, namespace=None, vectore_store = None, llm = None):
        self.pinecone_index = pinecone_index
        self.query = query
        self.metadata = metadata
        self.namespace = namespace
        self.vector_store = vectore_store
        self.llm = llm  
        self.retriever = self.vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 5,"namespace": self.namespace, "filter": self.metadata}
        )


    def retrieval_from_pinecone_vectoreStore(self):
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
        # res = self.pinecone_index.query(
        #     vector= self.query,
        #     top_k =top_k ,
        #     include_metadata = True, 
        #     include_values = False, 
        #     filter = self.metadata,
        #     namespace = self.namespace
        #     )
        
        # Process the results into the expected format
        # class ClauseHit:
        #     def __init__(self, doc_id, page, chunk_id, text, metadata, score):
        #         self.doc_id = doc_id
        #         self.page = page
        #         self.chunk_id = chunk_id
        #         self.text = text
        #         self.metadata = metadata
        #         self.score = score
        
        # hits = []
        # for match in res['matches']:
        #     hits.append(ClauseHit(
        #         doc_id=match['metadata'].get('doc_id', ''),
        #         page=match['metadata'].get('page_no', -1),  # Use page_no instead of page
        #         chunk_id=match['metadata'].get('chunk_id', ''),
        #         text=match['metadata'].get('text', match.get('text', '')),
        #         metadata=match['metadata'],
        #         score=match['score']
        #     ))
        # return hits
        results = self.retriever.invoke(self.query)
        for doc in results:
            print(f"printing Doc content : {doc.page_content}")
        return results
