# I2C interface modules for Cocotb

[![Regression Tests](https://github.com/alexforencich/cocotbext-i2c/actions/workflows/regression-tests.yml/badge.svg)](https://github.com/alexforencich/cocotbext-i2c/actions/workflows/regression-tests.yml)
[![codecov](https://codecov.io/gh/alexforencich/cocotbext-i2c/branch/master/graph/badge.svg)](https://codecov.io/gh/alexforencich/cocotbext-i2c)
[![PyPI version](https://badge.fury.io/py/cocotbext-i2c.svg)](https://pypi.org/project/cocotbext-i2c)
[![Downloads](https://pepy.tech/badge/cocotbext-i2c)](https://pepy.tech/project/cocotbext-i2c)

GitHub repository: https://github.com/alexforencich/cocotbext-i2c

## Introduction

I2C simulation models for [cocotb](https://github.com/cocotb/cocotb).

## Installation

Installation from pip (release version, stable):

    $ pip install cocotbext-i2c

Installation from git (latest development version, potentially unstable):

    $ pip install https://github.com/alexforencich/cocotbext-i2c/archive/master.zip

Installation for active development:

    $ git clone https://github.com/alexforencich/cocotbext-i2c
    $ pip install -e cocotbext-i2c

## Documentation and usage examples

See the `tests` directory, [taxi](https://github.com/fpganinja/taxi), and [verilog-i2c](https://github.com/alexforencich/verilog-i2c) for complete testbenches using these modules.

### I2C Master

The `I2cMaster` class can be used to issue read and write operations on an I2C bus.

Example:

    from cocotbext.i2c import I2cMaster

    i2c_master = I2cMaster(dut.sda_i, dut.sda_o, dut.scl_i, dut.scl_o, 400e3)

To issue I2C operations with an `I2cMaster`, call `read()` or `write()`.  These are the preferred methods, as they will manage the bus state automatically.  Lower-level methods must be called in the appropriate order.  The `read()` and `write()` methods will leave the bus active, so call `send_stop()` to release the bus.

#### Constructor parameters:

* _sda_: serial data in/out
* _sda_o_: serial data output
* _scl_: clock in/out
* _scl_o_: clock output
* _speed_: nominal data rate in bits per second (default `400e3`)

#### Attributes:

* _speed_: nominal data rate in bits per second

#### Methods

* `write(addr, data)`: send _data_ to device at address `addr` (blocking)
* `read(addr, count)`: read _count_ bytes from device at address `addr`  (blocking)
* `send_start()`: send a start condition on the bus
* `send_stop()`: send a stop condition and release the bus
* `send_byte()`: send a byte on the bus
* `recv_byte()`: read a byte from the bus

### I2C Device

The `I2cDevice` class emulates an I2C device.  This class cannot be used directly, instead it should extended and the methods `handle_start()`, `handle_write()`, `handle_read()`, and `handle_stop()` implemented appropriately.  See `I2cMem` for an example.

#### Constructor parameters:

* _sda_: serial data in/out
* _sda_o_: serial data output
* _scl_: clock in/out
* _scl_o_: clock output

### I2C Memory

The `I2cMemory` class emulates a simple memory like an I2C EEPROM.

Example:

    from cocotbext.i2c import I2cMemory

    i2c_mem = I2cMemory(dut.sda_i, dut.sda_o, dut.scl_i, dut.scl_o, 0x50, 256)

The memory can then be read/written via I2C operations on the bus, with the first bytes written after a start bit setting the address, and subsequent reads/writes advancing the internal address and reading/writing the memory.  The memory can also be accessed via `read_mem()` and `write_mem()`.

#### Constructor parameters:

* _sda_: serial data in/out
* _sda_o_: serial data output
* _scl_: clock in/out
* _scl_o_: clock output
* _addr_: device address (default `0x50`)
* _size_: size in bytes (default `256`)

#### Methods

* `read_mem(addr, count)`: read _count_ bytes from memory, starting at `addr`
* `write_mem(addr, data)`: write _data_ to memory, starting at `addr`
