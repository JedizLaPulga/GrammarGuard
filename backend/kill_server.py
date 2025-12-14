import os
import subprocess

def kill_port(port):
    try:
        cmd = f"netstat -ano | findstr :{port}"
        try:
            result = subprocess.check_output(cmd, shell=True).decode()
        except subprocess.CalledProcessError:
            print(f"No process found on port {port}")
            return

        lines = result.strip().split('\n')
        for line in lines:
            parts = line.split()
            if parts:
                pid = parts[-1]
                print(f"killing PID {pid}")
                os.system(f"taskkill /PID {pid} /F")
    except Exception as e:
        print(f"Error killing port {port}: {e}")

if __name__ == "__main__":
    kill_port(14300)
