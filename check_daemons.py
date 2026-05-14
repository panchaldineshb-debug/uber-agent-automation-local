import subprocess

def get_running_processes():
    try:
        # Use pgrep to find processes by name
        result = subprocess.run(['pgrep', '-f', 'uber-agent-automation-local'], capture_output=True, text=True, check=True)
        return result.stdout.strip().split('\n')
    except subprocess.CalledProcessError:
        return []

def main():
    processes = get_running_processes()
    if processes:
        print("Running background daemons for uber-agent-automation-local:")
        for pid in processes:
            print(f"PID: {pid}")
    else:
        print("No background daemons found for uber-agent-automation-local.")

if __name__ == '__main__':
    main()
