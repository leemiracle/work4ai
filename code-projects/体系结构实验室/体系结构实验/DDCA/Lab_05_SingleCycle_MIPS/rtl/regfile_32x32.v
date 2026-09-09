/**
 * MIPS Register File - DDCA Lab 04 / Lab 05
 *
 * 32 个 32 位寄存器
 * 2 读 1 写，写同步、读异步（适合单周期 CPU）
 * $zero (reg 0) 永远 0
 */
module regfile_32x32 (
    input             clk, we3,
    input      [4:0]  ra1, ra2, wa3,
    input      [31:0] wd3,
    output     [31:0] rd1, rd2
);
    reg [31:0] rf [31:0];

    // 同步写
    always @(posedge clk)
        if (we3 && (wa3 != 5'd0))   // $zero 不能写
            rf[wa3] <= wd3;

    // 异步读
    assign rd1 = (ra1 == 5'd0) ? 32'h0 : rf[ra1];
    assign rd2 = (ra2 == 5'd0) ? 32'h0 : rf[ra2];
endmodule
