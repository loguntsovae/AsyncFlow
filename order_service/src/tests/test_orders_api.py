import pytest
from fastapi.testclient import TestClient
from src.main import app

client_sync = TestClient(app)


@pytest.mark.asyncio
async def test_create_order_success(client, mock_exchange):
    payload = {"user_id": 123, "amount": 99.9}

    response = await client.post("/api/orders", json=payload)

    assert response.status_code == 201
    data = response.json()
    assert data["order_id"] > 0
    assert data["message"].startswith("Order created")

    # проверяем, что публикация события была вызвана
    mock_exchange.publish.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_order_invalid_amount(client):
    payload = {"user_id": 123, "amount": -10}

    response = await client.post("/api/orders", json=payload)
    assert response.status_code == 422  # ошибка валидации


def test_validation_handler_jsonable():
    response = client_sync.post("/api/orders", json={"user_id": 1, "amount": -5})
    assert response.status_code == 422
    assert "detail" in response.json()
