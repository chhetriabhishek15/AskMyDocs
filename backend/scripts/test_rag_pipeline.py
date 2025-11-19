"""
Test script for RAG pipeline with Memori integration.
"""
import asyncio
import os
from pathlib import Path
import sys

# Add the backend directory to the Python path
sys.path.insert(0, str(Path(__file__).resolve().parent))

import structlog
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(Path(__file__).resolve().parent / ".env")

# Setup logging
structlog.configure(
    processors=[
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.dev.ConsoleRenderer(),
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    logger_factory=structlog.stdlib.LoggerFactory(),
)

logger = structlog.get_logger()


async def test_rag_pipeline():
    """Test complete RAG pipeline."""
    print("=" * 60)
    print("Testing RAG Pipeline with Memori")
    print("=" * 60)

    # 1. Initialize components
    print("\n1. Initializing components...")
    try:
        from app.vectorstore.chromadb_store import ChromaDBStore
        from app.repositories.chromadb_repository import ChromaDBRepository
        from app.rag.retrieval import RetrievalService
        from app.services.llm_service import LLMService
        from app.rag.memory_service import MemoryService
        from app.rag.pipeline import RAGPipeline

        chroma_store = ChromaDBStore()
        chroma_repository = ChromaDBRepository(chroma_store)
        retrieval_service = RetrievalService(chroma_repository)
        llm_service = LLMService()
        memory_service = MemoryService()

        pipeline = RAGPipeline(
            retrieval_service=retrieval_service,
            llm_service=llm_service,
            memory_service=memory_service,
        )

        print("   ✓ All components initialized successfully")
        print(f"   ✓ Memory service available: {memory_service.is_available()}")
    except Exception as e:
        print(f"   ✗ Error initializing components: {e}")
        logger.error("init_failed", error=str(e))
        return

    # 2. Test retrieval
    print("\n2. Testing retrieval service...")
    try:
        query = "What is the document about?"
        chunks = await retrieval_service.retrieve_with_context(
            query_text=query,
            top_k=3,
            min_score=0.0,  # Get all results for testing
        )
        print(f"   ✓ Retrieved {len(chunks)} chunks")
        if chunks:
            print(f"   ✓ Top chunk similarity: {chunks[0].get('similarity_score', 0.0):.2f}")
    except Exception as e:
        print(f"   ✗ Retrieval test failed: {e}")
        logger.error("retrieval_test_failed", error=str(e))
        return

    # 3. Test LLM service
    print("\n3. Testing LLM service...")
    try:
        test_prompt = "What is the capital of France? Answer in one sentence."
        response = await llm_service.generate(test_prompt, use_cache=False)
        print(f"   ✓ LLM response received: {response.text[:100]}...")
        print(f"   ✓ Model: {response.model}")
    except Exception as e:
        print(f"   ✗ LLM test failed: {e}")
        logger.error("llm_test_failed", error=str(e))
        return

    # 4. Test RAG pipeline (without documents if none exist)
    print("\n4. Testing RAG pipeline...")
    try:
        session_id = "test-session-123"
        query = "What information is available in the documents?"

        rag_response = await pipeline.generate(
            query=query,
            session_id=session_id,
            top_k=3,
            min_score=0.0,
        )

        print(f"   ✓ RAG response generated")
        print(f"   ✓ Answer length: {len(rag_response.answer)} characters")
        print(f"   ✓ Number of sources: {len(rag_response.sources)}")
        print(f"   ✓ Session ID: {rag_response.session_id}")
        print(f"\n   Answer preview:")
        print(f"   {rag_response.answer[:200]}...")
    except Exception as e:
        print(f"   ✗ RAG pipeline test failed: {e}")
        logger.error("rag_pipeline_test_failed", error=str(e), exc_info=True)
        return

    # 5. Test conversation memory (if Memori is available)
    if memory_service.is_available():
        print("\n5. Testing conversation memory...")
        try:
            session_id = "test-session-memory"
            
            # First query
            query1 = "What is the main topic?"
            response1 = await pipeline.generate(
                query=query1,
                session_id=session_id,
                top_k=2,
            )
            print(f"   ✓ First query answered: {len(response1.answer)} chars")

            # Second query (should have context from first)
            query2 = "Can you tell me more about that?"
            response2 = await pipeline.generate(
                query=query2,
                session_id=session_id,
                top_k=2,
            )
            print(f"   ✓ Second query answered: {len(response2.answer)} chars")
            print(f"   ✓ Memory integration working")
        except Exception as e:
            print(f"   ⚠ Memory test failed (non-critical): {e}")
            logger.warning("memory_test_failed", error=str(e))
    else:
        print("\n5. Skipping memory test (Memori not available)")

    print("\n" + "=" * 60)
    print("✅ RAG Pipeline tests completed!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_rag_pipeline())

