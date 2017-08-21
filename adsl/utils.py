import requests

def get_real_ip():
    for i in range(3):
        try:
            # httpbin_url = "http://httpbin.org/ip"
            httpbin_url = "http://101.200.158.162:7000/ip"
            resp = requests.get(httpbin_url, timeout=10)
            data = resp.json()
        except requests.exceptions.RequestException:
            continue
        return data['origin']
