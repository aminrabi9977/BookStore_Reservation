
import pytest

from app.models.reservation import Reservation, ReservationStatus
from app.models.customer import Customer, SubscriptionModel
from datetime import datetime, timedelta

@pytest.mark.asyncio
async def test_create_reservation(test_session, test_client):
    
    customer = Customer(
        user_id=1,
        subscription_modele=SubscriptionModel.PLUS,
        wallet_balance=100000
    )
    test_session.add(customer)
    await test_session.commit()


    reservation_data = {
        "book_id": 1,
        "start_time": datetime.now() + timedelta(days=1),
        "end_time": datetime.now() + timedelta(days=8)
    }
    
    response = test_client.post(
        "/api/v1/reservations/",
        json=reservation_data,
        headers={"Authorization": f"Bearer {test_token}"}
    )
    
    assert response.status_code == 201
    assert response.json()["status"] == ReservationStatus.PENDING.value

@pytest.mark.asyncio
async def test_reservation_queue(test_session, test_client):
    # Test queue functionality
    # Create multiple reservations and verify queue ordering
    pass