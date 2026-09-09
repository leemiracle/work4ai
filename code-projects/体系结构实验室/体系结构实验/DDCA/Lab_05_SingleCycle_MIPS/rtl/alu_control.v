/**
 * MIPS ALU Control - DDCA Lab 05
 *
 * 把 control 单元的 2-bit alu_op + 指令的 funct 字段
 * 转换为 ALU 实际的 3-bit 操作码
 *
 * alu_op 含义：
 *   00 = 加（用于 lw/sw/addi）
 *   01 = 减（用于 beq）
 *   10 = 看 funct（R-type）
 *   11 = reserved
 */
module alu_control (
    input  [1:0]     alu_op,
    input  [5:0]     funct,
    output reg [2:0] alu_control
);
    // ALU 操作码（与 mips_alu.v 的 4-bit 高 1 位补 0 对应）
    localparam ALU_AND = 3'b000;
    localparam ALU_OR  = 3'b001;
    localparam ALU_ADD = 3'b010;
    localparam ALU_SUB = 3'b110;
    localparam ALU_SLT = 3'b111;

    always @(*) begin
        case (alu_op)
            2'b00: alu_control = ALU_ADD;   // lw/sw/addi
            2'b01: alu_control = ALU_SUB;   // beq
            2'b10: begin                    // R-type, 看 funct
                case (funct)
                    6'b100000: alu_control = ALU_ADD;  // add
                    6'b100010: alu_control = ALU_SUB;  // sub
                    6'b100100: alu_control = ALU_AND;  // and
                    6'b100101: alu_control = ALU_OR;   // or
                    6'b101010: alu_control = ALU_SLT;  // slt
                    default:   alu_control = 3'bxxx;
                endcase
            end
            default: alu_control = 3'bxxx;
        endcase
    end
endmodule
