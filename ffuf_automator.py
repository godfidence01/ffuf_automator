import os
import subprocess
import threading
import time
import sys
import readline  # Enables line-editing and history features

# Global control flags
pause_flag = threading.Event()
pause_flag.set()
stop_flag = False

def control_listener():
    """Listens for user input to control the tool."""
    global stop_flag
    while True:
        print("\nControls:\n1. Press 'q' to quit.\n2. Press 'c' to skip the current wordlist.\n3. Press 'p' to pause.\n4. Press 'r' to resume.\n")
        choice = input("Enter your choice: ").strip().lower()

        if choice == 'q':
            print("\nQuitting the tool...")
            stop_flag = True
            pause_flag.set()  # Unpause if paused
            break
        elif choice == 'c':
            print("\nSkipping the current wordlist...")
            pause_flag.set()  # Unpause if paused
            stop_flag = False
            break
        elif choice == 'p':
            print("\nPausing the current scan...")
            pause_flag.clear()
        elif choice == 'r':
            print("\nResuming the current scan...")
            pause_flag.set()
        else:
            print("\nInvalid input. Try again.")

def run_ffuf():
    global stop_flag
    print("FFUF Automation Script\n")
    print("This script uses ffuf to run wordlists for fuzzing a target URL.")
    print("Make sure ffuf is installed and available in your system's PATH.\n")

    try:
        # Get user inputs with line editing
        input_path = input("Enter the path to a single wordlist or a folder containing wordlists: ").strip()
        
        if os.path.isfile(input_path):  # If it's a single file
            wordlists = [input_path]
        elif os.path.isdir(input_path):  # If it's a folder
            wordlists = [os.path.join(input_path, f) for f in os.listdir(input_path) if os.path.isfile(os.path.join(input_path, f))]
            if not wordlists:
                raise ValueError(f"No wordlists found in the folder '{input_path}'.")
        else:
            raise ValueError(f"The path '{input_path}' is neither a valid file nor a folder.")

        target_url = input("Enter the target URL (use 'FUZZ' in place of the fuzzing point): ").strip()
        if "FUZZ" not in target_url:
            raise ValueError("The target URL must contain 'FUZZ' as the placeholder for fuzzing.")

        additional_params = input("Enter any additional ffuf parameters (or press Enter to skip): ").strip()

        print(f"\nFound {len(wordlists)} wordlist(s). Starting fuzzing...\n")

        # Start control listener in a separate thread
        control_thread = threading.Thread(target=control_listener, daemon=True)
        control_thread.start()

        # Run ffuf for each wordlist
        for wordlist in wordlists:
            if stop_flag:
                print("\nStopping the tool as requested by the user.")
                break

            print(f"[+] Running ffuf with wordlist: {wordlist}")
            command = f"ffuf -u {target_url} -w {wordlist} {additional_params}"
            print(f"Executing: {command}\n")

            # Execute the ffuf command
            process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            while process.poll() is None:
                time.sleep(0.1)  # Check for user input periodically
                if not pause_flag.is_set():
                    print("\n[Paused] Press 'r' to resume.")
                    while not pause_flag.is_set():
                        time.sleep(0.5)

                if stop_flag:
                    process.terminate()
                    print(f"\nStopped the current wordlist: {wordlist}")
                    break

            if stop_flag:
                continue

            stdout, stderr = process.communicate()
            if process.returncode != 0:
                print(f"Error: ffuf failed for wordlist {wordlist}. Error:\n{stderr.decode()}\n")
            else:
                print(stdout.decode())

        print("\nFuzzing complete!")

    except ValueError as ve:
        print(f"Input Error: {ve}")
        print("\nExiting script. Please correct the input and try again.")
        sys.exit(1)

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        print("\nExiting script. Please check your input and system setup.")
        sys.exit(1)

if __name__ == "__main__":
    run_ffuf()
 
