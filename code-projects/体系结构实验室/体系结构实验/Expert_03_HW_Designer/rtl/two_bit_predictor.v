// Expert_03_HW_Designer/rtl/two_bit_predictor.v — 2-bit 饱和分支预测器 FSM
// 对应 Capstone/cpu_simulator/rv32i_sim.py 的 TwoBitPredictor 类
// 状态机：SN → WN → WT → ST（带迟滞 hysteresis）

`default_nettype none

module two_bit_predictor (
    input  wire clk,
    input  wire rst_n,            // 异步低有效复位
    // 预测阶段：IF/ID 时查询（combinational）
    output wire predict_taken,    // 1 = 预测 taken
    // 更新阶段：分支结果出来后更新（同步）
    input  wire branch_resolve,   // 1 = 本周期有分支需要更新
    input  wire taken_actual      // 实际是否 taken
);
    // 4 状态 FSM
    localparam [1:0]
        SN = 2'b00,   // Strongly Not-taken
        WN = 2'b01,   // Weakly Not-taken
        WT = 2'b10,   // Weakly Taken
        ST = 2'b11;   // Strongly Taken

    reg [1:0] state, next_state;

    // —— 状态寄存器 ——
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n)
            state <= WN;   // 复位为弱 not-taken
        else
            state <= next_state;
    end

    // —— 次态组合逻辑 ——
    always @(*) begin
        if (branch_resolve) begin
            case (state)
                SN: next_state = taken_actual ? WN : SN;
                WN: next_state = taken_actual ? WT : SN;
                WT: next_state = taken_actual ? ST : WN;
                ST: next_state = taken_actual ? ST : WT;
                default: next_state = WN;
            endcase
        end else begin
            next_state = state;   // 无更新则保持
        end
    end

    // —— 输出：predict_taken 当状态在 WT 或 ST 时为 1 ——
    assign predict_taken = state[1];   // 即 state == WT || state == ST

endmodule

// 真实飞腾的预测器：
// - TAGE-SC-L 变种（多个历史长度表 + 统计修正器 + loop 预测）
// - 复杂度高 1000×，但 FSM 思想不变
// - 状态存储：BTB + PHT + RAS，数百 KB SRAM

`default_nettype wire
