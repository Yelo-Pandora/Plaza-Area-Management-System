"""
生成 64x64 彩色 tab 图标并写入 client/images/tab/ 下。
使用 Pillow 绘制简单图形表示各图标：home, route, activities, search, user
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

os.makedirs(OUT_DIR, exist_ok=True)

def save(name, img):
    path = os.path.join(OUT_DIR, f"{name}.png")
    img.save(path, format='PNG')
    print('Wrote', path)

# Home icon: house silhouette
img = Image.new('RGBA', (SIZE, SIZE), (255,255,255,0))
d = ImageDraw.Draw(img)
# roof
d.polygon([(8,28),(32,8),(56,28)], fill=(34,170,25,255))
# body
d.rectangle([(16,28),(48,52)], fill=(34,170,25,255))
# door
d.rectangle([(28,36),(36,52)], fill=(255,255,255,255))
save('home', img)

# Route icon: curved path
img = Image.new('RGBA',(SIZE,SIZE),(255,255,255,0))
d = ImageDraw.Draw(img)
# path strokes
d.line([(10,54),(22,40),(36,32),(54,14)], fill=(136,136,136,255), width=6)
# start/end dots
d.ellipse([(6,50),(14,58)], fill=(26,26,26,255))
d.ellipse([(50,10),(58,18)], fill=(26,170,25,255))
save('route', img)

# Activities icon: circle + bar
img = Image.new('RGBA',(SIZE,SIZE),(255,255,255,0))
d = ImageDraw.Draw(img)
# circle
d.ellipse([(20,8),(44,32)], fill=(34,170,25,255))
# bar
d.rectangle([(12,36),(52,50)], fill=(34,170,25,255))
save('activities', img)

# Search icon: magnifier
img = Image.new('RGBA',(SIZE,SIZE),(255,255,255,0))
d = ImageDraw.Draw(img)
# circle
d.ellipse([(10,10),(36,36)], outline=(136,136,136,255), width=6)
# handle
d.line([(34,34),(54,54)], fill=(136,136,136,255), width=6)
save('search', img)

# User icon: head + body
img = Image.new('RGBA',(SIZE,SIZE),(255,255,255,0))
d = ImageDraw.Draw(img)
# head
d.ellipse([(18,8),(46,36)], fill=(34,170,25,255))
# body
d.rectangle([(12,34),(52,54)], fill=(34,170,25,255))
save('user', img)

# Also write active variants (green tone)
for name in ICONS:
    base = Image.open(os.path.join(OUT_DIR, f"{name}.png")).convert('RGBA')
    # create active by tinting to green (already green for most; for route/search tint stroke)
    active = Image.new('RGBA', base.size, (0,0,0,0))
    active_draw = ImageDraw.Draw(active)
    # overlay slight green circle for demonstration (no complex recolor here)
    # Instead, for simplicity, re-create icons with green highlight where appropriate

# Recreate active versions with green primary color
# Home active
img = Image.new('RGBA', (SIZE, SIZE), (255,255,255,0))
d = ImageDraw.Draw(img)
d.polygon([(8,28),(32,8),(56,28)], fill=(26,170,25,255))
d.rectangle([(16,28),(48,52)], fill=(26,170,25,255))
d.rectangle([(28,36),(36,52)], fill=(255,255,255,255))
save('home-active', img)
# Route active
img = Image.new('RGBA',(SIZE,SIZE),(255,255,255,0))
d = ImageDraw.Draw(img)
d.line([(10,54),(22,40),(36,32),(54,14)], fill=(26,170,25,255), width=6)
d.ellipse([(6,50),(14,58)], fill=(26,170,25,255))
d.ellipse([(50,10),(58,18)], fill=(26,170,25,255))
save('route-active', img)
# Activities active
img = Image.new('RGBA',(SIZE,SIZE),(255,255,255,0))
d = ImageDraw.Draw(img)
d.ellipse([(20,8),(44,32)], fill=(26,170,25,255))
d.rectangle([(12,36),(52,50)], fill=(26,170,25,255))
save('activities-active', img)
# Search active
img = Image.new('RGBA',(SIZE,SIZE),(255,255,255,0))
d = ImageDraw.Draw(img)
d.ellipse([(10,10),(36,36)], outline=(26,170,25,255), width=6)
d.line([(34,34),(54,54)], fill=(26,170,25,255), width=6)
save('search-active', img)
# User active
img = Image.new('RGBA',(SIZE,SIZE),(255,255,255,0))
d = ImageDraw.Draw(img)
d.ellipse([(18,8),(46,36)], fill=(26,170,25,255))
d.rectangle([(12,34),(52,54)], fill=(26,170,25,255))
save('user-active', img)

print('All icons generated.')
