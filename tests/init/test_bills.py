import uuid

def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_create_and_get_bill(client):
    bill_data = {
        "account_id": str(uuid.uuid4()),
        "merchant": "Unit Test Store",
        "amount": 99.99,
        "status": "pending"
    }
    # CREATE
    response = client.post("/api/bills", json=bill_data)
    assert response.status_code == 201
    bill_id = response.json()["bill_id"]

    # READ
    response = client.get(f"/api/bills/{bill_id}")
    assert response.status_code == 200
    assert response.json()["merchant"] == "Unit Test Store"

def test_update_and_delete_bill(client):
    bill_data = {
        "account_id": str(uuid.uuid4()),
        "merchant": "Old Store",
        "amount": 20,
        "status": "pending"
    }
    # CREATE
    response = client.post("/api/bills", json=bill_data)
    bill_id = response.json()["bill_id"]

    # UPDATE
    update_data = {"merchant": "New Store", "status": "paid"}
    response = client.patch(f"/api/bills/{bill_id}", json=update_data)
    assert response.status_code == 200
    assert response.json()["merchant"] == "New Store"

    # DELETE
    response = client.delete(f"/api/bills/{bill_id}")
    assert response.status_code == 204
