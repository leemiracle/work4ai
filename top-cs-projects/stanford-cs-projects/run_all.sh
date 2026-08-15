#!/bin/bash
# 批量运行所有主题 demo
set -e

PROJECTS=(
    "topic1-choice/choice_theory.py"
    "topic2-agent-v2/dspy_framework.py"
    "topic3-safety/pluralistic_safety.py"
    "topic4-mlsys/kv_cache_sim.py"
    "topic5-robot/motion_planner.py"
    "topic6-graph/gcn_from_scratch.py"
    "topic7-hci/hci_eval.py"
    "topic8-med/medical_rag.py"
    "topic9-systems/tcp_sim.py"
    "topic10-theory/rsa_crypto.py"
    "topic11-graphics/ray_tracer.py"
    "topic12-intro/sorting_visualizer.py"
)

for proj in "${PROJECTS[@]}"; do
    echo ""
    echo "============================================================"
    echo "▶ Running: $proj"
    echo "============================================================"
    if python3 "$proj" > /tmp/demo_output.log 2>&1; then
        echo "✅ PASS"
        # 显示最后 3 行（结论）
        tail -3 /tmp/demo_output.log
    else
        echo "❌ FAIL"
        tail -20 /tmp/demo_output.log
    fi
done
