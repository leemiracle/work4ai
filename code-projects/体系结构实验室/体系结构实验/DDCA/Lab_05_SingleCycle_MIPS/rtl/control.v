/**
 * MIPS Control Unit - DDCA Lab 05
 *
 * 根据指令的 op 字段（高 6 位）生成所有控制信号
 *
 * 控制信号含义：
 *   reg_dst    : 1=rd (R-type), 0=rt (I-type)
 *   alu_src    : 1=imm (I-type/lw/sw), 0=reg (R-type)
 *   mem_to_reg : 1=memory data (lw), 0=ALU result
 *   reg_write  : 1=write to regfile
 *   mem_write  : 1=write to dmem (sw)
 *   mem_read   : 1=read from dmem (lw)
 *   branch     : 1=conditional branch (beq/bne)
 *   jump       : 1=unconditional jump (j/jal)
 *   alu_op     : 2-bit, tells alu_control what to compute
 *
 * 注：完整实现还需要 addi/andi/ori/jal/jr 等，留给学生扩展
 */
module control (
    input  [5:0] op,
    output       reg_dst, alu_src, mem_to_reg, reg_write,
    output       mem_write, mem_read, branch, jump,
    output [1:0] alu_op
);
    reg [9:0] controls;
    assign {reg_dst, alu_src, mem_to_reg, reg_write,
            mem_write, mem_read, branch, jump, alu_op} = controls;

    always @(*) begin
        case (op)
            6'b000000:  controls = 10'b1_0_0_1_0_0_0_0_10;  // R-type
            6'b100011:  controls = 10'b0_1_1_1_0_1_0_0_00;  // lw
            6'b101011:  controls = 10'b0_1_0_0_1_0_0_0_00;  // sw
            6'b000100:  controls = 10'b0_0_0_0_0_0_1_0_01;  // beq
            6'b001000:  controls = 10'b0_1_0_1_0_0_0_0_00;  // addi
            6'b000010:  controls = 10'b0_0_0_0_0_0_0_1_00;  // j
            default:    controls = 10'b0_0_0_0_0_0_0_0_00;
        endcase
    end
endmodule
