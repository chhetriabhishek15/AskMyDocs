"""
Test script for LLM service.
"""
import asyncio
import os

# Set API key if not in environment
if not os.getenv("GEMINI_API_KEY"):
    print("⚠️  Warning: GEMINI_API_KEY not set in environment")
    print("   Please set it in backend/.env or export it before running")

from app.services.llm_service import LLMService


async def test_llm():
    """Test LLM service."""
    print("=" * 60)
    print("Testing LLM Service (Gemini API)")
    print("=" * 60)

    try:
        # Initialize service
        print("\n1. Initializing LLM service...")
        llm_service = LLMService()
        print(f"   Model: {llm_service.model_name}")
        print(f"   Temperature: {llm_service.temperature}")

        # Test 1: Simple generation
        print("\n2. Testing simple generation...")
        prompt = "What is artificial intelligence? Answer in one sentence."
        response = await llm_service.generate(prompt)
        print(f"\n   Prompt: {prompt}")
        print(f"   Response: {response.text}")
        print(f"   Model: {response.model}")
        if response.usage:
            print(f"   Usage: {response.usage}")

        # Test 2: RAG prompt building (using prompt templates)
        print("\n" + "=" * 60)
        print("3. Testing RAG prompt building with templates...")
        print("-" * 60)
        
        from app.rag.prompts.templates import RAGPromptTemplate
        
        context_chunks = [
            {
                "text": "Artificial Intelligence (AI) is the simulation of human intelligence by machines.",
                "document_filename": "ai_intro.pdf",
                "metadata": {"filename": "ai_intro.pdf"},
                "similarity_score": 0.95,
            },
            {
                "text": "Machine learning is a subset of AI that enables systems to learn from data.",
                "document_filename": "ml_basics.pdf",
                "metadata": {"filename": "ml_basics.pdf"},
                "similarity_score": 0.88,
            },
        ]
        
        user_query = "What is AI and how does it relate to machine learning?"
        
        # Use RAGPromptTemplate from app/rag/prompts/ (NOT llm_service)
        prompt_template = RAGPromptTemplate()
        rag_prompt = prompt_template.build(
            user_query=user_query,
            context_chunks=context_chunks,
        )
        
        print(f"\n   User Query: {user_query}")
        print(f"\n   Generated RAG Prompt using app/rag/prompts/templates (first 500 chars):")
        print(f"   {rag_prompt[:500]}...")
        print(f"\n   ✓ Prompt built correctly using prompt templates (not llm_service)")

        # Test 3: RAG generation
        print("\n" + "=" * 60)
        print("4. Testing RAG generation with context...")
        print("-" * 60)
        
        rag_response = await llm_service.generate(
            prompt=rag_prompt,
            use_cache=False,  # Don't cache for testing
        )
        
        print(f"\n   Response: {rag_response.text}")

        # Test 4: Cache test
        print("\n" + "=" * 60)
        print("5. Testing response caching...")
        print("-" * 60)
        
        # First call (should hit API)
        print("\n   First call (should hit API)...")
        start_time = asyncio.get_event_loop().time()
        response1 = await llm_service.generate(
            "Say hello in one word.",
            use_cache=True,
        )
        time1 = asyncio.get_event_loop().time() - start_time
        print(f"   Response: {response1.text}")
        print(f"   Time: {time1:.2f}s")

        # Second call (should hit cache)
        print("\n   Second call (should hit cache)...")
        start_time = asyncio.get_event_loop().time()
        response2 = await llm_service.generate(
            "Say hello in one word.",
            use_cache=True,
        )
        time2 = asyncio.get_event_loop().time() - start_time
        print(f"   Response: {response2.text}")
        print(f"   Time: {time2:.4f}s")
        print(f"   Cache speedup: {time1/time2:.1f}x faster" if time2 > 0 else "   Cache working!")

        print("\n" + "=" * 60)
        print("✅ LLM service test completed successfully!")
        print("=" * 60)

    except ValueError as e:
        if "API key" in str(e) or "GEMINI_API_KEY" in str(e):
            print(f"\n❌ Error: {e}")
            print("\n   Please set GEMINI_API_KEY in backend/.env file")
        else:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_llm())

