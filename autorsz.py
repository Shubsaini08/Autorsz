import os
import subprocess
import time

# Input file containing Bitcoin addresses
address_file = "/mnt/g/heart/database/btc5.txt"
# Log file to track checked addresses
log_file = "rsz.log"
# File to save keys and associated addresses where private keys are found
found_file = "foundRSZ.txt"

def get_checked_addresses():
    """Read the log file to get a list of already checked addresses."""
    if os.path.exists(log_file):
        with open(log_file, "r") as f:
            return set(line.strip() for line in f if line.strip())
    return set()

def save_checked_address(address):
    """Append an address to the log file."""
    with open(log_file, "a") as f:
        f.write(f"{address}\n")

def save_found_key(address, key):
    """Save the found private key and associated address."""
    with open(found_file, "a") as f:
        f.write(f"Address: {address}, PrivateKey: {key}\n")

def main():
    # Load all Bitcoin addresses from the file
    if not os.path.exists(address_file):
        print(f"Address file not found: {address_file}")
        return

    with open(address_file, "r") as f:
        addresses = [line.strip() for line in f if line.strip()]

    if not addresses:
        print("No addresses found in the file.")
        return

    # Get the list of already checked addresses
    checked_addresses = get_checked_addresses()

    for address in addresses:
        if address in checked_addresses:
            print(f"Skipping already checked address: {address}")
            continue

        print(f"Processing address: {address}")

        # Run the command for the current address
        cmd = ["python3", "rsz_rdiff_scan.py", "-a", address]
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        while True:
            output = process.stdout.readline()
            if output == "" and process.poll() is not None:
                break
            if output:
                print(output.strip())

                # Check for Privatekey FOUND
                if "Privatekey FOUND:" in output:
                    print("\n!!! Private key found !!!")
                    # Extract the key and save it along with the address
                    key = output.split("Privatekey FOUND:")[1].strip()
                    save_found_key(address, key)
                    # Terminate the program after finding the key
                    return

        _, errors = process.communicate()
        if errors:
            print(f"Error for address {address}: {errors.strip()}")

        # Mark the address as checked
        save_checked_address(address)
        print(f"Completed processing for address: {address}\n")

        # Wait a bit to avoid overloading the system
        time.sleep(1)

if __name__ == "__main__":
    main()

