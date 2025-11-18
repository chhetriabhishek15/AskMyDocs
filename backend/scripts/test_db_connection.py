"""
Database connection test script.

Works both inside Docker containers and locally:
- Inside Docker: Uses 'postgres' hostname (Docker service name)
- Locally: Uses 'localhost' hostname

Usage:
    # From host (local)
    cd backend
    uv run python scripts/test_db_connection.py

    # Inside Docker container
    docker exec -it tiramai-backend python scripts/test_db_connection.py
"""
import asyncio
import os
import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

import asyncpg

def get_db_host():
    """Determine database host based on environment."""
    # Check if running inside Docker
    # Docker sets these environment variables
    if os.path.exists("/.dockerenv") or os.environ.get("DOCKER_CONTAINER"):
        return "postgres"  # Docker service name
    else:
        return "localhost"  # Local development

async def test():
    """Test database connection."""
    host = get_db_host()
    user = os.environ.get("POSTGRES_USER", "tiramai_user")
    password = os.environ.get("POSTGRES_PASSWORD", "tiramai_password")
    database = os.environ.get("POSTGRES_DB", "tiramai_db")
    port = int(os.environ.get("POSTGRES_PORT", "5432"))
    
    print("Testing PostgreSQL connection...")
    print(f"  Environment: {'Docker' if host == 'postgres' else 'Local'}")
    print(f"  Host: {host}")
    print(f"  Port: {port}")
    print(f"  Database: {database}")
    print(f"  User: {user}")
    print()
    
    try:
        conn = await asyncpg.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            port=port
        )
        
        # Test query
        version = await conn.fetchval("SELECT version();")
        db_name = await conn.fetchval("SELECT current_database();")
        
        print("✓ Connected successfully!")
        print(f"  PostgreSQL: {version.split(',')[0]}")
        print(f"  Database: {db_name}")
        
        # Check pgvector extension
        has_pgvector = await conn.fetchval(
            "SELECT EXISTS(SELECT 1 FROM pg_extension WHERE extname = 'vector');"
        )
        if has_pgvector:
            pgv_version = await conn.fetchval(
                "SELECT extversion FROM pg_extension WHERE extname = 'vector';"
            )
            print(f"  pgvector: v{pgv_version}")
        else:
            print("  pgvector: NOT installed")
        
        await conn.close()
        print("\n✓ Connection test passed!")
        return True
        
    except Exception as e:
        print(f"\n✗ Connection failed: {type(e).__name__}: {e}")
        print("\nTroubleshooting:")
        if host == "postgres":
            print("  - Ensure you're running inside Docker container")
            print("  - Check that postgres service is running: docker-compose ps")
        else:
            print("  - Ensure PostgreSQL container is running: docker-compose ps")
            print("  - Check port mapping: docker-compose ps postgres")
        print("  - Verify credentials in .env files")
        return False

if __name__ == "__main__":
    success = asyncio.run(test())
    sys.exit(0 if success else 1)
