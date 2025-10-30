import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.db.models.orders import Order

client_sync = TestClient(app)

@pytest.mark.asyncio
class TestOrdersAPI:
    async def test_create_order_success(self, client, mock_exchange, db_session):
        payload = {"user_id": 123, "amount": 99.9}

        response = await client.post("/api/orders", json=payload)

        assert response.status_code == 201
        data = response.json()
        assert data["order_id"] > 0
        assert data["message"].startswith("Order created")

        # Verify database state
        order = await db_session.get(Order, data["order_id"])
        assert order is not None
        assert order.user_id == payload["user_id"]
        assert float(order.amount) == payload["amount"]
        assert order.status == "pending"

        # Verify event publication
        mock_exchange.publish.assert_awaited_once()

    async def test_create_order_invalid_amount(self, client):
        payload = {"user_id": 123, "amount": -10}
        response = await client.post("/api/orders", json=payload)
        assert response.status_code == 422

    async def test_create_order_zero_amount(self, client):
        payload = {"user_id": 123, "amount": 0}
        response = await client.post("/api/orders", json=payload)
        assert response.status_code == 422

    async def test_create_order_missing_fields(self, client):
        response = await client.post("/api/orders", json={})
        assert response.status_code == 422
        errors = response.json()["detail"]
        # Validation errors include the field location in 'loc'
        assert any("user_id" in str(err["loc"]) for err in errors)
        assert any("amount" in str(err["loc"]) for err in errors)

    async def test_get_order(self, client, sample_order):
        response = await client.get(f"/api/orders/{sample_order.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_order.id
        assert data["user_id"] == sample_order.user_id
        assert float(data["amount"]) == float(sample_order.amount)
        assert data["status"] == sample_order.status

    async def test_get_nonexistent_order(self, client):
        response = await client.get("/api/orders/99999")
        assert response.status_code == 404

    async def test_list_orders(self, client, sample_order):
        response = await client.get("/api/orders")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        order = data[0]
        assert order["id"] == sample_order.id
        assert order["user_id"] == sample_order.user_id

    def test_validation_handler_jsonable(self):
        response = client_sync.post("/api/orders", json={"user_id": 1, "amount": -5})
        assert response.status_code == 422
        assert "detail" in response.json()
