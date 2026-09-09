// Expert_03_HW_Designer/rtl/forwarding_unit.v — 5 级流水线 forwarding 单元
// 对应 Capstone/cpu_simulator/rv32i_sim.py 的 _forward 函数
// 实现 EX/MEM → EX 和 MEM/WB → EX 两路 forwarding

`default_nettype none

module forwarding_unit (
    // 当前 EX 阶段指令的源寄存器（来自 ID/EX 流水线寄存器）
    input  wire [4:0]  id_ex_rs1,
    input  wire [4:0]  id_ex_rs2,
    // EX/MEM 槽的指令信息
    input  wire [4:0]  ex_mem_rd,
    input  wire        ex_mem_reg_write,    // 该指令是否写寄存器
    input  wire        ex_mem_is_load,      // load-use 例外（load 不能从这 forward）
    // MEM/WB 槽的指令信息
    input  wire [4:0]  mem_wb_rd,
    input  wire        mem_wb_reg_write,
    // 输出：选择 a/b 两路操作数的来源
    // 2'b00 = 来自 RegFile（默认）
    // 2'b01 = 来自 MEM/WB（次优先）
    // 2'b10 = 来自 EX/MEM（最高优先级，最新值）
    output wire [1:0]  forward_a,
    output wire [1:0]  forward_b
);
    // —— forward_a：操作数 A 的 forwarding ——
    reg [1:0] fa;
    always @(*) begin
        // EX/MEM 优先（最新）
        if (ex_mem_reg_write && (ex_mem_rd != 5'b00000)
                && (ex_mem_rd == id_ex_rs1) && !ex_mem_is_load)
            fa = 2'b10;
        // 次选 MEM/WB
        else if (mem_wb_reg_write && (mem_wb_rd != 5'b00000)
                && (mem_wb_rd == id_ex_rs1))
            fa = 2'b01;
        else
            fa = 2'b00;  // 用 RegFile 默认值
    end

    // —— forward_b：操作数 B 的 forwarding（逻辑同上）——
    reg [1:0] fb;
    always @(*) begin
        if (ex_mem_reg_write && (ex_mem_rd != 5'b00000)
                && (ex_mem_rd == id_ex_rs2) && !ex_mem_is_load)
            fb = 2'b10;
        else if (mem_wb_reg_write && (mem_wb_rd != 5'b00000)
                && (mem_wb_rd == id_ex_rs2))
            fb = 2'b01;
        else
            fb = 2'b00;
    end

    assign forward_a = fa;
    assign forward_b = fb;
endmodule

// 关键观察：
// 1. ex_mem_is_load = 1 时不能从 EX/MEM forward —— load 数据在 MEM 阶段末才出来
//    这就是 load-use stall 的物理基础（必须 stall 1 cycle，详见 hazard_detection_unit.v）
// 2. 检查 rd != 0 —— x0 寄存器永远是 0，写入无效，不能 forward

`default_nettype wire
