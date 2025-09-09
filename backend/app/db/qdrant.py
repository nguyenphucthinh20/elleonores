from qdrant_client import QdrantClient, AsyncQdrantClient
from llama_index.core import VectorStoreIndex, StorageContext
from llama_index.vector_stores.qdrant import QdrantVectorStore
from app.core.config import settings
from llama_index.core import Settings
from neo4j_graphrag.retrievers import QdrantNeo4jRetriever
from neo4j import GraphDatabase
import json


class VectorSearchQdant:
    def __init__(self):
        self.client = QdrantClient(settings.QDRANT_URL)
        self.aclient = AsyncQdrantClient(settings.QDRANT_URL)
        self.driver = GraphDatabase.driver(
            settings.NEO4J_URI,
            auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
        )

    def create_vector_index(self, documents, collection_name):
        vector_store = QdrantVectorStore(
            client=self.client,
            aclient=self.aclient,
            collection_name=collection_name,
            enable_hybrid=True,
            fastembed_sparse_model="Qdrant/bm25",
        )

        storage_context = StorageContext.from_defaults(vector_store=vector_store)

        index = VectorStoreIndex.from_documents(
            documents,
            storage_context=storage_context,
        )

        return index

    def retrieve_from_qdrant_neo4j(self, 
                                   query_text: str,
                                   number_candidate: int
                                   ):
        try:
            query_vector = Settings.embed_model.get_text_embedding(query_text)
            print(f"Query text: '{query_text}'")
            print(f"Query vector dimension: {len(query_vector)}")
        except Exception as e:
            print(f"Error generating embedding: {e}")
            return []

        retriever = QdrantNeo4jRetriever(
            driver=self.driver,
            client=self.client,
            collection_name=settings.QDRANT_COLLECTION_NAME,
            id_property_external="talent_id",  
            id_property_neo4j="talent_id",      
            using="text-dense"                 
        )

        try:
            results = retriever.get_search_results(
                query_vector=query_vector,
                top_k=number_candidate
            )
            
            print(f"QdrantNeo4jRetriever results type: {type(results)}")
            print(f"QdrantNeo4jRetriever results: {results}")
            
            if hasattr(results, 'records') and results.records:
                print(f"Found {len(results.records)} records")
                for i, record in enumerate(results.records):
                    print(f"Record {i}: {record}")
                return results.records
            else:
                print("No records found in QdrantNeo4jRetriever results")
                return []
                
        except Exception as e:
            print(f"QdrantNeo4jRetriever error: {e}")

    def get_resume_text_by_talent_id(self, talent_id: str) -> str | None:
        try:
            hits = self.client.scroll(
                collection_name=settings.QDRANT_COLLECTION_NAME,
                scroll_filter={
                    "must": [
                        {"key": "talent_id", "match": {"value": talent_id}}
                    ]
                },
                limit=1
            )

            if not hits or not hits[0]:
                return None

            point = hits[0][0]
            node_content = point.payload.get("_node_content")
            if not node_content:
                return None

            node = json.loads(node_content)
            return node.get("text")

        except Exception as e:
            print(f"Error while fetching from Qdrant: {e}")
            return None
        
vector_search = VectorSearchQdant()