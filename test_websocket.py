import time

def tail_log_file(log_path):
    """Continuously read new lines from a log file as they are added."""
    with open(log_path, 'r') as file:
        file.seek(0, 2)
        while True:
            line = file.readline()
            if not line:
                time.sleep(0.1)
                continue
            print("Log:", line.strip())

if __name__ == "__main__":
    # Path to the serial.log file (adjust path if necessary)
    log_path = "C:\\OctoPrint\\basedir\\5000\\logs\\serial.log"
    tail_log_file(log_path)
