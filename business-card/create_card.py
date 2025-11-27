#!/usr/bin/env python3
"""
Shadow Protocol Business Card Generator
Creates a meticulously crafted business card for The Shinobi Project
Matches the website's sharp, minimal aesthetic
"""

from PIL import Image, ImageDraw, ImageFont
import os
import numpy as np

# === CONFIGURATION ===
# Standard business card: 3.5" x 2" at 300 DPI
CARD_WIDTH = 1050  # 3.5 inches * 300 DPI
CARD_HEIGHT = 600  # 2 inches * 300 DPI

# Color palette - matches website exactly
BLACK = (0, 0, 0)              # Pure black (bg-black)
ZINC_950 = (9, 9, 11)          # Near-black (bg-zinc-950)
ZINC_900 = (24, 24, 27)        # Card backgrounds
ZINC_800 = (39, 39, 42)        # Borders
ZINC_500 = (113, 113, 122)     # Secondary text
ZINC_400 = (161, 161, 170)     # Body text
WHITE = (255, 255, 255)        # Primary text
RED_700 = (185, 28, 28)        # Accent

FONTS_DIR = "/Users/aarondudfield/.claude/skills/canvas-design/canvas-fonts"
LOGO_PATH = "/Users/aarondudfield/the-shinobi-project/frontend/public/logos/Shinobi.png"
OUTPUT_DIR = "/Users/aarondudfield/the-shinobi-project/business-card"


def invert_logo_for_dark_bg(logo):
    """Convert dark logo to light while preserving red accent."""
    if logo.mode != 'RGBA':
        logo = logo.convert('RGBA')

    r, g, b, a = logo.split()
    r_arr = np.array(r)
    g_arr = np.array(g)
    b_arr = np.array(b)

    # Dark pixels (black text) -> white
    is_dark = (r_arr < 80) & (g_arr < 80) & (b_arr < 80)
    r_arr[is_dark] = 255
    g_arr[is_dark] = 255
    b_arr[is_dark] = 255

    return Image.merge('RGBA', (
        Image.fromarray(r_arr),
        Image.fromarray(g_arr),
        Image.fromarray(b_arr),
        a
    ))


def create_front_card():
    """Front: Name card - bold, minimal, sharp."""
    img = Image.new('RGB', (CARD_WIDTH, CARD_HEIGHT), ZINC_950)
    draw = ImageDraw.Draw(img)

    # Load fonts
    font_name = ImageFont.truetype(f"{FONTS_DIR}/Outfit-Bold.ttf", 54)
    font_role = ImageFont.truetype(f"{FONTS_DIR}/GeistMono-Regular.ttf", 14)
    font_tagline = ImageFont.truetype(f"{FONTS_DIR}/GeistMono-Regular.ttf", 11)

    # Left accent bar - the signature element (like website's border-l-2 border-red-700)
    bar_width = 4
    draw.rectangle([(0, 0), (bar_width, CARD_HEIGHT)], fill=RED_700)

    # Name - bold, white, dominant
    name_x = 60
    name_y = CARD_HEIGHT // 2 - 30
    draw.text((name_x, name_y), "JONIN", font=font_name, fill=WHITE)

    # Role - uppercase, tracked, muted
    role_y = name_y + 70
    draw.text((name_x, role_y), "FOUNDER  /  PRINCIPAL", font=font_role, fill=ZINC_500)

    # Horizontal accent under role
    line_y = role_y + 30
    draw.line([(name_x, line_y), (name_x + 80, line_y)], fill=RED_700, width=2)

    # Tagline bottom - whispered
    tagline_y = CARD_HEIGHT - 55
    draw.text((name_x, tagline_y), "SILENT PARTNERS FOR LOCAL GROWTH", font=font_tagline, fill=ZINC_800)

    return img


def create_back_card():
    """Back: Contact card - clean, hierarchical, precise."""
    img = Image.new('RGB', (CARD_WIDTH, CARD_HEIGHT), ZINC_950)
    draw = ImageDraw.Draw(img)

    # Load fonts
    font_label = ImageFont.truetype(f"{FONTS_DIR}/GeistMono-Regular.ttf", 10)
    font_value = ImageFont.truetype(f"{FONTS_DIR}/GeistMono-Regular.ttf", 14)
    font_url = ImageFont.truetype(f"{FONTS_DIR}/Outfit-Bold.ttf", 16)

    # Load and process logo
    try:
        logo = Image.open(LOGO_PATH)
        logo = invert_logo_for_dark_bg(logo)

        # Scale logo
        logo_height = 65
        aspect = logo.width / logo.height
        logo_width = int(logo_height * aspect)
        logo = logo.resize((logo_width, logo_height), Image.Resampling.LANCZOS)

        # Position logo left-aligned with margin
        logo_x = 60
        logo_y = 70
        img.paste(logo, (logo_x, logo_y), logo)
    except Exception as e:
        print(f"Logo error: {e}")

    # Red accent line below logo
    line_y = 160
    draw.line([(60, line_y), (140, line_y)], fill=RED_700, width=2)

    # Contact info - left aligned, clean hierarchy
    left_margin = 60

    # Email block
    email_label_y = 195
    draw.text((left_margin, email_label_y), "EMAIL", font=font_label, fill=ZINC_500)
    draw.text((left_margin, email_label_y + 18), "ops@theshinobiproject.com", font=font_value, fill=ZINC_400)

    # Divider
    div_y = email_label_y + 55
    draw.line([(left_margin, div_y), (left_margin + 30, div_y)], fill=ZINC_800, width=1)

    # Phone block
    phone_label_y = div_y + 20
    draw.text((left_margin, phone_label_y), "DIRECT", font=font_label, fill=ZINC_500)
    draw.text((left_margin, phone_label_y + 18), "+1 (555) 000-0000", font=font_value, fill=ZINC_400)

    # Website - bottom right, prominent
    url_text = "THESHINOBIPROJECT.COM"
    bbox = draw.textbbox((0, 0), url_text, font=font_url)
    url_width = bbox[2] - bbox[0]
    url_x = CARD_WIDTH - 60 - url_width
    url_y = CARD_HEIGHT - 60
    draw.text((url_x, url_y), url_text, font=font_url, fill=WHITE)

    # Subtle border line at top (like website's border-t border-zinc-900)
    draw.line([(0, 0), (CARD_WIDTH, 0)], fill=ZINC_800, width=1)

    return img


def create_combined_card():
    """Combined preview of both sides."""
    front = create_front_card()
    back = create_back_card()

    if front is None or back is None:
        return None

    gap = 40
    combined_width = CARD_WIDTH * 2 + gap * 3
    combined_height = CARD_HEIGHT + gap * 2

    combined = Image.new('RGB', (combined_width, combined_height), (24, 24, 27))
    combined.paste(front, (gap, gap))
    combined.paste(back, (CARD_WIDTH + gap * 2, gap))

    return combined


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    front = create_front_card()
    back = create_back_card()
    combined = create_combined_card()

    if front:
        front.save(f"{OUTPUT_DIR}/business-card-front.png", "PNG", dpi=(300, 300))
        print("Created: business-card-front.png")

    if back:
        back.save(f"{OUTPUT_DIR}/business-card-back.png", "PNG", dpi=(300, 300))
        print("Created: business-card-back.png")

    if combined:
        combined.save(f"{OUTPUT_DIR}/business-card-combined.png", "PNG", dpi=(300, 300))
        print("Created: business-card-combined.png")

    print("\nBusiness cards generated.")


if __name__ == "__main__":
    main()
