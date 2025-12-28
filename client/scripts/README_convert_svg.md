使用说明：将 SVG 渲染为 PNG

1) 安装依赖：

```bash
pip install cairosvg
```

2) 在项目根目录运行脚本：

```bash
python client/scripts/convert_svg_to_png.py --input client/images/tab --size 64 --delete
```

参数说明：
- `--input` 指定包含 SVG 的目录（必填）。
- `--size` 输出 PNG 的宽高（默认 64，方形）。
- `--delete` 转换成功后删除原 SVG（可选）。

注意：Windows 下在 CMD 中使用路径时请注意反斜杠或使用双引号。
