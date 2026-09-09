// Expert_03_HW_Designer/rtl/alu.v — RV32I ALU 教学版（可综合）
// 对应 Capstone/cpu_simulator/rv32i_sim.py 的 _alu 函数
// 用 Verilog 2001 语法（兼容主流综合工具 Design Compiler / Yosys / Vivado）

`default_nettype none

module alu #(
    parameter XLEN = 32
)(
    input  wire [3:0]       alu_op,    // 操作码（见下方 ALU_ADD 等宏）
    input  wire [XLEN-1:0]  a,         // 操作数 A
    input  wire [XLEN-1:0]  b,         // 操作数 B
    output wire [XLEN-1:0]  result,    // ALU 输出
    output wire             zero       // 结果为零标志（用于 beq/bne）
);
    // 操作码定义（与 MIPS 教材对齐）
    localparam ALU_ADD  = 4'b0000;
    localparam ALU_SUB  = 4'b0001;
    localparam ALU_AND  = 4'b0010;
    localparam ALU_OR   = 4'b0011;
    localparam ALU_XOR  = 4'b0100;
    localparam ALU_SLL  = 4'b0101;
    localparam ALU_SRL  = 4'b0110;
    localparam ALU_SRA  = 4'b0111;
    localparam ALU_SLT  = 4'b1000;   // signed less than
    localparam ALU_SLTU = 4'b1001;   // unsigned less than

    reg [XLEN-1:0] r;
    wire signed [XLEN-1:0] sa = a;
    wire signed [XLEN-1:0] sb = b;
    wire       [4:0]       shamt = b[4:0];

    always @(*) begin
        case (alu_op)
            ALU_ADD : r = a + b;
            ALU_SUB : r = a - b;
            ALU_AND : r = a & b;
            ALU_OR  : r = a | b;
            ALU_XOR : r = a ^ b;
            ALU_SLL : r = a << shamt;
            ALU_SRL : r = a >> shamt;
            ALU_SRA : r = sa >>> shamt;
            ALU_SLT : r = (sa < sb) ? {{(XLEN-1){1'b0}}, 1'b1} : {XLEN{1'b0}};
            ALU_SLTU: r = (a  < b ) ? {{(XLEN-1){1'b0}}, 1'b1} : {XLEN{1'b0}};
            default : r = {XLEN{1'b0}};
        endcase
    end

    assign result = r;
    assign zero   = (r == {XLEN{1'b0}});
endmodule

`default_nettype wire
