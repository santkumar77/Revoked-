from http.server import BaseHTTPRequestHandler
import urllib.parse
import json
import requests
import os

DEFAULT_APP_ID = "100067"
BASE_URL = "https://100067.connect.garena.com/oauth/logout"
USER_AGENT = "GarenaMSDK/4.0.41(DN2101 ;Android 13;en;HK;app 2.123.1 2019117599;)"

def revoke_token(access_token, refresh_token=None, app_id=DEFAULT_APP_ID):
    params = {
        "access_token": access_token.strip(),
        "app_id": app_id.strip()
    }
    if refresh_token and refresh_token.strip():
        params["refresh_token"] = refresh_token.strip()

    headers = {
        "User-Agent": USER_AGENT,
        "Connection": "Keep-Alive",
        "Accept-Encoding": "gzip"
    }

    try:
        response = requests.get(BASE_URL, params=params, headers=headers, timeout=10)
        return {
            "success": response.status_code == 200,
            "status_code": response.status_code,
            "body": response.text
        }
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "status_code": 0,
            "body": str(e)
        }

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        query_params = urllib.parse.parse_qs(parsed_path.query)
        
        if '/revoke' in self.path:
            access_token = query_params.get('access_token', [''])[0]
            refresh_token = query_params.get('refresh_token', [''])[0]
            app_id = query_params.get('app_id', [DEFAULT_APP_ID])[0]
            
            if not access_token:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": "access_token is required"}).encode())
                return
            
            result = revoke_token(access_token, refresh_token or None, app_id)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(result, indent=2).encode())
            
        elif self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            html = """
            <html>
            <head><title>Garena Token Revoker</title></head>
            <body style="font-family:Arial;max-width:600px;margin:50px auto;padding:20px;">
                <h2>Garena Token Revoker</h2>
                <p>Use endpoint: <code>/revoke?access_token=TOKEN&refresh_token=OPTIONAL&app_id=100067</code></p>
                <p>Returns JSON with revoke status.</p>
            </body>
            </html>
            """
            self.wfile.write(html.encode())
        else:
            self.send_response(404)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Not found. Use /revoke endpoint"}).encode())

    def log_message(self, format, *args):
        pass

app = handler