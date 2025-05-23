def signal_handler(sig, frame, workers):
    print("Shutting down all markets...")
    for worker in workers:
        worker.terminate()
        worker.join()
    print("All markets stopped.")
    exit(0)

def create_shutdown_handler(workers):
    def shutdown(signum, frame):
        """Handles shutdown signals (e.g., Ctrl+C or system shutdown)."""
        print("\nShutting down all processes...")
        for p in workers:
            p.terminate()
            p.join()
        print("All processes stopped.")
        exit(0)
    return shutdown