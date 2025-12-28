"""client/scripts/generate_tab_pngs.py

生成 64x64 tab 图标并写入 client/images/tab/ 下。

- 未选中：灰色（与 client/app.json 的 tabBar.color 一致）
- 选中：蓝色（与 client/app.json 的 tabBar.selectedColor 一致）

运行：
    pip install pillow
    python client/scripts/generate_tab_pngs.py
"""
from PIL import Image, ImageDraw
import os

OUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'images', 'tab')
OUT_DIR = os.path.abspath(OUT_DIR)
ICONS = [
    'home',
    'route',
    'activities',
    'search',
    'user'
]
SIZE = 64

# Colors aligned with client/app.json
INACTIVE = (0x66, 0x66, 0x66, 0xFF)  # #666666
ACTIVE = (0x18, 0x90, 0xFF, 0xFF)    # #1890ff
TRANSPARENT = (0, 0, 0, 0)

os.makedirs(OUT_DIR, exist_ok=True)

def save(name, img):
    path = os.path.join(OUT_DIR, f"{name}.png")
    img.save(path, format='PNG')
    print('Wrote', path)

def draw_home(color):
    img = Image.new('RGBA', (SIZE, SIZE), TRANSPARENT)
    d = ImageDraw.Draw(img)
    d.polygon([(8, 28), (32, 8), (56, 28)], fill=color)
    d.rectangle([(16, 28), (48, 52)], fill=color)
    # Cut-out door to avoid introducing a non-gray/blue color block
    d.rectangle([(28, 36), (36, 52)], fill=TRANSPARENT)
    return img

def draw_route(color):
    img = Image.new('RGBA', (SIZE, SIZE), TRANSPARENT)
    d = ImageDraw.Draw(img)
    d.line([(10, 54), (22, 40), (36, 32), (54, 14)], fill=color, width=6)
    d.ellipse([(6, 50), (14, 58)], fill=color)
    d.ellipse([(50, 10), (58, 18)], fill=color)
    return img

def draw_activities(color):
    img = Image.new('RGBA', (SIZE, SIZE), TRANSPARENT)
    d = ImageDraw.Draw(img)
    d.ellipse([(20, 8), (44, 32)], fill=color)
    d.rectangle([(12, 36), (52, 50)], fill=color)
    return img

def draw_search(color):
    img = Image.new('RGBA', (SIZE, SIZE), TRANSPARENT)
    d = ImageDraw.Draw(img)
    d.ellipse([(10, 10), (36, 36)], outline=color, width=6)
    d.line([(34, 34), (54, 54)], fill=color, width=6)
    return img

def draw_user(color):
    img = Image.new('RGBA', (SIZE, SIZE), TRANSPARENT)
    d = ImageDraw.Draw(img)
    d.ellipse([(18, 8), (46, 36)], fill=color)
    d.rectangle([(12, 34), (52, 54)], fill=color)
    return img


# Inactive (gray)
save('home', draw_home(INACTIVE))
save('route', draw_route(INACTIVE))
save('activities', draw_activities(INACTIVE))
save('search', draw_search(INACTIVE))
save('user', draw_user(INACTIVE))

# Active (blue)
save('home-active', draw_home(ACTIVE))
save('route-active', draw_route(ACTIVE))
save('activities-active', draw_activities(ACTIVE))
save('search-active', draw_search(ACTIVE))
save('user-active', draw_user(ACTIVE))

print('All icons generated.')
