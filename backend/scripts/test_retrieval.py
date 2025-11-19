"""
Test script for retrieval service.
"""
import asyncio
from pathlib import Path

from app.vectorstore.chromadb_store import ChromaDBStore
from app.repositories.chromadb_repository import ChromaDBRepository
from app.rag.retrieval import RetrievalService


async def test_retrieval():
    """Test retrieval service."""
    print("=" * 60)
    print("Testing Retrieval Service")
    print("=" * 60)

    # Initialize services
    print("\n1. Initializing ChromaDB store and repository...")
    chroma_store = ChromaDBStore()
    chromadb_repository = ChromaDBRepository(chroma_store)
    retrieval_service = RetrievalService(chromadb_repository)

    # Test query
    query = "What is the main topic of the document?"
    print(f"\n2. Testing retrieval with query: '{query}'")
    
    try:
        # Retrieve chunks with very low threshold to see all results
        chunks = await retrieval_service.retrieve(
            query_text=query,
            top_k=5,
            min_score=0.0,  # No filtering - see all results
        )

        print(f"\n3. Retrieved {len(chunks)} chunks:")
        print("-" * 60)
        
        for i, chunk in enumerate(chunks, 1):
            print(f"\nChunk {i}:")
            print(f"  ID: {chunk.chunk_id}")
            print(f"  Document ID: {chunk.document_id}")
            print(f"  Similarity: {chunk.similarity_score:.4f}")
            print(f"  Text preview: {chunk.text[:150]}...")
            if chunk.metadata:
                print(f"  Metadata: {chunk.metadata}")

        # Test retrieval with context
        print("\n" + "=" * 60)
        print("4. Testing retrieval with formatted context:")
        print("-" * 60)
        
        formatted_results = await retrieval_service.retrieve_with_context(
            query_text=query,
            top_k=3,
            include_preview=True,
            preview_length=100,
        )

        for i, result in enumerate(formatted_results, 1):
            print(f"\nResult {i}:")
            print(f"  Document: {result['document_filename']}")
            print(f"  Similarity: {result['similarity_score']:.4f}")
            print(f"  Preview: {result['preview']}")

        print("\n" + "=" * 60)
        print("✅ Retrieval test completed successfully!")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ Error during retrieval: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_retrieval())

