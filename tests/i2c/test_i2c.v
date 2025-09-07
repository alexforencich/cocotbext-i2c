/*

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

*/

// Language: Verilog 2001

`timescale 1ns / 1ns

/*
 * I2C test
 */
module test_i2c
(
    input  wire sda_1_i,
    output wire sda_1_o,
    input  wire scl_1_i,
    output wire scl_1_o,

    input  wire sda_2_i,
    output wire sda_2_o,
    input  wire scl_2_i,
    output wire scl_2_o
);

assign sda_1_o = sda_1_i & sda_2_i;
assign scl_1_o = scl_1_i & scl_2_i;

assign sda_2_o = sda_1_i & sda_2_i;
assign scl_2_o = scl_1_i & scl_2_i;

endmodule
