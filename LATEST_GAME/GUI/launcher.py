import subprocess
import paramiko
import time
import webbrowser
import signal
import sys

# Updated Configuration based on your exact paths
PIS = [
    {
        "host": "pi5-chess.local", 
        "path": "/home/pi/Downloads/PIGAME/Boardapp",
        "env": "/home/pi/chess-env/bin/activate"
    },
    {
        "host": "pi5-chess2.local", 
        "path": "/home/pi/Downloads/PIGAME2/Boardapp",
        "env": "/home/pi/chess-env/bin/activate"
    }
]
LOCAL_APP_PATH = "/Users/dylanboles/Downloads/Senior_Design/Design_Folder/_01_30_26_/NEW_PROJ/GUI"
LOCAL_URL = "http://127.0.0.1:5001/"

processes = []
ssh_connections = []

def cleanup(sig, frame):
    print("\n[Shutting Down] Killing all local and remote processes...")
    for p in processes:
        p.terminate()
    
    for ssh in ssh_connections:
        try:
            # Targeted kill for the pi_chess_server
            ssh.exec_command("pkill -f pi_chess_server.py")
            ssh.close()
        except:
            pass
    print("Cleanup complete.")
    sys.exit(0)

signal.signal(signal.SIGINT, cleanup)

def main():
    for pi in PIS:
        try:
            print(f"Connecting to {pi['host']}...")
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            # Note: This assumes you have SSH Keys set up. 
            # If not, add password='yourpassword' to ssh.connect
            ssh.connect(pi['host'], username='pi')
            
            # Kill any old instances first
            ssh.exec_command("pkill -f pi_chess_server.py")
            
            # The "One-Liner" Command:
            # 1. Source the env using absolute path
            # 2. CD into the folder
            # 3. Run the python script with nohup (background)
            cmd = f"source {pi['env']} && cd {pi['path']} && nohup python pi_chess_server.py > /dev/null 2>&1 &"
            
            # We use invoke_shell or exec_command with a bash prefix to ensure 'source' works
            ssh.exec_command(f"bash -c '{cmd}'")
            
            ssh_connections.append(ssh)
            print(f"✅ Started server on {pi['host']}")
        except Exception as e:
            print(f"❌ Failed to connect to {pi['host']}: {e}")

    # Start Local App
    print("Starting local GUI...")
    local_proc = subprocess.Popen(["python", "app.py"], cwd=LOCAL_APP_PATH)
    processes.append(local_proc)

    time.sleep(3)
    webbrowser.open_new_tab(LOCAL_URL)

    print("System active. Press Ctrl+C in this window to kill all servers.")
    while True:
        time.sleep(1)

if __name__ == "__main__":
    main()
