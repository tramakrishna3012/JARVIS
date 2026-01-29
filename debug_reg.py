import urllib.request
import json
import urllib.error

url = 'https://jarvis-backend-phi.vercel.app/api/auth/register'
data = {
    'email': 'debug_py_3@example.com',
    'password': 'Password123!',
    'full_name': 'Debug User'
}
headers = {
    'Content-Type': 'application/json',
    'Origin': 'https://jarvis-nine-rose.vercel.app'
}

req = urllib.request.Request(
    url, 
    data=json.dumps(data).encode('utf-8'), 
    headers=headers
)

try:
    with urllib.request.urlopen(req) as response:
        print(response.read().decode())
except urllib.error.HTTPError as e:
    print(f"HTTP {e.code}")
    print(e.read().decode())
except Exception as e:
    print(f"Error: {e}")
