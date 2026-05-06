from escpos.printer import Usb
from PIL import Image
import usb.core
import os
import time

class PrinterCore:
    def __init__(self, vendor_id=0x04b8, product_id=0x0202):
        self.vendor_id = vendor_id
        self.product_id = product_id
        self.device = None
        self.logo_path = "/home/mathijsdl/Documents/Projects/eindopdracht-dev-4-speed-challenge/apps/end-pilar/raspberry-pi/src/assets/speed-challenge_logo.png"

    def connect(self):
        try:
            dev = usb.core.find(idVendor=self.vendor_id, idProduct=self.product_id)
            if dev is None: return False
            
            try:
                if dev.is_kernel_driver_active(0):
                    dev.detach_kernel_driver(0)
            except: pass

            if self.device is None:
                # We use a profile, but now 'default'
                self.device = Usb(self.vendor_id, self.product_id, timeout=60)
            return True
        except Exception as e:
            print(f"[PrinterCore] Connect error: {e}")
            return False

    def write(self, text: str, cut: bool = True):
        if not self.connect(): return False
        try:
            # 1. RESET: Remove any previous settings and start fresh
            self.device._raw(b'\x1b\x40') 
            time.sleep(0.2)
            
            self.device.set(align='center')

            # 2. Print logo
            if os.path.exists(self.logo_path):
                try:
                    img = Image.open(self.logo_path).convert('1')
                    
                    target_width = 250
                    w_percent = (target_width / float(img.size[0]))
                    h_size = int((float(img.size[1]) * float(w_percent)))
                    img = img.resize((target_width, h_size), Image.Resampling.NEAREST)
                    
                    self.device.image(img, impl='graphics')
                    time.sleep(0.8)
                except Exception as img_e:
                    print(f"[PrinterCore] Logo error: {img_e}")

            # 3. Print text
            self.device.text(f"\n{text}\n\n")

            # 4. Cut the paper
            if cut:
                time.sleep(0.5)
                self.device.cut()
            return True
        except Exception as e:
            print(f"[PrinterCore] Printfout: {e}")
            self.device = None
            return False