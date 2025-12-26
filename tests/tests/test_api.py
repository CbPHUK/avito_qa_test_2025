import pytest
import requests

BASE_URL = "https://qa-internship.avito.com"

@pytest.fixture(scope="module")
def seller_id():
    return 999999  # уникальный, чтобы не пересекаться

@pytest.fixture
def created_ad(seller_id):
    payload = {
        "name": "Test Ad from Grok",
        "price": 1000,
        "sellerId": seller_id,
        "statistics": {"contacts": 0, "likes": 0, "viewCount": 0}
    }
    response = requests.post(f"{BASE_URL}/api/1/item", json=payload)
    assert response.status_code == 200
    ad_id = response.json()["id"]
    yield ad_id
    # cleanup
    requests.delete(f"{BASE_URL}/api/2/item/{ad_id}")

def test_create_ad(seller_id):
    payload = {
        "name": "Test Ad",
        "price": 500,
        "sellerId": seller_id,
        "statistics": {"contacts": 0, "likes": 0, "viewCount": 0}
    }
    response = requests.post(f"{BASE_URL}/api/1/item", json=payload)
    assert response.status_code == 200
    assert "id" in response.json()

def test_get_ad(created_ad):
    response = requests.get(f"{BASE_URL}/api/1/item/{created_ad}")
    assert response.status_code == 200
    data = response.json()[0]
    assert data["id"] == created_ad

def test_get_ads_by_seller(seller_id, created_ad):
    response = requests.get(f"{BASE_URL}/api/1/{seller_id}/item")
    assert response.status_code == 200
    ads = response.json()
    assert any(ad["id"] == created_ad for ad in ads)

def test_get_statistics(created_ad):
    response = requests.get(f"{BASE_URL}/api/1/statistic/{created_ad}")
    assert response.status_code == 200
    stats = response.json()[0]
    assert "likes" in stats
    assert "viewCount" in stats
    assert "contacts" in stats

def test_delete_ad(created_ad):
    response = requests.delete(f"{BASE_URL}/api/2/item/{created_ad}")
    assert response.status_code == 200

# Негативные
def test_get_non_existent_ad():
    response = requests.get(f"{BASE_URL}/api/1/item/nonexistent123")
    assert response.status_code == 404
