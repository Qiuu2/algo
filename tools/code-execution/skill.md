---
name: "CodeExecutionAgent"
description: "代码执行Agent的具体功能、API规范与安全沙箱规则"
version: "1.0.0"
author: "ITC-Enterprise-Architecture-Team"
---

# Code Execution Agent — Skill

## 1. 支持的执行环境

### Python 3.11 环境

```yaml
runtime: python:3.11-slim
gcc: 11.4
os: Debian 12 (bookworm)
```

### MATLAB Runtime

```yaml
runtime: MATLAB_Runtime_R2023b
engine_api: python-matlab-bridge
toolbox_support:
  - Signal_Processing
  - DSP_System
  - Optimization
  - Statistics_and_Machine_Learning
```

### GCC C编译环境

```yaml
compiler: gcc 11.4
flags: "-O2 -Wall -Wextra -fstack-protector-strong"
sandbox: seccomp-bpf + chroot
```

## 2. 预装库清单

### 科学计算与数据处理

| 库名 | 版本 | 用途 |
|------|------|------|
| NumPy | 1.26.x | 数值计算、数组操作 |
| SciPy | 1.11.x | 科学计算、信号处理 |
| Pandas | 2.1.x | 数据框处理、CSV/Excel读写 |
| Matplotlib | 3.8.x | 数据可视化 |
| Plotly | 5.18.x | 交互式图表 |

### 音频处理专用库

| 库名 | 版本 | 用途 |
|------|------|------|
| Librosa | 0.10.x | 音频特征提取、STFT、MFCC |
| PyAudioAnalysis | 0.3.x | 音频分类、分割、特征分析 |
| SoundFile | 0.12.x | 音频文件读写（WAV/FLAC/OGG） |
| TorchAudio | 2.1.x | 深度学习音频处理 |

### 其他工具库

| 库名 | 版本 | 用途 |
|------|------|------|
| Requests | 2.31.x | HTTP调用（需白名单） |
| PyYAML | 6.0.x | YAML配置解析 |
| python-jsonrpc | 2.0.x | JSON-RPC服务端 |
| pytest | 7.4.x | 单元测试执行 |
| coverage | 7.3.x | 代码覆盖率分析 |

## 3. 执行接口规范（JSON-RPC）

### 主执行接口: `execute`

**请求格式：**

```json
{
  "jsonrpc": "2.0",
  "method": "execute",
  "params": {
    "language": "python",
    "code": "aW1wb3J0IG51bXB5IGFzIG5wCgpuID0gbnAuYXJyYW5nZSgxMDApCnByaW50KGYibWVhbj17bnAubWVhbihuKX0iKQo=",
    "inputs": {
      "data_file": "/input/signal.csv",
      "sample_rate": 48000
    },
    "timeout": 30,
    "resource_limits": {
      "memory_mb": 512,
      "cpu_percent": 80,
      "disk_mb": 100
    },
    "tags": ["signal_processing", "batch_001"]
  },
  "id": "req-uuid-001"
}
```

**参数说明：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `language` | string | 是 | 执行语言：`python` / `matlab` / `c` |
| `code` | string(base64) | 是 | Base64编码的源代码 |
| `inputs` | object | 否 | 输入参数/文件路径映射 |
| `timeout` | int | 否 | 超时秒数，默认30，最大300 |
| `resource_limits` | object | 否 | 资源限制配置 |
| `tags` | string[] | 否 | 执行标签，用于分类和检索 |

**成功响应：**

```json
{
  "jsonrpc": "2.0",
  "result": {
    "execution_id": "ce-20240115-001",
    "exit_code": 0,
    "stdout": "mean=49.5\n",
    "stderr": "",
    "outputs": {
      "result_value": 49.5,
      "output_files": ["/output/plot.png"]
    },
    "execution_time_ms": 1523,
    "resource_usage": {
      "memory_peak_mb": 245,
      "cpu_time_ms": 890,
      "disk_read_mb": 2.1,
      "disk_write_mb": 5.4
    },
    "timestamp_start": "2024-01-15T09:30:00Z",
    "timestamp_end": "2024-01-15T09:30:02Z"
  },
  "id": "req-uuid-001"
}
```

**错误响应：**

```json
{
  "jsonrpc": "2.0",
  "error": {
    "code": -32001,
    "message": "Execution timeout",
    "data": {
      "itc_error_code": "E2001",
      "execution_id": "ce-20240115-002",
      "partial_stdout": "Processing batch 1/10...",
      "resource_usage": {
        "memory_peak_mb": 510,
        "cpu_time_ms": 30000
      }
    }
  },
  "id": "req-uuid-001"
}
```

### 查询接口: `get_status`

```json
{
  "jsonrpc": "2.0",
  "method": "get_status",
  "params": {
    "execution_id": "ce-20240115-001"
  },
  "id": "req-uuid-002"
}
```

### 历史查询接口: `get_history`

```json
{
  "jsonrpc": "2.0",
  "method": "get_history",
  "params": {
    "tags": ["signal_processing"],
    "time_range": {
      "from": "2024-01-01T00:00:00Z",
      "to": "2024-01-15T23:59:59Z"
    },
    "limit": 50,
    "offset": 0
  },
  "id": "req-uuid-003"
}
```

## 4. 安全沙箱规则

### 网络策略

```yaml
network_policy: DENY_ALL
exceptions:
  - host: "pypi.org"
    port: 443
    purpose: "pip install dependency installation"
  - host: "files.pythonhosted.org"
    port: 443
    purpose: "Python package download"
```

### 文件系统策略

```yaml
rootfs: read_only
allowed_mounts:
  /input:
    mode: ro
    max_size: 100MB
  /output:
    mode: rw
    max_size: 500MB
  /tmp:
    mode: rw
    max_size: 100MB
forbidden_paths:
  - /etc/passwd
  - /proc
  - /sys
  - /dev
  - /var/run/docker.sock
```

### 系统调用过滤 (seccomp)

```yaml
seccomp_profile: default_deny
allowed_syscalls:
  - read/write/open/close
  - mmap/munmap/mprotect
  - clone/wait4/exit
  - futex/nanosleep
  - getrandom
forbidden_syscalls:
  - socket/connect/accept
  - execve/execveat
  - ptrace
  - mount/umount
```

## 5. 错误码体系

| 错误码 | 类别 | 说明 | HTTP映射 |
|--------|------|------|----------|
| `E1001` | 验证错误 | 代码语法错误 | 400 |
| `E1002` | 验证错误 | 依赖/库未在白名单 | 400 |
| `E1003` | 验证错误 | 权限越界/恶意代码 | 403 |
| `E1004` | 验证错误 | 资源限制配置无效 | 400 |
| `E2001` | 执行错误 | 超时终止 | 504 |
| `E2002` | 执行错误 | 内存溢出 | 507 |
| `E2003` | 执行错误 | CPU使用率超限 | 503 |
| `E2004` | 执行错误 | 容器启动失败 | 500 |
| `E3001` | 输出错误 | 运行时异常 | 500 |
| `E3002` | 输出错误 | 输出序列化失败 | 500 |
| `E3003` | 输出错误 | 输出文件过大 | 413 |
| `E9001` | 系统错误 | 内部服务错误 | 500 |
| `E9002` | 系统错误 | 依赖服务不可用 | 503 |

## 6. 执行历史与缓存机制

### 代码指纹

```python
def compute_code_fingerprint(language: str, code: str, inputs_hash: str) -> str:
    content = f"{language}:{code}:{inputs_hash}"
    return hashlib.sha256(content.encode()).hexdigest()[:16]
```

### 缓存策略

```yaml
cache_policy:
  enabled: true
  ttl_seconds: 3600
  max_entries: 1000
  cache_conditions:
    - "language == 'python'"
    - "resource_limits.memory_mb <= 1024"
  cache_key: "{code_fingerprint}:{inputs_hash}"
```

### 缓存命中响应

```json
{
  "jsonrpc": "2.0",
  "result": {
    "execution_id": "ce-20240115-001",
    "cache_hit": true,
    "cached_at": "2024-01-15T08:00:00Z",
    "exit_code": 0,
    "outputs": {}
  }
}
```
