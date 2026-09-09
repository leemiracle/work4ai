#!/usr/bin/env python3
"""tiny2pc — 参照 XA/Two-Phase Commit 的分布式事务
参照：2PC / 3PC / Saga / XA
csdiy 对应：tinytx(MVCC) + tinyraft(分布式) + db §二
核心：协调者 → Prepare → Commit/Abort"""
import threading, time, random
from dataclasses import dataclass
from enum import Enum

class TxStatus(Enum): PREPARING="PREPARING"; COMMITTED="COMMITTED"; ABORTED="ABORTED"

@dataclass
class Participant:
    name: str; ready: bool=False; committed: bool=False

class Coordinator:
    """2PC 协调者（参照 Gray 1978 / XA）
    Phase 1: Prepare → 所有参与者投票
    Phase 2: 全部 YES → Commit；任一 NO → Abort"""
    def __init__(self,participants):
        self.participants=participants; self.txns={}
    def begin(self,txn_id,operation):
        self.txns[txn_id]={"status":TxStatus.PREPARING,"op":operation,"participants":self.participants[:]}
        print(f"\n  TXN {txn_id}: BEGIN (op={operation})")
    def prepare(self,txn_id):
        """Phase 1: Prepare"""
        txn=self.txns[txn_id]
        all_ready=True
        for p in txn["participants"]:
            # 模拟参与者投票（90% 概率同意）
            vote=random.random()<0.9
            p.ready=vote
            status="YES" if vote else "NO"
            print(f"  TXN {txn_id}: {p.name} → Prepare {status}")
            if not vote: all_ready=False; break
        return all_ready
    def commit(self,txn_id):
        txn=self.txns[txn_id]
        for p in txn["participants"]:
            p.committed=True
            print(f"  TXN {txn_id}: {p.name} → Commit ✅")
        txn["status"]=TxStatus.COMMITTED
    def abort(self,txn_id):
        txn=self.txns[txn_id]
        for p in txn["participants"]:
            if p.ready: print(f"  TXN {txn_id}: {p.name} → Rollback ↩️")
        txn["status"]=TxStatus.ABORTED
    def execute(self,txn_id,operation):
        """完整 2PC 流程"""
        self.begin(txn_id,operation)
        if self.prepare(txn_id):
            self.commit(txn_id)
            print(f"  TXN {txn_id}: COMMITTED ✅")
        else:
            self.abort(txn_id)
            print(f"  TXN {txn_id}: ABORTED ❌")

class SagaCoordinator:
    """Saga 模式（参照 Garcia-Molina 1987）
    补偿事务替代全局回滚"""
    def __init__(self): self.steps=[]
    def add_step(self,name,action,compensation):
        self.steps.append({"name":name,"action":action,"compensation":compensation})
    def execute(self):
        completed=[]
        for step in self.steps:
            result=step["action"]()
            if result:
                completed.append(step); print(f"  ✅ {step['name']}: success")
            else:
                print(f"  ❌ {step['name']}: failed → compensating...")
                for s in reversed(completed):
                    s["compensation"](); print(f"  ↩️  {s['name']}: compensated")
                return False
        return True

def main():
    print("tiny2pc — 分布式事务（参照 2PC + Saga）\n")
    # 2PC
    print("── Two-Phase Commit ──")
    participants=[Participant("order-db"),Participant("inventory-db"),Participant("payment")]
    coord=Coordinator(participants)
    coord.execute("TX001","transfer $100")
    # Saga
    print("\n── Saga Pattern ──")
    saga=SagaCoordinator()
    saga.add_step("reserve_flight",lambda:True,lambda:print("    cancel_flight"))
    saga.add_step("reserve_hotel",lambda:True,lambda:print("    cancel_hotel"))
    saga.add_step("charge_card",lambda:False,lambda:print("    refund"))  # 故意失败
    saga.execute()
    print(f"\n  2PC: 强一致，但阻塞（协调者挂=全部等待）")
    print(f"  Saga: 最终一致，非阻塞（用补偿替代回滚）")

if __name__=="__main__": main()
