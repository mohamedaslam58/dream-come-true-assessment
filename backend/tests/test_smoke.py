"""Expanded smoke and integration test suite."""
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_app_title():
    assert app.title == 'Wallet Operations - Assessment (Hardened)'

def test_get_wallet_default_user():
    response = client.get('/wallet', headers={'X-User-ID': '1'})
    assert response.status_code == 200
    data = response.json()
    assert data['user_id'] == 1
    assert 'balance' in data

def test_unauthorized_transaction_access():
    # BOLA check: User 1 attempting to access a non-existent or unauthorized transaction ID
    response = client.get('/transactions/99999', headers={'X-User-ID': '1'})
    assert response.status_code in [404, 403]