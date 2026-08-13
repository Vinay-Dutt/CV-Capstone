import subprocess
import sys
import time
import threading
import os

def run_flask():
    print("[Flask] Starting local Flask server on http://127.0.0.1:5000 ...")
    # Run production server using Waitress
    subprocess.call([sys.executable, "run_production.py"])

def run_tunnel():
    print("[Tunnel] Starting secure public tunnel on port 5000...")
    # Use npx --yes to download and run localtunnel without user prompt
    cmd = ["npx.cmd", "--yes", "localtunnel", "--port", "5000"]
    if os.name != 'nt':
        cmd[0] = 'npx'
        
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    
    print("\n[Tunnel] Establishing connection... Please wait.")
    url_found = False
    for line in proc.stdout:
        line_str = line.strip()
        if "your url is:" in line_str.lower():
            url = line_str.split("is:")[-1].strip()
            print("\n==================================================================")
            print("  MOBILE ACCESS PUBLIC URL (ANY NETWORK):")
            print(f"  {url}")
            print("==================================================================")
            print("  Open this link on your phone (using mobile data or any Wi-Fi).")
            print("  Press Ctrl+C in this terminal to stop the server.")
            print("==================================================================\n")
            url_found = True
        elif not url_found:
            # Print package fetch output if any
            if line_str:
                print(f"[Tunnel] {line_str}")

if __name__ == "__main__":
    try:
        # Start Flask server thread
        flask_thread = threading.Thread(target=run_flask)
        flask_thread.daemon = True
        flask_thread.start()
        
        # Give Flask server 3 seconds to spin up and bind to port 5000
        time.sleep(3)
        
        # Start Tunnel
        run_tunnel()
        
        # Keep main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[System] Exiting and shutting down tunnel and server...")
        sys.exit(0)
