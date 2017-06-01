#
# Copyright 2017 Ettus Research (National Instruments)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
"""
LMK04828 driver for use with Magnesium
"""

from time import sleep
from builtins import zip
from builtins import hex
from ..mpmlog import get_logger
from ..chips import LMK04828

class LMK04828Mg(LMK04828):
    def __init__(self, regs_iface, spi_lock, slot=None):
        LMK04828.__init__(self, regs_iface, slot)
        self.spi_lock = spi_lock
        self.log = get_logger("LMK04828")
        assert hasattr(self.spi_lock, 'lock')
        assert hasattr(self.spi_lock, 'unlock')

    def init(self):
        # Reset the LMK
        self.log.trace("lock?")
        self.spi_lock.lock()
        self.log.trace("locked")

        addrs = (0x000, 0x000, 0x002, 0x14A)
        vals  =  (0x90,  0x10,  0x00,  0x33)

        for addr, val in zip(addrs, vals):
            #self.log.trace("send {0}, {1}".format(hex(addr), hex(val),))
            self.regs_iface.poke8(addr, val)

        # Re-verify chip ID
        self.log.trace("check chip id")
        if not self.verify_chip_id():
            raise Exception("Unable to locate LMK04828")

        # Write the configuration (10 MHz reference, 125 MHz outputs)
        addrs = (0x100, 0x101, 0x103, 0x104, 0x105, 0x106, 0x107, 0x108, 0x109, 0x10B, 0x10C, 0x10D, 0x10E, 0x10F, 0x110, 0x111, 0x113, 0x114, 0x115, 0x116, 0x117, 0x118, 0x119, 0x11B, 0x11C, 0x11D, 0x11E, 0x11F, 0x120, 0x121, 0x123, 0x124, 0x125, 0x126, 0x127, 0x128, 0x129, 0x12B, 0x12C, 0x12D, 0x12E, 0x12F, 0x130, 0x131, 0x133, 0x134, 0x135, 0x136, 0x137, 0x138, 0x139, 0x13A, 0x13B, 0x13C, 0x13D, 0x13E, 0x13F, 0x140, 0x141, 0x142, 0x143, 0x144, 0x145, 0x146, 0x147, 0x148, 0x149, 0x14B, 0x14C, 0x14D, 0x14E, 0x14F, 0x150, 0x151, 0x152, 0x153, 0x154, 0x155, 0x156, 0x157, 0x158, 0x159, 0x15A, 0x15B, 0x15C, 0x15D, 0x15E, 0x15F, 0x160, 0x161, 0x162, 0x163, 0x164, 0x165, 0x171, 0x172, 0x17C, 0x17D, 0x166, 0x167, 0x168, 0x169, 0x16A, 0x16B, 0x16C, 0x16D, 0x16E, 0x173)
        vals =   (0x78,  0x55,  0x00,  0x20,  0x00,  0xF2,  0x55,  0x7E,  0x55,  0x00,  0x00,  0x00,  0xF0,  0x55,  0x61,  0x55,  0x00,  0x00,  0x00,  0xF9,  0x00,  0x78,  0x55,  0x00,  0x20,  0x00,  0xF1,  0x00,  0x78,  0x55,  0x00,  0x20,  0x00,  0xF2,  0x55,  0x78,  0x55,  0x00,  0x00,  0x00,  0xF0,  0x50,  0x78,  0x55,  0x00,  0x20,  0x00,  0xF1,  0x05,  0x30,  0x00,  0x01,  0xE0,  0x00,  0x08,  0x00,  0x09,  0x00,  0x00,  0x00,  0xD1,  0x00,  0x7F,  0x10,  0x1A,  0x01,  0x01,  0x01,  0xF6,  0x00,  0x00,  0x7F,  0x03,  0x02,  0x00,  0x00,  0x01,  0x00,  0x0A,  0x00,  0x01,  0x00,  0x7D,  0xCF,  0x03,  0xE8,  0x00,  0x0B,  0x00,  0x04,  0xA4,  0x00,  0x00,  0x19,  0xAA,  0x02,  0x15,  0x33,  0x00,  0x00,  0x19,  0x51,  0x27,  0x10,  0x00,  0x00,  0x13,  0x00)

        self.log.trace("send init sequence")
        for addr, val in zip(addrs, vals):
            self.regs_iface.poke8(addr, val) 

        self.spi_lock.unlock()
        sleep(0.1)
        self.spi_lock.lock()

        # Clear Lock Detect Sticky
        self.log.trace("clear lock sticky")
        addrs = (0x182, 0x182, 0x183, 0x183)
        vals  =  (0x01,  0x00,  0x01,  0x00)
        
        for addr, val in zip(addrs, vals):
            self.regs_iface.poke8(addr, val) 

        self.spi_lock.unlock()
        sleep(0.1)
        self.spi_lock.lock()

        # Check Lock Detects
        self.log.trace("check lock status")
        pll1_lock_status = self.regs_iface.peek8(0x182)
        pll2_lock_status = self.regs_iface.peek8(0x183)

        if not pll1_lock_status == 0x02:
            self.log.error("LMK PLL1 did not lock. Status {0}".format(hex(pll1_lock_status)))

        if not pll2_lock_status == 0x02:
            self.log.error("LMK PLL2 did not lock. Status {0}".format(hex(pll2_lock_status)))

        # Toggle SYNC polarity to trigger SYNC event
        self.regs_iface.poke8(0x143, 0xF1)
        self.regs_iface.poke8(0x143, 0xD1)
        # Enable SYSREF pulses
        self.regs_iface.poke8(0x139, 0x02)
        self.regs_iface.poke8(0x144, 0xFF)
        self.regs_iface.poke8(0x143, 0x52)
        self.spi_lock.unlock()

        self.log.trace("LMK init'd and locked")

