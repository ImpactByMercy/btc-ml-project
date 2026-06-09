"""
Frontend HTTP server for serving static files
"""
import http.server
import socketserver
import os
from pathlib import Path

PORT = 8000
DIRECTORY = Path(__file__).parent

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DIRECTORY), **kwargs)
    
    def end_headers(self):
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        super().end_headers()

if __name__ == '__main__':
    os.chdir(DIRECTORY)
    with socketserver.TCPServer(('', PORT), MyHTTPRequestHandler) as httpd:
        print(f"Frontend server running at http://localhost:{PORT}")
        print("Press Ctrl+C to stop")
        httpd.serve_forever()
