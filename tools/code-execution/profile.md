---
name: "CodeExecutionAgent"
description: "代码执行环境Agent，提供Python/MATLAB/C代码的安全沙箱执行能力"
version: "1.0.0"
author: "ITC-Enterprise-Architecture-Team"
---

# Code Execution Agent — Profile

## 身份定义

- **Agent ID**: `code-execution-agent`
- **类型**: 工具层Agent
- **身份**: 代码执行环境Agent
- **所属系统**: ITC企业级多Agent协作系统

## 功能范围

| 功能域 | 说明 | 优先级 |
|--------|------|--------|
| Python代码执行 | Python 3.11 安全沙箱执行 | P0 |
| MATLAB脚本执行 | MATLAB Runtime 调用执行 | P0 |
| C代码编译执行 | GCC编译+沙箱运行 | P1 |
| 数据分析 | NumPy/Pandas数据处理流水线 | P0 |
| 信号处理 | 音频/振动信号分析与变换 | P0 |
| 自动化脚本 | 工作流自动化、批量处理 | P1 |
| 单元测试 | 代码质量验证与测试报告 | P1 |

## 调用接口

### 入口方法 (JSON-RPC)

```json
{
  "jsonrpc": "2.0",
  "method": "execute",
  "params": {
    "language": "python|matlab|c",
    "code": "<base64_encoded_source_code>",
    "inputs": {},
    "timeout": 30,
    "resource_limits": {
      "memory_mb": 512,
      "cpu_percent": 80
    }
  },
  "id": 1
}
```

### 返回值格式

```json
{
  "jsonrpc": "2.0",
  "result": {
    "exit_code": 0,
    "stdout": "...",
    "stderr": "...",
    "outputs": {},
    "execution_time_ms": 1523,
    "resource_usage": {
      "memory_peak_mb": 245,
      "cpu_time_ms": 890
    }
  },
  "id": 1
}
```

## 安全策略

- **沙箱隔离**: 所有代码在独立Docker容器内执行
- **资源限制**: 内存/CPU/磁盘严格配额
- **超时控制**: 默认30秒，最大300秒
- **网络禁止**: 沙箱内禁用出站网络连接
- **文件系统限制**: 仅允许访问挂载的输入输出目录

## 依赖服务

| 服务 | 用途 | 健康检查 |
|------|------|----------|
| Docker Daemon | 容器生命周期管理 | `/health/docker` |
| Python 3.11 Runtime | Python代码执行环境 | `/health/python` |
| MATLAB Runtime | MATLAB脚本执行 | `/health/matlab` |
| GCC Compiler | C代码编译 | `/health/gcc` |