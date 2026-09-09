
class PPO:
    def __init__(self, actor_critic, clip_ratio=0.2, target_kl=0.01):
        self.actor_critic = actor_critic
        self.clip_ratio = clip_ratio
        self.target_kl = target_kl
        self.optimizer = torch.optim.Adam(actor_critic.parameters(), lr=3e-4)
    
    def compute_loss(self, batch):
        states, actions, old_logp, advantages, returns = batch
        
        # 计算新的策略概率
        pi, value = self.actor_critic(states)
        logp = self.actor_critic.get_log_prob(pi, actions)
        
        # 计算比率
        ratio = torch.exp(logp - old_logp)
        
        # PPO clipped损失
        surr1 = ratio * advantages
        surr2 = torch.clamp(ratio, 1 - self.clip_ratio, 1 + self.clip_ratio) * advantages
        policy_loss = -torch.min(surr1, surr2).mean()
        
        # 价值函数损失
        value_loss = F.mse_loss(value, returns)
        
        # KL散度惩罚
        approx_kl = (old_logp - logp).mean()
        
        return policy_loss + value_loss - 0.5 * approx_kl

# TODO: 实现训练循环和GAE
