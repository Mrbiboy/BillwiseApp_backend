import uuid

def test_bills_stats(client):
    account_id = str(uuid.uuid4())
    bills = [
        {"account_id": account_id, "merchant": "A", "amount": 100, "status": "pending"},
        {"account_id": account_id, "merchant": "B", "amount": 50, "status": "paid"},
        {"account_id": account_id, "merchant": "C", "amount": 30, "status": "overdue"},
    ]

    for bill in bills:
        client.post("/api/bills", json=bill)

    response = client.get(f"/api/bills/account/{account_id}/stats")
    assert response.status_code == 200
    stats = response.json()
    assert stats["total_bills"] == 3
    assert stats["total_amount"] == 180
    assert stats["pending_amount"] == 100
    assert stats["overdue_amount"] == 30
    assert stats["paid_amount"] == 50
