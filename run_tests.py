import subprocess

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

if __name__ == '__main__':
    run_tests()
