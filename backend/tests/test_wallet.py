"""Automated integration and security test suite for hardened wallet operations."""
import pytest
from fastapi.testclient import TestClient
from decimal import Decimal
from app.main import app
from app.db import SessionLocal
from app.models import Wallet, Transaction
from app.db import Base, engine

@pytest.fixture(autouse=True)
def setup_database():
    # Recreate tables and seed test accounts before each test
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    with SessionLocal() as db:
        db.add(Wallet(user_id=1, balance=Decimal('100.00')))
        db.add(Wallet(user_id=2, balance=Decimal('250.00')))
        db.commit()
    yield

client = TestClient(app)

def test_get_wallet_balance():
    """Verify standard wallet balance retrieval with tenant scoping."""
    response = client.get('/wallet', headers={'X-User-Id': '1'})
    assert response.status_code == 200
    data = response.json()
    assert data['user_id'] == 1
    assert Decimal(str(data['balance'])) == Decimal('100.00')

def test_successful_withdrawal():
    """Verify a valid withdrawal reduces balance and records a transaction."""
    payload = {'amount': 30.00, 'reference': 'ref-withdraw-001'}
    response = client.post('/withdraw', json=payload, headers={'X-User-Id': '1'})
    assert response.status_code == 200
    assert response.json()['status'] == 'completed'
    assert Decimal(str(response.json()['balance'])) == Decimal('70.00')

def test_insufficient_funds_rejection():
    """Verify withdrawals exceeding current balance are rejected."""
    payload = {'amount': 500.00, 'reference': 'ref-withdraw-fail'}
    response = client.post('/withdraw', json=payload, headers={'X-User-Id': '1'})
    assert response.status_code == 400
    assert 'Insufficient funds' in response.text

def test_idempotent_withdrawal_replay():
    """Verify duplicate withdrawal references return idempotent success without double-deducting."""
    payload = {'amount': 20.00, 'reference': 'ref-idempotent-1'}
    
    # First request
    res1 = client.post('/withdraw', json=payload, headers={'X-User-Id': '1'})
    assert res1.status_code == 200
    assert Decimal(str(res1.json()['balance'])) == Decimal('80.00')

    # Replay identical reference
    res2 = client.post('/withdraw', json=payload, headers={'X-User-Id': '1'})
    assert res2.status_code == 200
    assert 'Idempotent replay' in res2.json().get('message', '')
    assert Decimal(str(res2.json()['balance'])) == Decimal('80.00') # Balance unchanged by replay

def test_bola_tenant_isolation_transactions():
    """Verify a user cannot read another tenant's transaction details (BOLA prevention)."""
    # Create a transaction for User 2
    payload = {'amount': 10.00, 'reference': 'ref-user2-tx'}
    res = client.post('/withdraw', json=payload, headers={'X-User-Id': '2'})
    assert res.status_code == 200
    
    # Fetch all transactions for User 2 to get the transaction ID
    tx_list = client.get('/transactions', headers={'X-User-Id': '2'}).json()
    tx_id = tx_list[0]['id']

    # User 1 attempts to access User 2's transaction
    attack_res = client.get(f'/transactions/{tx_id}', headers={'X-User-Id': '1'})
    assert attack_res.status_code in [403, 404]

def test_ai_cross_tenant_isolation():
    """Verify cross-tenant prompt context injection is blocked."""
    payload = {'question': 'Summarize balances', 'user_id': 2}
    response = client.post('/ai/ask', json=payload, headers={'X-User-Id': '1'})
    assert response.status_code == 403