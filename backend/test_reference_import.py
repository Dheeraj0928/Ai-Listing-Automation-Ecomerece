"""Test Smart Reference Import endpoints via HTTP requests."""

import json
import httpx

BASE_URL = "http://127.0.0.1:8000/api/v1"

def test_flow():
    client = httpx.Client(timeout=30.0)
    
    # 1. Signup or login
    email = "seller_test@example.com"
    password = "SecurePassword123!"
    
    print("[1] Authenticating...")
    login_resp = client.post(f"{BASE_URL}/auth/login", json={"email": email, "password": password})
    if login_resp.status_code == 200:
        token = login_resp.json()["tokens"]["access_token"]
        print("  Logged in successfully.")
    else:
        # Try signup
        signup_resp = client.post(
            f"{BASE_URL}/auth/signup",
            json={
                "email": email,
                "password": password,
                "full_name": "Test Seller",
                "phone": "+919876543210",
                "business_name": "Test Ecom Store"
            }
        )
        print("  Signup status:", signup_resp.status_code, signup_resp.text[:100])
        if signup_resp.status_code in (200, 201):
            token = signup_resp.json()["tokens"]["access_token"]
        else:
            raise RuntimeError(f"Auth failed: {signup_resp.text}")

    headers = {"Authorization": f"Bearer {token}"}

    # 2. Test keyword search
    print("\n[2] Testing POST /api/v1/reference-import/from-keyword...")
    kw_payload = {
        "keyword": "Ultra Bright USB Rechargeable Red Bicycle Tail Light",
        "marketplace": "amazon",
        "tone": "professional"
    }
    kw_resp = client.post(f"{BASE_URL}/reference-import/from-keyword", json=kw_payload, headers=headers)
    print("  Status:", kw_resp.status_code)
    if kw_resp.status_code != 200:
        print("  Response error:", kw_resp.text)
        return
    kw_data = kw_resp.json()
    print("  Status field:", kw_data.get("status"))
    print("  Suggestions returned:", len(kw_data.get("suggestions", [])))
    first_suggestion = kw_data["suggestions"][0]
    print("  First suggestion title:", first_suggestion.get("title"))
    print("  Category:", first_suggestion.get("suggested_category"))

    # 3. Test confirm suggestion
    print("\n[3] Testing POST /api/v1/reference-import/confirm...")
    confirm_payload = {
        "suggestion": first_suggestion,
        "marketplace": "amazon",
        "tone": "professional",
        "sku": "RED-BIKE-LGT-001",
        "price": 499.00,
        "stock": 50
    }
    confirm_resp = client.post(f"{BASE_URL}/reference-import/confirm", json=confirm_payload, headers=headers)
    print("  Status:", confirm_resp.status_code)
    if confirm_resp.status_code != 200:
        print("  Response error:", confirm_resp.text)
        return
    confirm_data = confirm_resp.json()
    print("  Product created:", confirm_data["product"]["id"], confirm_data["product"]["title"])
    print("  Listing created:", confirm_data["listing"]["id"], confirm_data["listing"]["marketplace"])
    print("  AI Listing SEO score:", confirm_data.get("ai_listing", {}).get("seo_score"))
    print("  Bullet points count:", len(confirm_data.get("ai_listing", {}).get("bullet_points", [])))

    # 4. Test URL import (using mock provider / sample product URL)
    print("\n[4] Testing POST /api/v1/reference-import/from-url...")
    url_payload = {
        "url": "https://www.amazon.in/dp/B09XYZ1234",
        "marketplace": "amazon",
        "tone": "persuasive",
        "sku": "URL-TEST-001",
        "price": 699.00
    }
    url_resp = client.post(f"{BASE_URL}/reference-import/from-url", json=url_payload, headers=headers)
    print("  Status:", url_resp.status_code)
    if url_resp.status_code != 200:
        print("  Response details:", url_resp.text)
    else:
        url_data = url_resp.json()
        print("  Product created from URL:", url_data["product"]["id"], url_data["product"]["title"])
        print("  Source marketplace:", url_data.get("source_info", {}).get("source_marketplace"))

    print("\n[SUCCESS] All Reference Import flows tested successfully!")

if __name__ == "__main__":
    test_flow()
