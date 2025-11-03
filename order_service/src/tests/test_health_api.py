import pytest
from sqlalchemy import text

@pytest.mark.asyncio
class TestHealthAPI:
    async def test_health_endpoint(self, client):
        response = await client.get("/api/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

    async def test_health_check_with_db(self, client, db_session):
        """Test health check endpoint with database connection."""
        # First check the health endpoint
        response = await client.get("/api/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}
        
        # Verify database connection is working
        result = await db_session.execute(text("SELECT 1"))
        assert result.scalar() == 1

    async def test_health_check_with_rabbitmq(self, client, mock_exchange):
        """Test health check with RabbitMQ mock."""
        response = await client.get("/api/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}
        
        # Verify RabbitMQ mock is available
        assert mock_exchange is not None