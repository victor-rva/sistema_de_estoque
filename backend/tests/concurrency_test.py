import threading
import requests

API_URL = "http://localhost:5000/orders"  # ajuste se sua app estiver em outra porta
PRODUCT_ID = 1
QUANTITY_PER_REQ = 1
N_THREADS = 20

results = []

def worker(i):
    try:
        r = requests.post(API_URL, json={"productId": PRODUCT_ID, "quantity": QUANTITY_PER_REQ}, timeout=5)
        try:
            payload = r.json()
        except Exception:
            payload = r.text
        results.append((i, r.status_code, payload))
    except Exception as e:
        results.append((i, "ERR", str(e)))

threads = []
for i in range(N_THREADS):
    t = threading.Thread(target=worker, args=(i,))
    threads.append(t)
    t.start()

for t in threads:
    t.join()

success = [r for r in results if r[1] == 201]
conflict = [r for r in results if r[1] == 409]
others = [r for r in results if r[1] not in (201,409)]

print("Total requests:", len(results))
print("Success:", len(success))
print("Conflict (estoque insuficiente):", len(conflict))
print("Other:", len(others))
for r in results:
    print(r)
