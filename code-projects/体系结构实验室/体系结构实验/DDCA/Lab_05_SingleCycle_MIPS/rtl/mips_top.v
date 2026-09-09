/**
 * MIPS Single-Cycle Top - DDCA Lab 05
 *
 * 这是单周期 MIPS CPU 的顶层模块。
 * 你需要：
 *   1. 完成 pc.v / imem.v / dmem.v / sign_extend.v 等子模块
 *   2. 把这个顶层连起来
 *   3. 用 test_program.hex 测试
 *
 * 完整 datapath 见 README.md §3.1 的图。
 */
module mips_top (
    input             clk, reset,
    output     [31:0] pc,
    output     [31:0] instr,
    output     [31:0] alu_result,
    output            mem_write
);
    // ============= 控制信号 =============
    wire        reg_dst, alu_src, mem_to_reg, reg_write;
    wire        mem_write_ctrl, mem_read, branch, jump;
    wire [1:0]  alu_op;
    wire [2:0]  alu_ctrl;
    wire        zero;

    // ============= 数据信号 =============
    wire [31:0] pc_plus_4, pc_branch, jump_target;
    wire [31:0] instr_read;
    wire [31:0] rd1, rd2, sign_ext_imm;
    wire [31:0] alu_src_b;
    wire [31:0] alu_out;
    wire [31:0] mem_read_data;
    wire [31:0] write_data;
    wire [4:0]  write_reg;

    // ============= PC =============
    wire branch_taken = branch & zero;

    pc mips_pc (
        .clk(clk), .reset(reset),
        .branch_taken(branch_taken),
        .branch_target(pc_branch),
        .jump(jump),
        .jump_target(jump_target),
        .pc(pc)
    );

    assign pc_plus_4 = pc + 32'd4;
    assign pc_branch = pc_plus_4 + {sign_ext_imm[29:0], 2'b00};
    assign jump_target = {pc_plus_4[31:28], instr_read[25:0], 2'b00};

    // ============= Instruction Memory =============
    imem mips_imem (.a(pc), .rd(instr_read));
    assign instr = instr_read;

    // ============= Control =============
    control mips_control (
        .op(instr_read[31:26]),
        .reg_dst(reg_dst), .alu_src(alu_src),
        .mem_to_reg(mem_to_reg), .reg_write(reg_write),
        .mem_write(mem_write_ctrl), .mem_read(mem_read),
        .branch(branch), .jump(jump), .alu_op(alu_op)
    );

    // ============= ALU Control =============
    alu_control mips_alu_ctrl (
        .alu_op(alu_op),
        .funct(instr_read[5:0]),
        .alu_control(alu_ctrl)
    );

    // ============= Register File =============
    regfile_32x32 mips_rf (
        .clk(clk), .we3(reg_write),
        .ra1(instr_read[25:21]),
        .ra2(instr_read[20:16]),
        .wa3(write_reg),
        .wd3(write_data),
        .rd1(rd1), .rd2(rd2)
    );

    assign write_reg = reg_dst ? instr_read[15:11] : instr_read[20:16];

    // ============= Sign Extend =============
    sign_extend mips_se (
        .imm(instr_read[15:0]),
        .ext(sign_ext_imm)
    );

    // ============= ALU =============
    assign alu_src_b = alu_src ? sign_ext_imm : rd2;

    mips_alu mips_alu_unit (
        .alucont({1'b0, alu_ctrl}),
        .a(rd1), .b(alu_src_b),
        .result(alu_out),
        .zero(zero),
        .overflow()
    );

    // ============= Data Memory =============
    dmem mips_dmem (
        .clk(clk), .we(mem_write_ctrl),
        .a(alu_out), .wd(rd2),
        .rd(mem_read_data)
    );

    // ============= Write Back =============
    assign write_data = mem_to_reg ? mem_read_data : alu_out;

    // ============= Output =============
    assign alu_result = alu_out;
    assign mem_write  = mem_write_ctrl;
endmodule
