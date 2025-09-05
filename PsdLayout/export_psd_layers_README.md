## PSD 图层导出脚本（export_psd_layers.py）

导出指定 PSD 文件中的图层名称与坐标信息，并以 JSON 格式输出。

### 功能

- 递归遍历所有图层（包含分组中的图层）。
- 支持过滤隐藏图层或将其包含在输出中（`--include-hidden`）。
- 自动过滤锁定图层（基于 PROTECTED_SETTING/lspf 或 flags.transparency_protected）。
- 自动过滤字体（文字）图层，仅导出图片类图层的信息。
- 支持以图层左上角或中心点导出坐标（`--center`）。
- 输出每个图层的名称（保持与 PSD 中一致，不附加后缀）、完整分组路径、坐标与尺寸信息。

### 环境与依赖
- 需要 Python（建议 3.10+）。
- 依赖位于 `requirements.txt`：`psd-tools`、`Pillow`。

安装依赖（PowerShell）：
```bash
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip setuptools wheel
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### 使用方法

在项目根目录（包含 `continue.psd` 的目录）执行：

- 导出为默认文件 `<psd名>_layers.json`，坐标为左上角：

```bash
.\.venv\Scripts\python.exe export_psd_layers.py continue.psd
# 默认输出：./layout/<psd名>_layers.json
```

- 指定输出文件名：

```bash
.\.venv\Scripts\python.exe export_psd_layers.py continue.psd --out out.json
# 指定输出将覆盖默认 ./layout/
```

- 包含隐藏图层：

```bash
.\.venv\Scripts\python.exe export_psd_layers.py continue.psd --include-hidden
```

- 使用图层中心点作为坐标（x,y）：

```bash
.\.venv\Scripts\python.exe export_psd_layers.py continue.psd --center
```

- 组合参数示例（中心点 + 指定输出）：

```bash
.\.venv\Scripts\python.exe export_psd_layers.py continue.psd --center --out continue_layers_center.json
```

### 命令行参数
- `psd`（必填）: PSD 文件路径（例如 `continue.psd`）。
- `--out`（可选）: 输出 JSON 路径，默认 `./layout/<psd_basename>_layers.json`。
- `--include-hidden`（可选）: 包含隐藏图层。
- `--center`（可选）: 将 `x,y` 输出为图层中心点坐标（默认输出为左上角）。

### 输出字段说明

每个图层对象包含：

- `name`: 图层名称（保持原始图层名，不做扩展或拼接）。
- `path`: 图层完整分组路径（以 `/` 连接）。
- `x`, `y`: 坐标（像素）。默认为左上角；若加 `--center`，则为中心点。
- `width`, `height`: 图层的像素宽高。

坐标均相对于 PSD 画布左上角，单位为像素。

### 注意事项
- 若运行时出现 `Unknown tagged block` / `Unknown key` 等警告，通常可忽略，不影响图层与坐标解析。
- 空区域图层（宽高为 0）会被跳过。
- 分组会体现在 `path` 字段中，便于在层级中定位图层。
