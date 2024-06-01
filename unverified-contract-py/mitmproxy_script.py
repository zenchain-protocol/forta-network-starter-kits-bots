from mitmproxy import http

def request(flow: http.HTTPFlow) -> None:
    print(f"\n=== Request ===")
    print(f"URL: {flow.request.url}")
    print(f"Headers: {flow.request.headers}")
    print(f"Content: {flow.request.text}")

def response(flow: http.HTTPFlow) -> None:
    print(f"\n=== Response ===")
    print(f"Status Code: {flow.response.status_code}")
    print(f"Headers: {flow.response.headers}")
    print(f"Content: {flow.response.text}")
