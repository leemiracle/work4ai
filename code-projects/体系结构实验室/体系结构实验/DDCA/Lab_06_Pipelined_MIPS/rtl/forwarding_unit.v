/**
 * MIPS Pipelined Forwarding Unit - DDCA Lab 06
 *
 * 与本项目 Expert_03/rtl/forwarding_unit.v 几乎完全相同。
 * 学完 L06 后可以直接对照读 Expert_03 的 RV32I 版本。
 *
 * Forwarding 真值表：
 *
 *   forward_a / forward_b:
 *     00 = use regfile output (no hazard)
 *     01 = forward from MEM/WB pipeline reg
 *     10 = forward from EX/MEM pipeline reg (优先，因为更"新")
 *
 * 关键规则：
 *   1. EX/MEM hazard 优先于 MEM/WB hazard（更新数据）
 *   2. rd == 0 时不能 forward（避免错误覆盖 $zero）
 */
module forwarding_unit (
    input  [4:0]     id_ex_rs,    // EX 阶段读 regfile 的源 1
    input  [4:0]     id_ex_rt,    // EX 阶段读 regfile 的源 2
    input  [4:0]     ex_mem_rd,   // MEM 阶段的目的
    input  [4:0]     mem_wb_rd,   // WB  阶段的目的
    input            ex_mem_reg_write,
    input            mem_wb_reg_write,
    output reg [1:0] forward_a,
    output reg [1:0] forward_b
);
    always @(*) begin
        // ---- Forward A (rs) ----
        if (ex_mem_reg_write && (ex_mem_rd != 5'b0) && (ex_mem_rd == id_ex_rs))
            forward_a = 2'b10;   // EX/MEM hazard，优先
        else if (mem_wb_reg_write && (mem_wb_rd != 5'b0) && (mem_wb_rd == id_ex_rs))
            forward_a = 2'b01;   // MEM/WB hazard
        else
            forward_a = 2'b00;   // 无 hazard

        // ---- Forward B (rt) ----
        if (ex_mem_reg_write && (ex_mem_rd != 5'b0) && (ex_mem_rd == id_ex_rt))
            forward_b = 2'b10;
        else if (mem_wb_reg_write && (mem_wb_rd != 5'b0) && (mem_wb_rd == id_ex_rt))
            forward_b = 2'b01;
        else
            forward_b = 2'b00;
    end
endmodule


/**
 * Hazard Unit - 检测 Load-Use 冒险
 *
 * 当 ID 阶段的源寄存器等于 EX 阶段 lw 的目的寄存器时，
 * 必须插 1 拍 NOP。
 */
module hazard_unit (
    input  [4:0] id_ex_rt,
    input  [4:0] if_id_rs, if_id_rt,
    input        id_ex_mem_read,
    output       stall_pc,
    output       stall_if_id,
    output       flush_id_ex,
    input        branch_taken    // 分支预测错误
);
    wire load_use_hazard = id_ex_mem_read &&
                           ((id_ex_rt == if_id_rs) || (id_ex_rt == if_id_rt));

    assign stall_pc      = load_use_hazard;
    assign stall_if_id   = load_use_hazard;
    assign flush_id_ex   = load_use_hazard | branch_taken;
endmodule
