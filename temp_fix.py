#!/usr/bin/env python3
import re

# Read the file
with open('qrew/Qrew_message_handlers.py', 'r') as f:
    content = f.read()

# Replace stop_flask_server
stop_pattern = r'def stop_flask_server.*?""".*?""".*?global http_server.*?srv = http_server.*?http_server = None.*?if srv and not srv\.closed:.*?print\("🛑  Stopping REW-API server …"\).*?srv\.stop\(timeout\)'
stop_replacement = '''def stop_flask_server(timeout: float = 2.0):
    """
    Ask gevent's WSGIServer to shut down and wait (≤ *timeout* s).
    Safe to call more than once.
    """
    # Use server_manager instead of global http_server
    server_manager.stop(timeout)'''
content = re.sub(stop_pattern, stop_replacement, content, flags=re.DOTALL)

# Replace run_flask_server
run_pattern = r'def run_flask_server\(\):.*?import logging.*?global http_server.*?app\.config\["ENV"\] = "production".*?app\.config\["DEBUG"\] = False.*?http_server = WSGIServer\(.*?"127\.0\.0\.1", 5555.*?app,.*?log=logging\.getLogger\("http_server"\),.*?error_log=logging\.getLogger\("http_server_error"\),.*?\).*?print\("✅  REW-API server listening on http://127\.0\.0\.1:5555"\).*?http_server\.serve_forever\(\)'
run_replacement = '''def run_flask_server():
    import logging

    # Production
    app.config["ENV"] = "production"
    app.config["DEBUG"] = False

    server_manager.http_server = WSGIServer(
        ("127.0.0.1", 5555),
        app,
        log=logging.getLogger("http_server"),
        error_log=logging.getLogger("http_server_error"),
    )
    print("✅  REW-API server listening on http://127.0.0.1:5555")
    server_manager.http_server.serve_forever()'''
content = re.sub(run_pattern, run_replacement, content, flags=re.DOTALL)

# Write back the file
with open('qrew/Qrew_message_handlers.py', 'w') as f:
    f.write(content)

print("File successfully updated")
