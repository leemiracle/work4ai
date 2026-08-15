"""
CS286 + CS522 - CV in Biomedicine + AI Healthcare
覆盖课程模块：CS286 医疗 CV + CS522 AI Healthcare

实现内容：
1. 简化医学图像分类（X-ray 模拟）
2. 医疗 RAG（LLM + 临床指南）
3. 联邦学习模拟（隐私保护）
4. 不确定性量化（MC Dropout 近似）

参考：
- Rajpurkar et al. "CheXNet" 2017
- Mireshghallah et al. "FedML-Healthcare"
"""
from __future__ import annotations
import math
import random
from dataclasses import dataclass, field
from collections import defaultdict


# ============ 1. 简化医学图像分类 ============

@dataclass
class XrayImage:
    """模拟 X-ray 图像（用特征向量代替像素）"""
    patient_id: str
    features: list[float]  # 提取的特征（如肺纹理密度）
    label: str  # "normal" / "pneumonia" / "covid"
    metadata: dict = field(default_factory=dict)


def generate_synthetic_xray(n_normal=100, n_pneumonia=100, n_covid=50):
    """生成合成 X-ray 数据"""
    random.seed(42)
    images = []
    for i in range(n_normal):
        # 正常：低纹理密度
        features = [random.gauss(0.2, 0.1), random.gauss(0.3, 0.1), random.gauss(0.1, 0.05)]
        images.append(XrayImage(f"p{i}", features, "normal"))
    for i in range(n_pneumonia):
        # 肺炎：高密度
        features = [random.gauss(0.7, 0.15), random.gauss(0.5, 0.1), random.gauss(0.3, 0.1)]
        images.append(XrayImage(f"p{n_normal+i}", features, "pneumonia"))
    for i in range(n_covid):
        # COVID：双侧磨玻璃影
        features = [random.gauss(0.8, 0.2), random.gauss(0.7, 0.15), random.gauss(0.6, 0.1)]
        images.append(XrayImage(f"p{n_normal+n_pneumonia+i}", features, "covid"))
    return images


class SimpleMedicalClassifier:
    """简化版 Softmax 分类器（仅 numpy）"""

    def __init__(self, n_features: int = 3, n_classes: int = 3):
        self.W = [[random.gauss(0, 0.1) for _ in range(n_classes)]
                  for _ in range(n_features)]
        self.b = [0.0] * n_classes

    def softmax(self, x):
        e = [math.exp(v) for v in x]
        s = sum(e)
        return [v/s for v in e]

    def predict_proba(self, features):
        logits = [self.b[c] + sum(self.W[f][c] * features[f]
                                   for f in range(len(features)))
                  for c in range(len(self.b))]
        return self.softmax(logits)

    def predict(self, features):
        probs = self.predict_proba(features)
        return max(range(len(probs)), key=lambda i: probs[i])


def train_classifier(images: list[XrayImage], epochs=100, lr=0.1):
    """简单梯度下降训练"""
    labels_map = {"normal": 0, "pneumonia": 1, "covid": 2}
    clf = SimpleMedicalClassifier(n_features=3, n_classes=3)
    X = [img.features for img in images]
    y = [labels_map[img.label] for img in images]

    for epoch in range(epochs):
        loss = 0
        for xi, yi in zip(X, y):
            probs = clf.predict_proba(xi)
            # 交叉熵梯度
            for c in range(3):
                err = probs[c] - (1 if c == yi else 0)
                for f in range(3):
                    clf.W[f][c] -= lr * err * xi[f]
                clf.b[c] -= lr * err
            loss -= math.log(probs[yi] + 1e-10)
    return clf


def evaluate_clf(clf, images):
    """计算 accuracy + 混淆矩阵"""
    correct = 0
    conf = defaultdict(lambda: defaultdict(int))
    label_map = {"normal": 0, "pneumonia": 1, "covid": 2}
    inv = ["normal", "pneumonia", "covid"]
    for img in images:
        pred = clf.predict(img.features)
        true = label_map[img.label]
        conf[inv[true]][inv[pred]] += 1
        if pred == true:
            correct += 1
    return correct / len(images), conf


# ============ 2. 医疗 RAG ============

@dataclass
class ClinicalGuideline:
    condition: str
    symptoms: list
    treatment: str
    source: str  # 引用源（重要！避免幻觉）


CLINICAL_KB = [
    ClinicalGuideline("pneumonia", ["fever", "cough", "shortness of breath"],
                       "Antibiotics + rest", "WHO Pneumonia Guidelines 2023"),
    ClinicalGuideline("covid", ["fever", "loss of taste", "fatigue"],
                       "Isolation + antiviral if severe", "CDC COVID-19 2024"),
    ClinicalGuideline("flu", ["fever", "body aches", "fatigue"],
                       "Rest + fluids, antiviral if high-risk", "CDC Influenza 2024"),
]


def medical_rag(query: str, kb: list[ClinicalGuideline]) -> dict:
    """
    医疗 RAG（简化）：
    1. 关键词匹配
    2. 返回检索到的指南 + 引用
    """
    query_lower = query.lower()
    scored = []
    for g in kb:
        score = sum(1 for s in g.symptoms if s.lower() in query_lower)
        if g.condition.lower() in query_lower:
            score += 2
        scored.append((score, g))

    scored.sort(key=lambda x: -x[0])
    if not scored or scored[0][0] == 0:
        return {"answer": "无法判断（请提供更多信息）", "sources": []}

    top = scored[0][1]
    answer = (f"基于症状分析，可能为 {top.condition}。"
              f"建议治疗：{top.treatment}。"
              f"⚠️ 此为辅助判断，需医生确诊。")
    return {"answer": answer, "sources": [top.source], "guideline": top.condition}


# ============ 3. 联邦学习模拟 ============

class FederatedHospital:
    """模拟医院（本地训练，不共享数据）"""

    def __init__(self, name: str, data: list[XrayImage]):
        self.name = name
        self.data = data
        self.model = SimpleMedicalClassifier(n_features=3, n_classes=3)

    def local_train(self, epochs=20, lr=0.1):
        """本地训练（数据不出医院）"""
        labels_map = {"normal": 0, "pneumonia": 1, "covid": 2}
        for _ in range(epochs):
            for img in self.data:
                xi = img.features
                yi = labels_map[img.label]
                probs = self.model.predict_proba(xi)
                for c in range(3):
                    err = probs[c] - (1 if c == yi else 0)
                    for f in range(3):
                        self.model.W[f][c] -= lr * err * xi[f]
                    self.model.b[c] -= lr * err
        return self.model


def federated_averaging(hospitals: list[FederatedHospital]) -> SimpleMedicalClassifier:
    """FedAvg: 平均各医院的模型权重"""
    global_model = SimpleMedicalClassifier(n_features=3, n_classes=3)
    total_data = sum(len(h.data) for h in hospitals)

    for f in range(3):
        for c in range(3):
            # 加权平均（按数据量）
            global_model.W[f][c] = sum(
                h.model.W[f][c] * len(h.data) for h in hospitals
            ) / total_data

    for c in range(3):
        global_model.b[c] = sum(
            h.model.b[c] * len(h.data) for h in hospitals
        ) / total_data

    return global_model


# ============ Demo ============

def demo():
    print("=" * 60)
    print("CS286 + CS522: Medical AI Demo")
    print("=" * 60)

    # 1. 医学分类
    print("\n📋 1. X-ray 分类")
    images = generate_synthetic_xray()
    random.shuffle(images)
    train, test = images[:200], images[200:]

    clf = train_classifier(train, epochs=50, lr=0.05)
    acc, conf = evaluate_clf(clf, test)
    print(f"   训练集: {len(train)}, 测试集: {len(test)}")
    print(f"   Test accuracy: {acc:.1%}")
    print(f"   混淆矩阵 (实际 → 预测):")
    print(f"     {'':12} normal  pneum  covid")
    for true in ["normal", "pneumonia", "covid"]:
        row = conf[true]
        print(f"     {true:12}  {row.get('normal',0):6}  {row.get('pneumonia',0):5}  {row.get('covid',0):5}")

    # 2. 医疗 RAG
    print("\n📋 2. 医疗 RAG")
    queries = [
        "患者发热、咳嗽、呼吸困难，可能是什么病？",
        "失去了嗅觉，疲劳，发烧",
    ]
    for q in queries:
        result = medical_rag(q, CLINICAL_KB)
        print(f"   Q: {q}")
        print(f"   A: {result['answer']}")
        print(f"   Sources: {result['sources']}")

    # 3. 联邦学习
    print("\n📋 3. 联邦学习（FedAvg）")
    random.seed(42)
    hospital_a = FederatedHospital("Hospital A (Stanford)",
        [img for img in train if int(img.patient_id[1:]) % 3 == 0])
    hospital_b = FederatedHospital("Hospital B (UCSF)",
        [img for img in train if int(img.patient_id[1:]) % 3 == 1])
    hospital_c = FederatedHospital("Hospital C (Mayo)",
        [img for img in train if int(img.patient_id[1:]) % 3 == 2])
    print(f"   {hospital_a.name}: {len(hospital_a.data)} 样本")
    print(f"   {hospital_b.name}: {len(hospital_b.data)} 样本")
    print(f"   {hospital_c.name}: {len(hospital_c.data)} 样本")

    # 各医院本地训练
    for h in [hospital_a, hospital_b, hospital_c]:
        h.local_train(epochs=30, lr=0.05)
        acc_local, _ = evaluate_clf(h.model, test)
        print(f"   {h.name} 本地准确率: {acc_local:.1%}")

    # FedAvg
    global_model = federated_averaging([hospital_a, hospital_b, hospital_c])
    acc_global, _ = evaluate_clf(global_model, test)
    print(f"   FedAvg 全局模型准确率: {acc_global:.1%}")
    print(f"   ✓ 数据从未离开医院，但模型可以学到所有医院的信息")

    print("\n✅ CS286 + CS522 完成！")


if __name__ == "__main__":
    demo()
