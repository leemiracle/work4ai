# Kubernetes · 救火场景速查

> 一行场景 → 一条 kubectl。Pod 起不来先 describe，再 logs，再 exec。

## 🚨 最常用 5 条
```bash
kubectl get pods -A                              # 全集群 Pod 状态一览
kubectl describe pod <pod> -n <ns>              # Pod 不起看事件（90% 答案在这）
kubectl logs <pod> -n <ns> --previous            # 看上次崩之前的日志
kubectl exec -it <pod> -n <ns> -- sh            # 进容器里查现场
kubectl get events -n <ns> --sort-by=.lastTimestamp  # 按时间看事件流
```

---

## Pod 不起 / Crash / OOM
```bash
kubectl get pod <pod> -o wide                   # 看 Node、IP、重启次数、状态
kubectl describe pod <pod>                      # 最关键：末尾 Events 显示拉镜像/调度/健康检查失败原因
kubectl logs <pod>                              # 当前容器日志
kubectl logs <pod> --previous                   # 上次崩溃前的日志（崩了重启看不到当前的就用这个）
kubectl logs <pod> -c <container>               # 多容器 Pod 指定容器
kubectl logs <pod> --tail=100 -f                # 跟踪最后 100 行
kubectl exec -it <pod> -- sh                    # 进容器（没 sh 用 bash、或 distroless 改用 debug image）
kubectl exec -it <pod> -- cat /proc/1/status    # 看 OOM 信号（VmRSS / OOM score）
kubectl get pod <pod> -o jsonpath='{.status.containerStatuses[0].state}'  # 看 Waiting/Running/Terminated 原因
```

### 按状态定位原因
```
Pending            → describe 看 Events：通常是没资源 / nodeSelector 不匹配 / PVC 没绑 / 镜像太大拉不动
CrashLoopBackOff   → logs --previous 看启动报错；常见：配置错/依赖服务没起/启动检查失败
OOMKilled          → describe 里 Last State: Terminated Reason=OOMKilled；调高 resources.limits.memory
ImagePullBackOff   → 镜像名/标签错 / 私有仓库没配 imagePullSecrets / 网络到不了 registry
ErrImageNeverPull  → Never/IfNotPresent 策略但本地没镜像
Completed          → Job/任务正常跑完（不是故障）
```

### 排查技巧
```bash
kubectl get pods -A --field-selector=status.phase!=Running   # 一键列出所有非 Running
kubectl get pods -A -o wide | grep -iE 'OOM|Crash|Pull'      # 集群扫一遍出问题的
kubectl get events -n <ns> --sort-by=.metadata.creationTimestamp | tail -20  # 最近 20 条事件
kubectl get pod <pod> -o yaml                  # 全量 yaml，看环境变量/挂载/探针是否注入对
```

---

## 资源（requests / limits / QoS / HPA）
```bash
kubectl describe node <node>                    # Allocatable / Allocated resources 看节点余量
kubectl top nodes                               # 实时各节点 CPU/内存（需装 metrics-server）
kubectl top pods -A --sort-by=cpu               # 全集群 CPU 占用 Top
kubectl top pod <pod> --containers              # Pod 内每个容器占用
```

### requests/limits 设置
```yaml
resources:
  requests:            # 调度依据， Guaranteed/Burstable 取决于 requests==limits
    cpu: "500m"        # 1 核 = 1000m
    memory: "512Mi"
  limits:
    cpu: "2000m"       # 可突发到 2 核
    memory: "1Gi"      # 超了 → OOMKilled，不超就杀
# QoS 等级（影响驱逐顺序）：
#   Guaranteed  : requests==limits（CPU+内存都等）→ 最后被驱逐
#   Burstable   : 至少一个有 request → 中间
#   BestEffort  : 完全不设 → 节点紧时第一个被杀
kubectl get pod <pod> -o jsonpath='{.status.qosClass}'
```

### HPA（水平自动扩缩）
```bash
kubectl autoscale deployment <dep> --cpu-percent=70 --min=2 --max=10   # CPU 超 70% 自动扩
kubectl get hpa                                  # 看当前副本数、目标、能否扩
kubectl describe hpa <hpa>                       # 看 Events：为什么没扩（指标没采到/到上限）
# 前提：deployment 必须设 resources.requests.cpu，否则 HPA 拿不到利用率
```

### VPA（垂直自动调资源）
```bash
kubectl get vpa -A                               # 看是否开启自动调 requests/limits
kubectl describe vpa <vpa> | grep -A5 Recommendation   # 看 VPA 建议的资源值
# 注意：VPA Update 模式会重启 Pod 应用新值；初装用 Off/Initial 模式只看建议
```

---

## 网络（Service / DNS / Ingress / NetworkPolicy）
```bash
kubectl get svc -A                               # 看 Service 类型、ClusterIP、端口
kubectl get endpoints <svc> -n <ns>             # 后端 Pod 是否被选中（空 = 选择器错/Pod 没 ready）
kubectl describe svc <svc> -n <ns>              # 看选择器、目标端口
kubectl get ingress -A                           # 看七层路由规则
kubectl get networkpolicy -A                     # 看是否被 NetworkPolicy 限住
```

### DNS 排查
```bash
kubectl exec -it <pod> -- nslookup kubernetes.default    # 域名能解析否
kubectl exec -it <pod> -- cat /etc/resolv.conf           # 看 nameserver 是不是 coredns
kubectl get pods -n kube-system -l k8s-app=kube-dns      # CoreDNS 是否 Running
kubectl logs -n kube-system <coredns-pod>                # CoreDNS 解析报错
kubectl exec -it <pod> -- nslookup <svc>.<ns>.svc.cluster.local   # 完整 FQDN
# 常见：跨 namespace 访问要用 <svc>.<ns>；ndots:5 导致多查 → 业务 pod 用 FQDN 或调 dnsConfig
```

### 连不上 / conntrack 满
```bash
kubectl exec -it <pod> -- curl -v <svc>:<port>   # 进 Pod 里直连验证
kubectl exec -it <pod> -- wget -qO- <ip>         # 没有 curl 用 wget
# 大量连接失败 + 节点上 dmesg 报 "nf_conntrack: table full, dropping packet"
ssh <node>; sudo dmesg | grep conntrack          # 节点内核日志
sudo sysctl net.netfilter.nf_conntrack_max       # 当前上限，通常调大到 100w+
# CoreDNS 解析慢：conntrack 满 / ndots 高 → 改 Pod dnsPolicy: ClusterFirst 并用 FQDN
```

---

## 存储（PV / PVC / StorageClass / 强删）
```bash
kubectl get pv                                   # 集群级持久卷
kubectl get pvc -A                               # 各命名空间 PVC 绑定状态
kubectl get sc                                   # 存储类（默认带 (default) 标记）
kubectl describe pvc <pvc> -n <ns>              # Bound 不了看 Events
```

### stuck Terminating 强删
```bash
kubectl delete pod <pod> -n <ns> --force --grace-period=0    # Pod 卡 Terminating 强删
kubectl delete pvc <pvc> -n <ns> --force                      # PVC 强删（finalize 没清掉时）
# 还有 finalizer 卡住：编辑去掉 finalizers 字段
kubectl patch pvc <pvc> -n <ns> -p '{"metadata":{"finalizers":null}}'
kubectl patch pod <pod> -n <ns> -p '{"metadata":{"finalizers":null}}'
# 注意：这是绕过 K8s 的最后手段，确认底层存储已不需要再删
```

### 常见问题
```
PVC Pending      → describe 看 Events；StorageClass 没有 provisioner / 配额满 / 节点没本地盘
PV Released      → 旧 Pod 删了，PV 还留着数据（reclaimPolicy=Retain）；要复用改 claimRef
AccessMode 冲突  → RWO 只能挂一个节点；多 Pod 跨节点要 RWX/ROX
```

---

## 滚动发布
```bash
kubectl rollout status deployment/<dep> -n <ns>      # 看滚动是否完成
kubectl rollout history deployment/<dep> -n <ns>     # 看历史版本
kubectl rollout history deployment/<dep> --revision=3   # 看第 3 版的具体 yaml
kubectl rollout undo deployment/<dep> -n <ns>        # 回滚到上一版
kubectl rollout undo deployment/<dep> --to-revision=2   # 回滚到指定版本
kubectl rollout pause deployment/<dep>               # 暂停（改一部分先观察）
kubectl rollout resume deployment/<dep>              # 恢复
kubectl scale deployment/<dep> --replicas=5          # 手动扩缩
```

### maxSurge / maxUnavailable 取舍
```yaml
strategy:
  type: RollingUpdate
  rollingUpdate:
    maxSurge: 1            # 滚动时最多多出 1 个（需要节点有余量）
    maxUnavailable: 0      # 0 = 永远保持可用副本数（不丢请求）；大 = 快但可能短时不可用
# 想零停机：maxUnavailable=0 + maxSurge=1 + readinessProbe 配好
# 想快发：maxUnavailable=50% + maxSurge=50%
```

---

## RBAC（我到底有没有权限）
```bash
kubectl auth can-i create pods -n <ns>                       # 我能在这个 ns 建 Pod 吗
kubectl auth can-i '*' '*' --all-namespaces                   # 我是不是集群管理员
kubectl auth can-i list secrets --as=<user> -n <ns>           # 模拟某个 user 看权限
kubectl auth can-i get pods --as=system:serviceaccount:<ns>:<sa>  # 查某 ServiceAccount 权限
kubectl auth can-i --list -n <ns>                             # 列出我所有被允许的操作
```

### ServiceAccount / 绑定
```bash
kubectl get sa -n <ns>                                         # 看命名空间里的 SA
kubectl get rolebinding,clusterrolebinding -A -o wide         # 看谁绑了什么角色
kubectl get clusterrole <name> -o yaml | grep -A20 rules       # 看角色具体能干啥
kubectl auth reconcile -f rbac.yaml                            # 应用 RBAC yaml 并检查冲突
# Pod 里访问 API 没权限：检查 serviceAccountName + 对应 RoleBinding 是否在该 ns
```

---

## 集群救火
### 节点 NotReady
```bash
kubectl get nodes -o wide                                   # 看 READY 列
kubectl describe node <node>                                # 末尾 Events + Conditions
kubectl get node <node> -o jsonpath='{.status.conditions}'  # MemoryPressure/DiskPressure/PIDPressure
ssh <node>; systemctl status kubelet                        # kubelet 是否在跑
sudo journalctl -u kubelet --since "10 min ago" | tail -50  # kubelet 日志
sudo journalctl -u containerd --since "10 min ago" | tail   # 容器运行时日志
# 常见：kubelet 证书过期 / 节点内存压力驱逐 / 容器运行时崩 / CNI 插件挂
kubectl cordon <node>                                       # 暂停调度（不驱逐已有 Pod）
kubectl drain <node> --ignore-daemonsets --delete-emptydir-data  # 驱逐并准备下线
kubectl uncordon <node>                                     # 恢复调度
```

### etcd 问题
```bash
kubectl get pods -n kube-system | grep etcd                # 静态 Pod 是否 Running
# etcd 通常在 master 上以 static pod 跑
crictl logs <etcd-pod-id> 2>&1 | grep -iE 'alarm|compact|quota'   # 看报警/空间不足
# 常见：etcd db size 满（默认 2GB 配额）→ 触发告警拒绝写入 → 整个集群只读
# 解决：调大 --quota-backend-bytes，并定期 compact+defrag
# 测试集群恢复：etcdctl snapshot save / restore
ETCDCTL_API=3 etcdctl --endpoints=https://127.0.0.1:2379 \
  --cacert=/etc/kubernetes/pki/etcd/ca.crt \
  --cert=/etc/kubernetes/pki/etcd/peer.crt \
  --key=/etc/kubernetes/pki/etcd/peer.key endpoint status -w table
```

### kubelet / 控制面整体
```bash
kubectl get componentstatuses                              # scheduler/controller-manager/etcd 是否 Healthy
kubectl get --raw='/readyz?verbose'                        # 1.20+ 更详细的就绪检查
kubectl version                                            # client/server 版本，差太大会各种怪现象
# API server 慢：看 audit log、看 etcd 延迟、看是不是 list 全 namespace 大对象
kubectl get --raw='/metrics' | grep apiserver_request_duration  # API 延迟指标
```

### 集群级资源整理
```bash
kubectl api-resources                                      # 集群支持哪些资源类型
kubectl api-resources --verbs=list --namespaced -o name | xargs -n1 kubectl get -A  # 全量 dump（慎用，慢）
kubectl get all -n <ns>                                    # 该 ns 的 deploy/svc/pod 一览（不含 configmap/secret）
kubectl delete ns <ns>                                     # 删整个命名空间（内部所有资源会被 GC）
```

---
*参考：本仓库 `github-repos/references/REKCARC-TSC-UHT/`（含云原生/DevOps 课程资料）、`notes/network-程序员视角`（conntrack/epoll 原理）。*
