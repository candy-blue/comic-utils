import json
import time
import urllib.request
import urllib.error
import urllib.parse
from typing import Optional, Dict, Any

class HttpClient:
    """ Resilient HTTP client with retry, timeout, rate-limiting and user-agent support """
    DEFAULT_TIMEOUT = 15
    DEFAULT_USER_AGENT = "ComicUtils/2.0 (Windows NT 10.0; Win64; x64) DesktopApp"

    def __init__(self, timeout: int = DEFAULT_TIMEOUT, user_agent: str = DEFAULT_USER_AGENT):
        self.timeout = timeout
        self.user_agent = user_agent

    def get(self, url: str, params: Optional[Dict[str, Any]] = None, 
            headers: Optional[Dict[str, str]] = None, max_retries: int = 3) -> bytes:
        if params:
            query = urllib.parse.urlencode(params)
            sep = "&" if "?" in url else "?"
            url = f"{url}{sep}{query}"

        req_headers = {"User-Agent": self.user_agent}
        if headers:
            req_headers.update(headers)

        req = urllib.request.Request(url, headers=req_headers, method="GET")
        return self._execute_request(req, max_retries)

    def post_json(self, url: str, data: Dict[str, Any], 
                  headers: Optional[Dict[str, str]] = None, max_retries: int = 3) -> bytes:
        json_bytes = json.dumps(data).encode("utf-8")
        req_headers = {
            "User-Agent": self.user_agent,
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        if headers:
            req_headers.update(headers)

        req = urllib.request.Request(url, data=json_bytes, headers=req_headers, method="POST")
        return self._execute_request(req, max_retries)

    def get_json(self, url: str, params: Optional[Dict[str, Any]] = None,
                 headers: Optional[Dict[str, str]] = None, max_retries: int = 3) -> Dict[str, Any]:
        data = self.get(url, params=params, headers=headers, max_retries=max_retries)
        return json.loads(data.decode("utf-8"))

    def post_graphql(self, url: str, query: str, variables: Optional[Dict[str, Any]] = None,
                      headers: Optional[Dict[str, str]] = None, max_retries: int = 3) -> Dict[str, Any]:
        payload = {"query": query}
        if variables:
            payload["variables"] = variables
        data = self.post_json(url, payload, headers=headers, max_retries=max_retries)
        return json.loads(data.decode("utf-8"))

    def _execute_request(self, req: urllib.request.Request, max_retries: int) -> bytes:
        last_err = None
        for attempt in range(max_retries):
            try:
                with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                    return resp.read()
            except urllib.error.HTTPError as e:
                last_err = e
                # Rate limited (429) -> check retry after or exponential backoff
                if e.code == 429:
                    retry_after = e.headers.get("Retry-After")
                    wait_time = float(retry_after) if retry_after else (2 ** (attempt + 1))
                    time.sleep(min(wait_time, 10.0))
                    continue
                elif e.code in (500, 502, 503, 504):
                    time.sleep(1.0 * (attempt + 1))
                    continue
                else:
                    # 4xx client errors, do not retry
                    raise RuntimeError(f"HTTP Error {e.code}: {e.reason}") from e
            except urllib.error.URLError as e:
                last_err = e
                time.sleep(1.0 * (attempt + 1))
            except Exception as e:
                last_err = e
                time.sleep(1.0 * (attempt + 1))

        raise RuntimeError(f"Network request failed after {max_retries} attempts: {last_err}")
