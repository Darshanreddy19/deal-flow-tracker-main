"""
Centralized Qdrant Cloud client wrapper.
Provides upsert, search, and collection management for the multi-agent graph.
"""

import os
import uuid
from typing import List, Dict, Any, Optional
from langchain_text_splitters import RecursiveCharacterTextSplitter

from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.http import models as qdrant_models

from brain import LLM
from config import MODEL_NAME, QDRANT_COLLECTION_NAME, dim_size

load_dotenv()

# ---------------------------------------------------------------------------
# Singleton client
# ---------------------------------------------------------------------------
_client: Optional[QdrantClient] = None


def get_client() -> QdrantClient:
    """Return a re-usable Qdrant Cloud client."""
    global _client
    if _client is None:
        _client = QdrantClient(
            url=os.getenv("QDRANT_URL"),
            api_key=os.getenv("QDRANT_API_KEY"),
        )
    return _client


# ---------------------------------------------------------------------------
# Collection helpers
# ---------------------------------------------------------------------------
def ensure_collection(
    collection_name: str = QDRANT_COLLECTION_NAME,
    dim: int = dim_size,
) -> None:
    """Create the collection if it does not already exist."""
    client = get_client()
    if not client.collection_exists(collection_name):
        client.create_collection(
            collection_name=collection_name,
            vectors_config=qdrant_models.VectorParams(
                size=dim, distance=qdrant_models.Distance.COSINE
            ),
        )
        print(f"[qdrant] Created collection '{collection_name}' (dim={dim})")
        
        # Create payload index for deal_id to enable filtering
        client.create_payload_index(
            collection_name=collection_name,
            field_name="deal_id",
            field_schema=qdrant_models.PayloadSchemaType.KEYWORD,
        )
        print(f"[qdrant] Created payload index for 'deal_id'")
    else:
        print(f"[qdrant] Collection '{collection_name}' already exists")


# ---------------------------------------------------------------------------
# Embedding helper
# ---------------------------------------------------------------------------
def _get_embedding_model():
    """Return the embedding model from the LLM factory."""
    llm_factory = LLM(provider=MODEL_NAME)
    return llm_factory.get_embedding_model()


# ---------------------------------------------------------------------------
# Upsert
# ---------------------------------------------------------------------------
def upsert_text(
    text: str,
    metadata: Dict[str, Any],
    collection_name: str = QDRANT_COLLECTION_NAME,
) -> List[str]: # Note: Now returns a List of strings (point IDs)
    """
    Split *text* into chunks, embed each, and store them in Qdrant 
    with *metadata* as the payload. Returns generated point ids.
    """
    embedding_model = _get_embedding_model()

    # Split text to safely stay under GigaChat's 4096 token limit
    # 4000 characters is roughly 1000-1500 tokens.
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=2000, 
        chunk_overlap=400
    )
    chunks = text_splitter.split_text(text)
    
    point_ids = []
    points_to_upsert = []

    for i, chunk in enumerate(chunks):
        vector = embedding_model.embed_query(chunk)

        # Auto-create / verify collection dimension using the first chunk's vector
        if i == 0:
            ensure_collection(collection_name, len(vector))

        point_id = str(uuid.uuid4())
        point_ids.append(point_id)
        
        # Keep track of the specific chunk text and its index
        chunk_metadata = {**metadata, "text": chunk, "chunk_index": i}

        points_to_upsert.append(
            qdrant_models.PointStruct(
                id=point_id,
                vector=vector,
                payload=chunk_metadata,
            )
        )

    # Batch upsert all chunks for this text
    if points_to_upsert:
        get_client().upsert(
            collection_name=collection_name,
            points=points_to_upsert,
        )

    return point_ids


# ---------------------------------------------------------------------------
# Search
# ---------------------------------------------------------------------------
def search_similar(
    query: str,
    collection_name: str = QDRANT_COLLECTION_NAME,
    k: int = 5,
    filter_conditions: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    """
    Embed *query*, run a similarity search in Qdrant,
    and return a list of {score, payload} dicts.
    """
    client = get_client()
    if not client.collection_exists(collection_name):
        return []

    # ---------------------------------------------------------
    # FIX: Truncate query to avoid GigaChat 4096 token limit
    # 1 token is ~3-4 characters. 12,000 chars is a very safe 
    # boundary. We take the *last* 12,000 characters.
    # ---------------------------------------------------------
    safe_query = query[-12000:] if len(query) > 12000 else query

    embedding_model = _get_embedding_model()
    
    # Embed the truncated, safe query
    vector = embedding_model.embed_query(safe_query)

    # Build optional Qdrant filter
    qdrant_filter = None
    if filter_conditions:
        must_conditions = []
        for key, value in filter_conditions.items():
            if isinstance(value, list):
                must_conditions.append(
                    qdrant_models.FieldCondition(
                        key=key,
                        match=qdrant_models.MatchAny(any=value),
                    )
                )
            else:
                must_conditions.append(
                    qdrant_models.FieldCondition(
                        key=key,
                        match=qdrant_models.MatchValue(value=value),
                    )
                )
        qdrant_filter = qdrant_models.Filter(must=must_conditions)

    results = client.query_points(
        collection_name=collection_name,
        query=vector,
        limit=k,
        query_filter=qdrant_filter,
    )

    return [
        {"score": hit.score, "payload": hit.payload}
        for hit in results.points
    ]
