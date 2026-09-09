#!/usr/bin/env python3
"""
tinyshell — 参照 xv6 sh.c + bash 的迷你 Shell

参照：xv6 (sh.c 350行) + bash
csdiy 对应：os-程序员视角 §三(fork-exec-wait) + CSAPP Ch8(异常控制流)

功能：命令解析 → fork+exec → 管道 → 重定向 → 内建命令
"""
import os, sys, shlex

def run_pipeline(commands, env=None):
    """执行管道命令 [cmd1 | cmd2 | ...]，参照 xv6 runcmd 的 PIPE 分支"""
    n = len(commands)
    if n == 1:
        return run_single(commands[0], env, sys.stdin.fileno(), sys.stdout.fileno())

    pipes = [os.pipe() for _ in range(n - 1)]
    pids = []
    for i, cmd in enumerate(commands):
        pid = os.fork()
        if pid == 0:  # 子进程
            # stdin：第一个用原 stdin，其余读前一个管道
            if i > 0:
                os.dup2(pipes[i-1][0], 0)
            # stdout：最后一个用原 stdout，其余写后一个管道
            if i < n - 1:
                os.dup2(pipes[i][1], 1)
            # 关闭所有管道 fd（参照 xv6 sh.c close 逻辑）
            for r, w in pipes:
                os.close(r); os.close(w)
            # 处理重定向
            args = handle_redirect(cmd)
            try:
                os.execvpe(args[0], args, env or os.environ)
            except FileNotFoundError:
                sys.stderr.write(f"tinyshell: {args[0]}: not found\n")
                os._exit(127)
        pids.append(pid)

    for r, w in pipes:
        os.close(r); os.close(w)
    for pid in pids:
        os.waitpid(pid, 0)

def handle_redirect(args):
    """处理 > < >> 重定向（参照 bash redirect）"""
    result = []
    i = 0
    while i < len(args):
        if args[i] == '>' and i + 1 < len(args):
            fd = os.open(args[i+1], os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o644)
            os.dup2(fd, 1); os.close(fd); i += 2
        elif args[i] == '<' and i + 1 < len(args):
            fd = os.open(args[i+1], os.O_RDONLY)
            os.dup2(fd, 0); os.close(fd); i += 2
        elif args[i] == '>>' and i + 1 < len(args):
            fd = os.open(args[i+1], os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o644)
            os.dup2(fd, 1); os.close(fd); i += 2
        else:
            result.append(args[i]); i += 1
    return result

def run_single(args, env, stdin_fd, stdout_fd):
    """执行单条命令（参照 xv6 sh.c 的 exec 分支）"""
    builtin = args[0]
    if builtin == 'cd':
        os.chdir(args[1] if len(args) > 1 else os.path.expanduser('~'))
        return
    if builtin == 'pwd':
        print(os.getcwd()); return
    if builtin == 'exit':
        sys.exit(int(args[1]) if len(args) > 1 else 0)
    if builtin == 'export':
        if len(args) > 1 and '=' in args[1]:
            k, v = args[1].split('=', 1)
            os.environ[k] = v
        return
    if builtin == 'echo':
        # 简化版 echo
        print(' '.join(args[1:])); return

    pid = os.fork()
    if pid == 0:
        args = handle_redirect(args)
        try:
            os.execvpe(args[0], args, env or os.environ)
        except FileNotFoundError:
            sys.stderr.write(f"tinyshell: {args[0]}: not found\n")
            os._exit(127)
    os.waitpid(pid, 0)

def main():
    print("tinyshell v1.0 — 参照 xv6 sh.c (Ctrl+D to exit)")
    while True:
        try:
            cwd = os.getcwd().replace(os.path.expanduser('~'), '~')
            line = input(f"tinyshell:{cwd}$ ").strip()
            if not line:
                continue
            # 解析管道（参照 bash 的 | 分割）
            pipe_parts = [shlex.split(p) for p in line.split('|')]
            if len(pipe_parts) == 1:
                run_single(pipe_parts[0], None, 0, 1)
            else:
                run_pipeline(pipe_parts, None)
        except EOFError:
            print("\nbye"); break
        except KeyboardInterrupt:
            print("^C")
        except Exception as e:
            print(f"tinyshell: {e}")

if __name__ == "__main__":
    main()
