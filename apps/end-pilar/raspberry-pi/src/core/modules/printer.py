from escpos.printer import Usb
import usb.core # To check for library presence

class PrinterCore:
    def __init__(self, vendor_id=0x04b8, product_id=0x0202):
        self.vendor_id = vendor_id
        self.product_id = product_id
        self.device = None

    def connect(self):
        """Attempts to establish a USB connection with dependency checks."""
        try:
            # Check if pyusb can actually see the hardware first
            dev = usb.core.find(idVendor=self.vendor_id, idProduct=self.product_id)
            if dev is None:
                print(f"[PrinterCore] Device {hex(self.vendor_id)} not found. Check cable/power.")
                return False

            if not self.device:
                self.device = Usb(self.vendor_id, self.product_id)
            return True
        except Exception as e:
            print(f"[PrinterCore] USB Library or Connection Error: {e}")
            return False

    def write(self, text: str, cut: bool = True):
        if self.connect():
            try:
                self.device.text(text)
                if cut:
                    self.device.cut()
                return True
            except Exception as e:
                print(f"[PrinterCore] Write error: {e}")
        return False

    def close(self):
        if self.device:
            try:
                self.device.close()
            except:
                pass
            self.device = None