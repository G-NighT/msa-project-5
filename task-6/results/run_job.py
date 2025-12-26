import requests

url = "http://localhost:8080/api/jobs/import-products"
resp = requests.post(url, timeout=60)

print("Status:", resp.status_code)
print(resp.text)
