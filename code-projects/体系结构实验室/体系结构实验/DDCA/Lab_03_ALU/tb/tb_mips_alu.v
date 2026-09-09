/**
 * Testbench for mips_alu - DDCA Lab 03
 *
 * 用法：iverilog -o sim/tb mips_alu.v tb_mips_alu.v && vvp sim/tb
 */
`timescale 1ns/1ps

module tb_mips_alu;
    reg  [3:0]  alucont;
    reg  [31:0] a, b;
    wire [31:0] result;
    wire        zero, overflow;

    integer errors = 0;

    mips_alu dut (
        .alucont(alucont), .a(a), .b(b),
        .result(result), .zero(zero), .overflow(overflow)
    );

    task check;
        input [127:0] name;
        input [31:0]  expected;
        begin
            if (result !== expected) begin
                $display("FAIL: %0s got %h, expected %h", name, result, expected);
                errors = errors + 1;
            end else begin
                $display("PASS: %0s = %h", name, result);
            end
        end
    endtask

    initial begin
        // AND
        a = 32'hFF00FF00; b = 32'h0FF00FF0; alucont = 4'b0000; #10;
        check("AND", 32'h0F000F00);

        // OR
        alucont = 4'b0001; #10;
        check("OR", 32'hFFF0FFF0);

        // ADD
        a = 32'd5; b = 32'd3; alucont = 4'b0010; #10;
        check("ADD", 32'd8);

        // SUB
        a = 32'd10; b = 32'd7; alucont = 4'b0110; #10;
        check("SUB", 32'd3);

        // SLT (signed)
        a = 32'hFFFFFFFF; b = 32'h00000001; alucont = 4'b0111; #10;
        check("SLT (-1 < 1)", 32'h1);

        a = 32'd5; b = 32'd3; alucont = 4'b0111; #10;
        check("SLT (5 < 3 = 0)", 32'h0);

        // NOR
        a = 32'h00000000; b = 32'h00000000; alucont = 4'b1100; #10;
        check("NOR", 32'hFFFFFFFF);

        // ADD overflow
        a = 32'h7FFFFFFF; b = 32'h00000001; alucont = 4'b0010; #10;
        if (!overflow) begin $display("FAIL: overflow should be 1"); errors = errors + 1; end
        else $display("PASS: overflow detected");

        // SUB overflow
        a = 32'h80000000; b = 32'h00000001; alucont = 4'b0110; #10;
        if (!overflow) begin $display("FAIL: overflow should be 1"); errors = errors + 1; end
        else $display("PASS: overflow detected");

        // Summary
        if (errors == 0)
            $display("\n✅ All tests passed!");
        else
            $display("\n❌ %0d test(s) failed", errors);

        $finish;
    end
endmodule
