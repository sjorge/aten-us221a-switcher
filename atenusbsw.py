#!/usr/local/bin/python3.7
# require py-hidapi

import sys
import hid
import argparse
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
    argp = argparse.ArgumentParser(description="ATEN USB Switch CLI")
    argp.add_argument("-a", "--is-active", dest="do_check", action="store_true", help="return 0 if we are the active host")
    argp.add_argument("-s", "--switch", dest="do_switch", action="store_true", help="switch ourselves to be the active host")
    argp.add_argument("--carp", dest="carp_mode", action="store", choices=["MASTER", "BACKUP"],
            help="cleam switch based on CARP VIP status")
    argp.add_argument("-v", "--verbose", dest="be_verbose", action="store_true", help="verbose console messages")
    args = argp.parse_args()

    if args.carp_mode:
        args.do_switch = True if args.carp_mode == "MASTER" else False
        args.do_check = True if args.carp_mode == "BACKUP" else False

    if args.do_check and args.do_switch and args.be_verbose:
        print("WARNING: both --is-active and --switch provided, ignoring --switch!", file=sys.stderr)

    if args.do_check:
        if usbsw.is_active():
            if args.be_verbose:
                print("This host is active.")
            sys.exit(0)
        else:
            if args.be_verbose:
                print("Another host is active.")
            sys.exit(1)
    elif args.do_switch:
        if not usbsw.is_active():
            if args.be_verbose:
                print("Switching this host to active...")
            usbsw.switch()
        if usbsw.is_active():
            if args.be_verbose:
                print("This host is now active.")
            sys.exit(0)
        else:
            if args.be_verbose:
                print("ERROR: Failed to switch!", file=sys.stderr)
            sys.exit(1)
    else:
        argp.print_help()
        sys.exit(2)
