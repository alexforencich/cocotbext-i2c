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

import logging

import cocotb
from cocotb.triggers import RisingEdge, FallingEdge, First


class I2cDevice:

    def __init__(self, sda=None, sda_o=None, scl=None, scl_o=None, *args, **kwargs):
        self.log = logging.getLogger(f"cocotb.{sda._path}")
        self.sda = sda
        self.sda_o = sda_o
        self.scl = scl
        self.scl_o = scl_o

        super().__init__(*args, **kwargs)

        if self.sda_o is not None:
            self.sda_o.setimmediatevalue(1)
        if self.scl_o is not None:
            self.scl_o.setimmediatevalue(1)

        cocotb.fork(self._run())

    def handle_start(self):
        pass

    async def handle_write(self, data):
        pass

    async def handle_read(self):
        return 0

    def handle_stop(self):
        pass

    def _set_sda(self, val):
        if self.sda_o is not None:
            self.sda_o <= val
        else:
            self.sda <= val
            # self.sda <= BinaryValue('z') if val else 0

    def _set_scl(self, val):
        if self.scl_o is not None:
            self.scl_o <= val
        else:
            self.scl <= val
            # self.scl <= BinaryValue('z') if val else 0

    async def _send_bit(self, b):
        if self.scl.value.integer:
            await FallingEdge(self.scl)

        self._set_sda(bool(b))

        self._set_scl(1)

        await FallingEdge(self.scl)

        self._set_sda(1)

    async def _recv_bit(self):
        self._set_scl(1)
        self._set_sda(1)

        if self.scl.value.integer:
            await First(FallingEdge(self.scl), RisingEdge(self.sda), FallingEdge(self.sda))

            if self.scl.value.integer:
                # Got start or stop bit
                if self.sda.value.integer:
                    return 'stop'
                else:
                    return 'start'

        await RisingEdge(self.scl)

        return bool(self.sda.value.integer)

    async def _send_byte(self, b):
        for i in range(8):
            await self._send_bit(b & (1 << 7-i))

    async def _send_byte_ack(self, b):
        await self._send_byte(b)
        return await self._recv_bit()

    async def _recv_byte(self):
        b = 0
        for i in range(8):
            val = await self._recv_bit()
            if type(val) is str:
                return val
            b = (b << 1) | val
        return b

    async def _recv_byte_ack(self, ack):
        b = await self._recv_byte()
        if type(b) is not str:
            await self._send_bit(ack)
        return b

    async def _run(self):
        line_active = False

        while True:
            self._set_sda(1)

            await FallingEdge(self.sda)

            if self.scl.value.integer:
                # start condition
                self.log.info("Got start bit")
                line_active = True
                self.handle_start()

                while line_active:
                    # read address
                    addr = await self._recv_byte()

                    if addr == 'stop':
                        self.log.info("Got stop bit")
                        line_active = False
                        self.handle_stop()
                        break
                    elif addr == 'start':
                        self.log.info("Got repeated start bit")
                        self.handle_start()
                        break

                    if addr >> 1 == self.addr:
                        await self._send_bit(0)

                        if addr & 1:
                            self.log.info("Address matched (read)")

                            while True:
                                self._set_scl(0)
                                b = await self.handle_read()
                                self._set_scl(1)
                                ack = await self._send_byte_ack(b)
                                if ack:
                                    self.log.info("Got NACK")
                                    break
                        else:
                            self.log.info("Address matched (write)")

                            while True:
                                b = await self._recv_byte_ack(0)

                                if b == 'stop':
                                    self.log.info("Got stop bit")
                                    line_active = False
                                    self.handle_stop()
                                    break
                                elif b == 'start':
                                    self.log.info("Got repeated start bit")
                                    self.handle_start()
                                    break
                                else:
                                    self._set_scl(0)
                                    await self.handle_write(b)
                                    self._set_scl(1)
                    else:
                        # no match
                        break
