// Expert_03_HW_Designer/rtl/tb_alu.v — alu.v 的 testbench（自检）
// 用 iverilog 跑：iverilog -o tb_alu tb_alu.v alu.v && vvp tb_alu
// 无 iverilog 时也可作为教学文档阅读

`timescale 1ns/1ps
`default_nettype none

module tb_alu;
    reg  [3:0]      alu_op;
    reg  [31:0]     a, b;
    wire [31:0]     result;
    wire            zero;

    integer pass = 0, fail = 0;

    // 实例化 DUT
    alu #(.XLEN(32)) dut (
        .alu_op(alu_op), .a(a), .b(b),
        .result(result), .zero(zero)
    );

    // 测试用例
    task check;
        input [127:0] name;
        input [3:0]   op;
        input [31:0]  aa, bb, expected;
        begin
            alu_op = op; a = aa; b = bb;
            #10;
            if (result === expected) begin
                pass = pass + 1;
            end else begin
                fail = fail + 1;
                $display("[FAIL] %0s: a=%0d b=%0d → %0d (expected %0d)", name, aa, bb, result, expected);
            end
        end
    endtask

    localparam ALU_ADD=4'b0000, ALU_SUB=4'b0001, ALU_AND=4'b0010,
               ALU_OR=4'b0011,  ALU_XOR=4'b0100, ALU_SLL=4'b0101,
               ALU_SRL=4'b0110,  ALU_SRA=4'b0111, ALU_SLT=4'b1000,
               ALU_SLTU=4'b1001;

    initial begin
        // ADD
        check("ADD",  ALU_ADD, 32'd5,  32'd3,  32'd8);
        check("ADD0", ALU_ADD, 32'd0,  32'd0,  32'd0);   // zero=1
        check("ADDf", ALU_ADD, 32'hFFFF_FFFF, 32'd1, 32'd0);  // 溢出 wrap
        // SUB
        check("SUB",  ALU_SUB, 32'd5,  32'd3,  32'd2);
        check("SUBn", ALU_SUB, 32'd0,  32'd1,  32'hFFFF_FFFF);
        // AND/OR/XOR
        check("AND",  ALU_AND, 32'hFF, 32'h0F, 32'h0F);
        check("OR",   ALU_OR,  32'hF0, 32'h0F, 32'hFF);
        check("XOR",  ALU_XOR, 32'hFF, 32'h0F, 32'hF0);
        // SLL/SRL/SRA
        check("SLL",  ALU_SLL, 32'd1,  32'd4,  32'd16);
        check("SRL",  ALU_SRL, 32'h8000_0000, 32'd4, 32'h0800_0000);
        check("SRA",  ALU_SRA, 32'h8000_0000, 32'd4, 32'hF800_0000);  // 算术右移保持符号
        // SLT/SLTU
        check("SLT",  ALU_SLT,  32'hFFFF_FFFF, 32'd0, 32'd1);  // -1 < 0
        check("SLTU", ALU_SLTU, 32'hFFFF_FFFF, 32'd0, 32'd0);  // unsigned 大数

        $display("\n=== ALU testbench: %0d pass, %0d fail ===", pass, fail);
        if (fail == 0) $display("[ALL PASS]");
        else           $display("[SOME FAILED]");
        $finish;
    end
endmodule

`default_nettype wire
