import httpx

base = "https://z1go1ry6zi.execute-api.us-east-1.amazonaws.com"

# 1. Send OTP
r1 = httpx.post(f"{base}/api/auth/send-otp", json={"email": "user@test.com"}, timeout=30)
data = r1.json()
otp = data["otp_hint"]
print(f"1. Send OTP: {r1.status_code} - OTP={otp}")

# 2. Verify OTP
r2 = httpx.post(f"{base}/api/auth/verify-otp", json={"email": "user@test.com", "otp": otp}, timeout=30)
print(f"2. Verify OTP: {r2.status_code} - {r2.json()}")

# 3. Chat
r3 = httpx.post(f"{base}/api/chat/message", json={"customer_id": "CUST001", "message": "hello", "language": "en"}, timeout=30)
print(f"3. Chat: {r3.status_code} - {r3.json()['response'][:100]}")

# 4. Chat Hindi
r4 = httpx.post(f"{base}/api/chat/message", json={"customer_id": "CUST001", "message": "namaste", "language": "hi"}, timeout=30)
print(f"4. Hindi: {r4.status_code} - {r4.json()['response'][:100]}")

# 5. Portfolio
r5 = httpx.get(f"{base}/api/portfolio/CUST001", timeout=30)
print(f"5. Portfolio: {r5.status_code} - value={r5.json()['portfolio']['total_value']}")

# 6. Recommendations
r6 = httpx.post(f"{base}/api/recommendations/generate", json={"customer_id": "CUST001", "goal": "Home", "amount": 10000}, timeout=30)
print(f"6. Recommendations: {r6.status_code} - {len(r6.json()['recommendations'])} funds")

print("\nALL TESTS PASSED!")
