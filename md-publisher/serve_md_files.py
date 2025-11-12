import os
import socket
import mimetypes
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import unquote
import markdown

# 📁 Folder where your .md files and assets are stored
MARKDOWN_DIR = "./md-publisher/markdown_files"
ENTRYPOINT = "/sebot"

# ✅ Dark-themed CSS styling
CSS_STYLE = """
<style>
body {
    max-width: 900px;
    margin: auto;
    padding: 2em;
    font-family: "Segoe UI", sans-serif;
    background-color: #1e1e1e;
    color: #d4d4d4;
}
a {
    color: #4fc1ff;
    text-decoration: none;
}
a:hover {
    text-decoration: underline;
}
pre, code {
    background-color: #2d2d2d;
    color: #c0c0c0;
    padding: 0.4em;
    border-radius: 4px;
    line-height:1.5em;
    font-family: "Courier New", monospace;
}
pre {
    overflow-x: auto;
}
h1, h2, h3 {
    border-bottom: 1px solid #555;
    padding-bottom: 0.3em;
}
hr {
    border-color: #444;
}
</style>
"""

def list_md_files():
    return [f for f in os.listdir(MARKDOWN_DIR) if f.endswith('.md')]

class MarkdownHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = unquote(self.path)

        if path == ENTRYPOINT or path == ENTRYPOINT + '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()

            md_files = list_md_files()
            html = "<h1>SeBot Markdown Server</h1><ul>"
            for fname in md_files:
                html += f'<li><a href="{ENTRYPOINT}/{fname}">{fname}</a></li>'
            html += "</ul>"

            full_page = f"<html><head>{CSS_STYLE}<meta charset='utf-8'></head><body>{html}</body></html>"
            self.wfile.write(full_page.encode('utf-8'))

        elif path.startswith(ENTRYPOINT + '/') and path.endswith('.md'):
            fname = path[len(ENTRYPOINT) + 1:]
            file_path = os.path.join(MARKDOWN_DIR, fname)

            if os.path.isfile(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    md_content = f.read()

                html = markdown.markdown(md_content, extensions=['fenced_code', 'tables'])

                self.send_response(200)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.end_headers()

                base_url = os.path.dirname(path)
                full_page = f"""
                <html><head>
                    {CSS_STYLE}
                    <meta charset='utf-8'>
                    <base href="{base_url}/">
                </head><body>
                    <a href="{ENTRYPOINT}">&larr; Back</a><hr>
                    {html}
                </body></html>"""

                self.wfile.write(full_page.encode('utf-8'))
            else:
                self.send_error(404, "Markdown file not found.")

        else:
            requested_file = os.path.join(MARKDOWN_DIR, path[len(ENTRYPOINT) + 1:])
            if os.path.isfile(requested_file):
                mime_type, _ = mimetypes.guess_type(requested_file)
                self.send_response(200)
                self.send_header('Content-type', mime_type or 'application/octet-stream')
                self.end_headers()
                with open(requested_file, 'rb') as f:
                    self.wfile.write(f.read())
            else:
                self.send_error(404, "File not found.")

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("10.255.255.255", 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = "127.0.0.1"
    finally:
        s.close()
    return IP

def run(server_class=HTTPServer, handler_class=MarkdownHandler, port=8000):
    ip = get_local_ip()
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f"\n🌍 Local Markdown server running at:\n  http://{ip}:{port}{ENTRYPOINT}")
    print(f"📁 Serving from: {os.path.abspath(MARKDOWN_DIR)}\n")
    httpd.serve_forever()

if __name__ == '__main__':
    os.makedirs(MARKDOWN_DIR, exist_ok=True)
    run()
