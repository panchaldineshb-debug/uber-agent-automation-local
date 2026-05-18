import subprocess

def get_running_processes():
    try:
        # Use pgrep to find processes by name
        result = subprocess.run(['pgrep', '-f', 'uber-agent-automation-local'], capture_output=True, text=True, check=True)
        return result.stdout.strip().split('\n')
    except subprocess.CalledProcessError:
        return []

def run_tests():
    try:
        # Run all tests using pytest
        result = subprocess.run(['pytest'], capture_output=True, text=True, check=False)
        if result.returncode != 0:
            print("Some tests failed:")
            print(result.stderr)
        else:
            print("All tests passed.")
    except Exception as e:
        print(f"An error occurred while running tests: {e}")

def main():
    processes = get_running_processes()
    if processes:
        print("Running background daemons for uber-agent-automation-local:")
        for pid in processes:
            print(f"PID: {pid}")
    else:
        print("No background daemons found for uber-agent-automation-local.")

    # Run tests after checking for running daemons
    run_tests()

if __name__ == '__main__':
    main()
