import sys
import subprocess

try:
    import waitress
except ImportError:
    print("Waitress not found. Installing waitress package...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "waitress"])
    import waitress

from wsgi import app

if __name__ == '__main__':
    print("==================================================================")
    print(" Image Complexity Index (ICI) Generator Web Server Launching...")
    print(" Running in PRODUCTION mode via Waitress WSGI server")
    print(" Access Web UI at: http://127.0.0.1:5000")
    print("==================================================================")
    waitress.serve(app, host='0.0.0.0', port=5000)
