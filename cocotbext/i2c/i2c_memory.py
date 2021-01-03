"""

Copyright (c) 2020 Alex Forencich

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

"""

import mmap

from .i2c_device import I2cDevice
from .version import __version__


class I2cMemory(I2cDevice):

    def __init__(self, sda=None, sda_o=None, scl=None, scl_o=None, addr=0x50, size=256, *args, **kwargs):
        super().__init__(sda, sda_o, scl, scl_o, *args, **kwargs)

        self.log.info("I2C Memory")
        self.log.info("cocotbext-i2c version %s", __version__)
        self.log.info("Copyright (c) 2020 Alex Forencich")
        self.log.info("https://github.com/alexforencich/cocotbext-i2c")

        self.size = size
        self.mem = mmap.mmap(-1, size)
        self.addr = addr
        self.ptr = 0

        self.addr_size = ((size-1).bit_length() + 7) // 8
        self.addr_ptr = self.addr_size-1

        self.log.info("I2C memory configuration:")
        self.log.info("  Device address: 0x%02x", self.addr)
        self.log.info("  Size: %d bytes", self.size)

    def read_mem(self, address, length):
        self.mem.seek(address)
        return self.mem.read(length)

    def write_mem(self, address, data):
        self.mem.seek(address)
        self.mem.write(data)

    def handle_start(self):
        self.addr_ptr = self.addr_size-1

    async def handle_write(self, data):
        if self.addr_ptr >= 0:
            self.ptr = (data << self.addr_ptr * 8) | (self.ptr & ~(0xff << self.addr_ptr))
            self.addr_ptr -= 1
            self.log.info("Set ptr 0x%04x", self.ptr)
        else:
            self.mem[self.ptr] = data
            self.log.info("Write ptr 0x%04x data 0x%02x", self.ptr, data)
            self.ptr = (self.ptr + 1) % self.size

    async def handle_read(self):
        data = self.mem[self.ptr]
        self.log.info("Read ptr 0x%04x data 0x%02x", self.ptr, data)
        self.ptr = (self.ptr + 1) % self.size
        return data

    def handle_stop(self):
        pass
