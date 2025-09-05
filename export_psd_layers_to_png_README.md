## 导出 PSD 图层为 PNG（export_psd_layers_to_png.py）

说明如何将 PSD 中的“未锁定”图层批量导出为 PNG 文件。

### 功能

- 递归遍历所有图层（包含分组内的子图层）。
- 跳过分组层，仅导出具体可渲染的图层。
- 跳过“已锁定”的图层（基于 PROTECTED_SETTING/lspf 判断，任一保护位视作锁定）。
- 默认仅导出“可见”图层；可通过参数包含隐藏图层。
- 过滤字体（文字）图层，仅导出图片类图层。
- 导出文件名严格等于图层名（清理非法字符），不再附加 bbox 后缀。
- 输出目录默认为 `./layout/png/`，不存在将自动创建。

### 环境与依赖

- Python 3.10+
- 依赖见 `requirements.txt`（psd-tools、Pillow 等）

安装依赖（PowerShell）：

```bash
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip setuptools wheel
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### 运行方式

在项目根目录执行（以 `continue.psd` 为例）：

- 导出未锁定且可见的图层到默认目录 `./layout/png/`：

```bash
.\.venv\Scripts\python.exe export_psd_layers_to_png.py continue.psd
# 默认输出：./layout/png/
```

- 包含隐藏图层一并导出：

```bash
.\.venv\Scripts\python.exe export_psd_layers_to_png.py continue.psd --include-hidden
# 输出目录仍为：./layout/png/
```

- 指定其它输出目录（例如 `out_png`）：

```bash
.\.venv\Scripts\python.exe export_psd_layers_to_png.py continue.psd --out-dir out_png
```

### 命令行参数

- `psd`（必填）: 输入 PSD 文件路径（如 `continue.psd`）。
- `--out-dir`（可选）: 输出目录，默认 `./layout/png`。
- `--include-hidden`（可选）: 包含隐藏图层（默认不导出隐藏图层）。

### 导出规则与命名

- 锁定图层：若 `PROTECTED_SETTING (lspf)` 存在且任一保护位为 1，则视为锁定并跳过。
- 文字图层：检测为文字图层（如 `TextLayer`/`kind=="type"`/`TySh` 数据）将被跳过，不导出。
- 空像素/零尺寸：渲染后宽高为 0 的图层会被跳过。
- 文件命名：`<清理后的图层名>.png`，非法文件名字符会被替换为下划线 `_`。
- 坐标系：bbox 相对 PSD 画布左上角（仅做说明，命名中不再使用）。

### 常见提示

- 运行时若出现 `Unknown tagged block` / `Unknown key` 等警告，一般可忽略，不影响导出。
- 如果某些图层没有像素或仅为容器（分组），不会导出 PNG。可在 PSD 中栅格化或检查可见性后重试。
