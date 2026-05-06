from src.core.modules.printer import PrinterCore
from src.data.facts import Facts
from datetime import datetime

class PrinterManager:
    """
    Defines the receipt layout and processes the speed data.
    """
    def __init__(self):
        self.printer = PrinterCore()

    def print_speed_result(self, elapsed_time: float):
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

        receipt += "Did you know?\n\n"
        receipt += f"{Facts.get_random_fact()}\n"

        success = self.printer.write(receipt)
        if success:
            print(f"[Printer] Ticket printed for time: {elapsed_time:.3f}s")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.printer.close()