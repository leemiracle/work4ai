
class ChainOfThoughtPrompter:
    def __init__(self, llm_client):
        self.llm = llm_client
        self.few_shot_examples = [
            {
                "question": "Roger有5个网球。他又买了2罐网球，每罐有3个球。他现在有几个网球？",
                "reasoning": "Roger一开始有5个球。2罐 × 每罐3个球 = 6个球。5 + 6 = 11。",
                "answer": "11"
            }
        ]
    
    def format_prompt(self, question):
        examples = "\n\n".join([
            f"问题: {ex['question']}\n推理: {ex['reasoning']}\n答案: {ex['answer']}"
            for ex in self.few_shot_examples
        ])
        prompt = f"{examples}\n\n问题: {question}\n推理:"
        return prompt
    
    def generate(self, question):
        prompt = self.format_prompt(question)
        return self.llm.generate(prompt)

# TODO: 测试不同的CoT变体
