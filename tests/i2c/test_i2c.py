#!/usr/bin/env python
"""

Copyright (c) 2020-2025 Alex Forencich

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
import os

import cocotb_test.simulator

import cocotb
from cocotb.triggers import Timer
from cocotb.regression import TestFactory

from cocotbext.i2c import I2cMaster, I2cMemory


class TB:
    def __init__(self, dut):
        self.dut = dut

        self.log = logging.getLogger("cocotb.tb")
        self.log.setLevel(logging.DEBUG)

        self.i2c_master = I2cMaster(sda=dut.sda_1_o, sda_o=dut.sda_1_i,
            scl=dut.scl_1_o, scl_o=dut.scl_1_i, speed=400e3)
        self.i2c_memory = I2cMemory(sda=dut.sda_2_o, sda_o=dut.sda_2_i,
            scl=dut.scl_2_o, scl_o=dut.scl_2_i, addr=0x50, size=256)


async def run_test(dut, payload_lengths=None, payload_data=None):

    tb = TB(dut)

    await Timer(100, 'us')

    test_data = b'\xaa\xbb\xcc\xdd'

    await tb.i2c_master.write(0x50, b'\x00' + test_data)
    await tb.i2c_master.send_stop()

    await Timer(100, 'us')

    await tb.i2c_master.write(0x50, b'\x00')
    data = await tb.i2c_master.read(0x50, 4)
    await tb.i2c_master.send_stop()

    tb.log.info("Read data: %s", data)

    assert test_data == data


if getattr(cocotb, 'top', None) is not None:

    factory = TestFactory(run_test)
    factory.generate_tests()


# cocotb-test

tests_dir = os.path.dirname(__file__)


def test_i2c(request):
    dut = "test_i2c"
    module = os.path.splitext(os.path.basename(__file__))[0]
    toplevel = dut

    verilog_sources = [
        os.path.join(tests_dir, f"{dut}.v"),
    ]

    parameters = {}

    extra_env = {f'PARAM_{k}': str(v) for k, v in parameters.items()}

    sim_build = os.path.join(tests_dir, "sim_build",
        request.node.name.replace('[', '-').replace(']', ''))

    cocotb_test.simulator.run(
        python_search=[tests_dir],
        verilog_sources=verilog_sources,
        toplevel=toplevel,
        module=module,
        parameters=parameters,
        sim_build=sim_build,
        extra_env=extra_env,
    )
