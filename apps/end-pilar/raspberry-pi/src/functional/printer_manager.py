from datetime import datetime
from src.core.modules.printer import PrinterCore

class PrinterManager:
    """
    Defines the receipt layout and processes the speed data.
    """
    def __init__(self):
        self.printer = PrinterCore()

    def print_speed_result(self, elapsed_time: float): # Rename this to match main.py
        """
        Formats a receipt based on the provided elapsed time.
        """
        # Define the layout
        receipt = "\n"
        receipt += "================================\n"
        receipt += "       SPEED CHALLENGE         \n"
        receipt += "================================\n\n"
        receipt += f"  TIME:  {elapsed_time:.3f} seconds\n"
        receipt += "\n--------------------------------\n"
        receipt += f"  DATE: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
        receipt += "================================\n\n\n"

        success = self.printer.write(receipt)
        if success:
            print(f"[Printer] Ticket printed for time: {elapsed_time:.3f}s")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.printer.close()