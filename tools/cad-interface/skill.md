---
name: "CADInterfaceAgent"
description: "CAD接口Agent的具体功能、API规范与协作接口"
version: "1.0.0"
author: "ITC-Enterprise-Architecture-Team"
---

# CAD Interface Agent — Skill

## 1. 支持的CAD格式

### 核心格式支持矩阵

| 格式 | 扩展名 | 读 | 写 | 用途 | 精度 |
|------|--------|----|----|------|------|
| STEP AP242 | .step/.stp | Yes | Yes | 首选交换格式 | Double |
| IGES 5.3 | .iges/.igs | Yes | Yes | 降级兼容 | Double |
| STL (Binary) | .stl | Yes | Yes | 3D打印/仿真 | Controllable |
| STL (ASCII) | .stl | Yes | Yes | 可读性 | Controllable |
| OBJ | .obj | Yes | Yes | 可视化/纹理 | Double |
| SLDPRT | .sldprt | Yes | No | SolidWorks native | Double |
| SLDASM | .sldasm | Yes | No | SolidWorks assembly | Double |
| CATPart | .CATPart | Yes | No | CATIA native | Double |
| CATProduct | .CATProduct | Yes | No | CATIA assembly | Double |
| F3D | .f3d | Yes | No | Fusion 360 native | Double |

### 格式转换推荐路径

```
SLDPRT --→ STEP AP242 --→ 任何系统
CATPart --→ STEP AP242 --→ 任何系统
F3D ----→ STEP AP242 --→ 任何系统
任何格式 --→ STL --------→ 仿真/3D打印
任何格式 --→ OBJ --------→ 可视化
```

## 2. 接口操作规范（JSON-RPC）

### 模型打开: `cad.open`

```json
{
  "jsonrpc": "2.0",
  "method": "cad.open",
  "params": {
    "file_path": "/models/enclosure.step",
    "source_system": "solidworks",
    "options": {
      "tessellation_quality": "medium",
      "import_curves": true,
      "merge_faces": false
    }
  },
  "id": "cad-req-001"
}
```

### 几何参数查询: `cad.query_geometry`

```json
{
  "jsonrpc": "2.0",
  "method": "cad.query_geometry",
  "params": {
    "model_id": "cad-20240115-001",
    "properties": [
      "volume",
      "surface_area",
      "center_of_mass",
      "bounding_box",
      "moment_of_inertia",
      "face_count",
      "edge_count"
    ]
  },
  "id": "cad-req-002"
}
```

**响应示例：**

```json
{
  "jsonrpc": "2.0",
  "result": {
    "model_id": "cad-20240115-001",
    "geometry": {
      "volume_mm3": 125000.000000,
      "surface_area_mm2": 28500.000000,
      "center_of_mass_mm": [100.000000, 75.000000, 50.000000],
      "bounding_box_mm": {
        "min": [0.000000, 0.000000, 0.000000],
        "max": [200.000000, 150.000000, 100.000000]
      },
      "moment_of_inertia_kgmm2": [
        [1.250e6, 0, 0],
        [0, 2.083e6, 0],
        [0, 0, 1.667e6]
      ],
      "face_count": 124,
      "edge_count": 356,
      "solid_count": 5,
      "shell_count": 0
    }
  }
}
```

### 模型导出: `cad.export`

```json
{
  "jsonrpc": "2.0",
  "method": "cad.export",
  "params": {
    "model_id": "cad-20240115-001",
    "output_format": "stl",
    "output_path": "/output/enclosure_mesh.stl",
    "options": {
      "tessellation_quality": "high",
      "max_edge_length_mm": 2.0,
      "min_edge_length_mm": 0.5,
      "surface_deviation_mm": 0.05
    }
  }
}
```

### 版本管理: `cad.version_checkin`

```json
{
  "jsonrpc": "2.0",
  "method": "cad.version_checkin",
  "params": {
    "model_id": "cad-20240115-001",
    "comment": "Updated port diameter to 50mm",
    "auto_increment": true
  }
}
```

```json
{
  "jsonrpc": "2.0",
  "method": "cad.version_checkout",
  "params": {
    "file_path": "/models/enclosure.step",
    "version": "latest",
    "exclusive": true
  }
}
```

### 版本对比: `cad.version_compare`

```json
{
  "jsonrpc": "2.0",
  "method": "cad.version_compare",
  "params": {
    "model_id": "cad-20240115-001",
    "version_a": "v1.2",
    "version_b": "v1.3",
    "compare_options": {
      "geometry_tolerance_mm": 0.01,
      "check_mass_properties": true,
      "visual_diff": true
    }
  }
}
```

## 3. 几何参数提取规范

### 提取参数清单

| 参数 | 单位 | 提取方法 | 精度 |
|------|------|----------|------|
| 体积 (Volume) | mm^3 | 几何内核计算 | 1e-6 |
| 表面积 (Surface Area) | mm^2 | 面片积分 | 1e-6 |
| 重心 (Center of Mass) | mm | 体积加权平均 | 1e-6 |
| 边界框 (Bounding Box) | mm | 极值坐标 | 1e-6 |
| 惯性矩 (Moment of Inertia) | kg*mm^2 | 密度*体积积分 | 1e-4 |
| 面数 (Face Count) | count | 拓扑遍历 | Integer |
| 边数 (Edge Count) | count | 拓扑遍历 | Integer |
| 最小曲率半径 | mm | 曲面分析 | 1e-3 |

### 材料属性传递

```json
{
  "material": {
    "name": "ABS_Plastic",
    "density_kg_m3": 1050.0,
    "youngs_modulus_pa": 2.3e9,
    "poisson_ratio": 0.35,
    "yield_strength_pa": 4.0e7
  }
}
```

## 4. 版本管理规范

### 版本命名规则

```
v{major}.{minor}.{patch}

major: 重大设计变更
minor: 参数调整、特征修改
patch: 修复、注释更新
```

### 版本操作状态机

```
        checkout                 checkin
[LOCKED] --------→ [CHECKED_OUT] --------→ [LOCKED]
                    |
                    | cancel
                    v
                 [LOCKED]
```

## 5. 协作接口

### 与结构Agent的协作接口

```json
{
  "interface": "cad-to-structural",
  "data_format": {
    "geometry_file": "/shared/enclosure.step",
    "material_properties": {
      "density": "kg/m3",
      "youngs_modulus": "Pa",
      "poisson_ratio": "dimensionless"
    },
    "boundary_conditions": {
      "fixed_faces": ["face_id_list"],
      "load_faces": ["face_id_list"],
      "load_values_N": ["vector_list"]
    },
    "mesh_requirements": {
      "max_element_size_mm": 5.0,
      "min_element_size_mm": 1.0,
      "element_type": "tet4|tet10|hex8"
    }
  }
}
```

### 与声学仿真Agent的协作接口

```json
{
  "interface": "cad-to-acoustic",
  "data_format": {
    "simulation_ready_model": "/shared/enclosure_acoustic.stl",
    "acoustic_surfaces": {
      "radiating_surface": ["face_ids"],
      "rigid_surface": ["face_ids"],
      "absorbing_surface": ["face_ids"]
    },
    "acoustic_ports": [
      {
        "port_id": "p1",
        "location_mm": [100, 75, 100],
        "normal": [0, 0, 1],
        "diameter_mm": 50.0
      }
    ],
    "mesh_quality": {
      "max_edge_length_mm": 2.0,
      "surface_deviation_mm": 0.05
    }
  }
}
```

## 6. 错误码体系

| 错误码 | 类别 | 说明 |
|--------|------|------|
| `C1001` | 文件错误 | 文件不存在或不可访问 |
| `C1002` | 格式错误 | 不支持的文件格式 |
| `C1003` | 许可错误 | CAD系统许可证不可用 |
| `C1004` | 文件损坏 | 文件解析失败 |
| `C2001` | 转换错误 | 格式转换失败 |
| `C2002` | 几何错误 | 几何体损坏或无效 |
| `C2003` | 拓扑错误 | 拓扑关系不一致 |
| `C3001` | 精度警告 | 转换精度损失 |
| `C3002` | 体积偏差 | 转换前后体积差异超限 |
| `C4001` | 版本错误 | 检出冲突或版本不存在 |
| `C4002` | PDM错误 | 产品数据管理系统错误 |
| `C9001` | 系统错误 | 内部服务错误 |
