#!/usr/bin/python
# require py-hidapi

import hid
from time import sleep

class ATENUsbSwitch(object):
    def __init__(self, vendor_id=1367, product_id=9223):
        self.vendor_id = vendor_id
        self.product_id = product_id
        self.device = None

    def __del__(self):
        self._close()

    def _open(self):
        self.device = hid.device()
        for dev in hid.enumerate(self.vendor_id, self.product_id):
            if dev["interface_number"] == 1:
                self.device.open_path(dev["path"])

    def _close(self):
        if self.device:
            self.device.close()

    def is_active(self):
        try:
            self._open()
            status = self.device.read(4)
            self._close()
        except ValueError as e:
            return False
        else:
            return (status[1] & 0x01)

    def is_locked(self):
        try:
            self._open()
            status = self.device.read(4)
            self._close()
        except ValueError as e:
            return False
        else:
            return (status[1] & 0x02)

    def switch(self, wait=True):
        self._open()
        self.device.write([0x02, 0x11])
        self._close()
        wait_for_active = wait
        while wait_for_active:
            sleep(3)
            try:
                if self.is_active():
                    wait_for_active = False
            except OSError as e:
                continue

    def lock(self):
        self._open()
        self.device.write([0x02, 0x11])
        self._close()

    def unlock(self):
        self._open()
        self.device.write([0x02, 0x20])
        self._close()

    def keep_locked(self):
        self._open()
        self.lock()
        while True:
            sleep(4)
            self.device.write([0x02, 0x40])
        self._close()


if __name__ == "__main__":
    usbsw = ATENUsbSwitch()
    if usbsw.is_active():
        print("Device already attached.")
    else:
        print("Switching device ...", end="", flush=True)
        usbsw.switch()
        if usbsw.is_active():
            print(" Done!")
