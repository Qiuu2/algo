---
name: "CADInterfaceAgent"
description: "CAD系统接口Agent，提供与SolidWorks/Fusion 360/CATIA等CAD系统的统一交互能力"
version: "1.0.0"
author: "ITC-Enterprise-Architecture-Team"
---

# CAD Interface Agent — Profile

## 身份定义

- **Agent ID**: `cad-interface-agent`
- **类型**: 工具层Agent
- **身份**: CAD系统接口Agent
- **所属系统**: ITC企业级多Agent协作系统

## 功能范围

| 功能域 | 说明 | 优先级 |
|--------|------|--------|
| 模型导入导出 | STEP/IGES/STL/OBJ/SLDPRT格式转换 | P0 |
| 参数查询 | 几何参数、材料属性、装配关系 | P0 |
| 几何操作 | 简化、修复、布尔运算、网格生成 | P1 |
| 版本管理 | 模型检入/检出、版本对比、变更追踪 | P1 |
| 格式转换 | CAD to simulation-ready model conversion | P0 |
| 装配管理 | BOM extraction, assembly tree, mating relations | P1 |

## 调用接口

### 入口方法 (JSON-RPC)

```json
{
  "jsonrpc": "2.0",
  "method": "cad.open",
  "params": {
    "file_path": "/models/speaker_enclosure.step",
    "options": {
      "tessellation_quality": "medium",
      "import_curves": true
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
    "model_id": "cad-20240115-001",
    "file_format": "STEP",
    "geometry_summary": {
      "body_count": 5,
      "face_count": 124,
      "edge_count": 356,
      "volume_mm3": 125000.0,
      "surface_area_mm2": 28500.0,
      "bounding_box": {
        "min": [0, 0, 0],
        "max": [200, 150, 100]
      }
    },
    "status": "loaded"
  },
  "id": 1
}
```

## 支持CAD系统

| CAD系统 | 版本 | 接口方式 | 状态 |
|---------|------|----------|------|
| SolidWorks | 2023/2024 | COM API | Connected |
| Fusion 360 | Latest | Python API | Connected |
| CATIA V5 | R2023 | CAA API | Connected |
| FreeCAD | 0.21 | Python API | Standby |

## 依赖服务

| 服务 | 用途 | 健康检查 |
|------|------|----------|
| CAD Server | CAD process management | `/health/cad` |
| File Converter | Format conversion service | `/health/converter` |
| PDM Connector | Product data management | `/health/pdm` |
