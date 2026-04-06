from PIL import Image, ImageDraw, ImageFont
import math

# ── Canvas ──────────────────────────────────────────────────────────────────
W, H = 1080, 1920
img = Image.new("RGB", (W, H), (15, 30, 53))
draw = ImageDraw.Draw(img)

# ── Colors ───────────────────────────────────────────────────────────────────
NAVY_TOP    = (15,  30,  53)   # #0F1E35
NAVY_BOT    = (28,  48,  84)   # #1C3054
GOLD        = (201, 162,  85)  # #C9A255
WHITE       = (255, 255, 255)
WHITE_MUTED = (217, 224, 235)  # #D9E0EB  85% white

# ── Gradient background (horizontal bands) ───────────────────────────────────
steps = 200
for i in range(steps):
    t  = i / (steps - 1)
    r  = int(NAVY_TOP[0] + (NAVY_BOT[0] - NAVY_TOP[0]) * t)
    g  = int(NAVY_TOP[1] + (NAVY_BOT[1] - NAVY_TOP[1]) * t)
    b  = int(NAVY_TOP[2] + (NAVY_BOT[2] - NAVY_TOP[2]) * t)
    y0 = int(i * H / steps)
    y1 = int((i + 1) * H / steps)
    draw.rectangle([0, y0, W, y1], fill=(r, g, b))

# ── Subtle center overlay (adds depth) ───────────────────────────────────────
overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
od = ImageDraw.Draw(overlay)
cx, cy = W // 2, H // 2
for radius in range(500, 0, -10):
    alpha = int(18 * (1 - radius / 500))
    od.ellipse([cx - radius, cy - radius, cx + radius, cy + radius],
               fill=(40, 70, 120, alpha))
img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
draw = ImageDraw.Draw(img)

# ── Fonts ────────────────────────────────────────────────────────────────────
FONTS = "C:/Windows/Fonts/"
def load(path, size):
    try:
        return ImageFont.truetype(FONTS + path, size)
    except Exception:
        return ImageFont.load_default()

f_label   = load("arialbd.ttf",  28)
f_headline= load("arialbd.ttf",  95)
f_hero    = load("arialbi.ttf", 100)
f_body    = load("ariali.ttf",   34)
f_tagline = load("arialbi.ttf",  36)
f_logo_r  = load("arialbd.ttf",  42)
f_logo_nm = load("arialbd.ttf",  52)
f_logo_sub= load("arialbd.ttf",  22)

# ── Helper: centered text ─────────────────────────────────────────────────────
def cx_text(text, y, font, color, draw=draw):
    bbox = draw.textbbox((0, 0), text, font=font)
    tw   = bbox[2] - bbox[0]
    draw.text(((W - tw) // 2, y), text, font=font, fill=color)

# ── Helper: letter-spaced text (simulate tracking) ────────────────────────────
def cx_tracked(text, y, font, color, spacing=5):
    chars  = list(text)
    widths = []
    for c in chars:
        bb = draw.textbbox((0, 0), c, font=font)
        widths.append(bb[2] - bb[0])
    total = sum(widths) + spacing * (len(chars) - 1)
    x = (W - total) // 2
    for c, w in zip(chars, widths):
        draw.text((x, y), c, font=font, fill=color)
        x += w + spacing

# ── 1. Decorative top-left square with chevron ───────────────────────────────
sq_x, sq_y, sq_s = 40, 40, 130
bw = 2  # border width

# Outer border square (gold outline)
for t in range(bw):
    draw.rectangle([sq_x + t, sq_y + t, sq_x + sq_s - t, sq_y + sq_s - t],
                   outline=GOLD)

# Chevron "‹" pointing upper-left (two lines forming a V rotated)
cx_ch = sq_x + sq_s // 2
cy_ch = sq_y + sq_s // 2
size  = 28
lw    = 3
# Upper-left chevron: two lines meeting at a point
pts_outer = [(cx_ch + size, cy_ch - size),
             (cx_ch - size, cy_ch),
             (cx_ch + size, cy_ch + size)]
draw.line(pts_outer, fill=GOLD, width=lw)
pts_inner = [(cx_ch + size - 14, cy_ch - size + 8),
             (cx_ch - size + 10, cy_ch),
             (cx_ch + size - 14, cy_ch + size - 8)]
draw.line(pts_inner, fill=GOLD, width=lw)

# ── 2. Gold thin accent line (top, near square) ──────────────────────────────
draw.rectangle([40, sq_y + sq_s + 16, 220, sq_y + sq_s + 18], fill=GOLD)

# ── 3. ICP Label ─────────────────────────────────────────────────────────────
cx_tracked("PARA CONTADORES E CONSULTORES", 280, f_label, GOLD, spacing=4)

# ── 4. Headline ──────────────────────────────────────────────────────────────
cx_text("Seja",    340, f_headline, WHITE)
cx_text("nosso",   445, f_headline, WHITE)
cx_text("Parceiro",550, f_hero,     GOLD)

# ── 5. Horizontal gold separator ─────────────────────────────────────────────
sep_y = 678
sep_w = 200
draw.rectangle([(W - sep_w) // 2, sep_y, (W + sep_w) // 2, sep_y + 2], fill=GOLD)

# ── 6. Body text ─────────────────────────────────────────────────────────────
body_x = (W - 860) // 2  # left-align block centered on canvas

def left_block(text, y):
    bbox = draw.textbbox((0, 0), text, font=f_body)
    tw   = bbox[2] - bbox[0]
    draw.text(((W - tw) // 2, y), text, font=f_body, fill=WHITE_MUTED)

left_block("Aumente o faturamento da sua carteira",     708)
left_block("com soluções tributárias especializadas.",  750)

left_block("Você indica; nós assumimos todo o técnico", 814)
left_block("e operacional — do diagnóstico à entrega.", 856)

# ── 7. Tagline ────────────────────────────────────────────────────────────────
cx_text("Você indica. Nós entregamos.", 932, f_tagline, GOLD)
cx_text("Os dois ganham.",              978, f_tagline, GOLD)

# ── 8. Thin decorative rule before logo ──────────────────────────────────────
rule_y = 1600
draw.rectangle([(W - 300) // 2, rule_y, (W + 300) // 2, rule_y + 1],
               fill=(*GOLD, 180))

# ── 9. Logo R-TORN ────────────────────────────────────────────────────────────
logo_y   = 1630
icon_s   = 70
icon_x   = (W - icon_s) // 2 - 160
icon_y   = logo_y

# Gold square icon
for t in range(3):
    draw.rectangle([icon_x + t, icon_y + t,
                    icon_x + icon_s - t, icon_y + icon_s - t],
                   outline=GOLD)
draw.rectangle([icon_x + 3, icon_y + 3, icon_x + icon_s - 3, icon_y + icon_s - 3],
               fill=GOLD)

# "R" letter centered inside icon
f_r_icon = load("arialbd.ttf", 44)
r_bbox   = draw.textbbox((0, 0), "R", font=f_r_icon)
r_w      = r_bbox[2] - r_bbox[0]
r_h      = r_bbox[3] - r_bbox[1]
draw.text((icon_x + (icon_s - r_w) // 2,
           icon_y + (icon_s - r_h) // 2 - 2),
          "R", font=f_r_icon, fill=WHITE)

# "R-TORN" text next to icon
name_x = icon_x + icon_s + 18
name_bbox = draw.textbbox((0, 0), "R-TORN", font=f_logo_nm)
name_h    = name_bbox[3] - name_bbox[1]
name_y    = icon_y + (icon_s - name_h) // 2 - 2
draw.text((name_x, name_y), "R-TORN", font=f_logo_nm, fill=WHITE)

# Subtexto "INTELIGÊNCIA TRIBUTÁRIA"
sub_y = icon_y + icon_s + 14
cx_tracked("INTELIGÊNCIA TRIBUTÁRIA", sub_y, f_logo_sub, GOLD, spacing=6)

# ── Save ──────────────────────────────────────────────────────────────────────
out = "C:/Users/admin/Desktop/rtorn_parceiro.png"
img.save(out, "PNG")
print(f"Saved: {out}  ({W}x{H}px)")
