from PIL import Image
from pathlib import Path

root = Path(__file__).resolve().parents[1]
png = root / 'high-resolution-color-logo.png'
ico = root / 'logo.ico'

if not png.exists():
    print('PNG not found:', png)
    raise SystemExit(1)

sizes = [256, 128, 64, 48, 32, 16]
img = Image.open(png).convert('RGBA')
# Ensure square by padding
max_side = max(img.size)
if img.size[0] != img.size[1]:
    new = Image.new('RGBA', (max_side, max_side), (0,0,0,0))
    new.paste(img, ((max_side - img.size[0]) // 2, (max_side - img.size[1]) // 2))
    img = new

# Save as multi-size ICO
img.save(ico, sizes=[(s, s) for s in sizes])
print('Created ICO:', ico)
