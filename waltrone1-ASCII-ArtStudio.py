import base64
import colorsys
import html
import json
import os
import random
import re
import socket
import tempfile
import threading
import time
import webbrowser
from dataclasses import dataclass, asdict
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from PIL import Image, ImageEnhance, ImageOps, ImageTk, ImageDraw, ImageFont
import tkinter as tk
from tkinter import filedialog, messagebox, colorchooser
from tkinter import ttk

SOFTWARE_NAME = "waltrone1-ASCII-ArtStudio Retro HTML Pro Arcade"
SOFTWARE_VERSION = "1.0.0"
CHAR_ASPECT_CORRECTION = 0.56

ASCII_CHARSETS = {
    "Standard fein": "@%#*+=-:. ",
    "Blockig": "█▓▒░. ",
    "Retro Dense": "$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\\|()1{}[]?-_+~<>i!lI;:,\"^`'. ",
    "Minimal": "@#*:. ",
    "Matrix": "01|/\\[]{}<>*+=-:. ",
    "Punkte": "●◉◎○◌· ",
    "Quadrate": "■▣▦▤▪▫. ",
}

PALETTES = {
    "Originalfarben": [],
    "Matrix Grün": ["#001600", "#003300", "#007700", "#00BB00", "#00FF66", "#B8FFCC"],
    "Amber Monitor": ["#160B00", "#402000", "#804000", "#D98C00", "#FFB000", "#FFE0A0"],
    "Ice Terminal": ["#001018", "#00364D", "#006C8A", "#00B7D9", "#7FEFFF", "#E8FDFF"],
    "Neon Cyber": ["#090A1A", "#36185A", "#7B2CBF", "#FF2CDF", "#00D9FF", "#FFFFFF"],
    "Fire CRT": ["#190000", "#4D0000", "#A51600", "#FF4400", "#FFAA00", "#FFF1B8"],
    "Blue DOS": ["#000018", "#001A55", "#003BA0", "#007ACC", "#69D2FF", "#F1FCFF"],
    "Metal Chrome": ["#070707", "#2A2A2A", "#6B7280", "#CBD5E1", "#FFFFFF", "#8FA3B8"],
    "Mario Retro": ["#5C0000", "#D00000", "#FFCC00", "#2FAE2F", "#2D6CDF", "#FFFFFF"],
    "Arcade 80s": ["#12002B", "#3A0CA3", "#7209B7", "#F72585", "#4CC9F0", "#FFFFFF"],
    "Neon Miami": ["#080014", "#240046", "#7B2CBF", "#FF4DDB", "#00F5D4", "#F8F7FF"],
    "Toxic Lime": ["#061000", "#153800", "#3E8E00", "#8CFF00", "#D8FF5A", "#FFFFFF"],
}

TERMINAL_FONTS = [
    "Consolas",
    "Lucida Console",
    "Cascadia Mono",
    "Courier New",
    "DejaVu Sans Mono",
    "monospace",
]

EFFECTS = [
    "CMD Classic",
    "CRT",
    "Retro",
    "Glow Soft",
    "Glow Strong",
    "Neon Terminal",
    "Neon Pink",
    "Neon Cyan",
    "Neon Lime",
    "Matrix Background",
    "Glitch",
    "Amber Monitor",
    "Metal Chrome",
    "Arcade 80s",
    "Mario Retro",
    "Pixel Candy",
    "Blue Electric",
    "Laser Red",
    "Gold Shine",
    "Copper Glow",
]

MENU_STYLE_PRESETS = ["CMD Classic", "CRT", "Retro"]
MENU_STYLE_EFFECT_MAP = {
    "CMD Classic": "CMD Classic",
    "CRT": "CRT",
    "Retro": "Retro",
}

BG_PRESETS = ["#000000", "#020617", "#06130B", "#0B1020", "#111111", "#111827", "#1F1300", "#001018", "#240046", "#330000", "#002B36", "#1A1200"]

EXPORT_MODES = ["Nur ASCII-Bild", "Bild + Programmname", "Terminal-Frame", "Embed"]
EXPORT_SCALES = ["1x", "2x", "4x", "Druckqualität"]

RETRO_MOTIFS = [
    "Atari 2600", "Atari 7800", "Arcade Cabinet", "Space Invaders", "Pac Maze",
    "Tetris Blocks", "CRT Terminal", "VHS Night", "Walkman", "Floppy Disk",
    "Game Handheld", "Cassette Tape", "Boombox", "Synthwave Palm", "Vector Grid",
    "Glitch Signal", "Modem Dialup", "Pixel Racer", "Laser Tunnel", "Demo Scene"
]

RETRO_MOTIF_ITEMS = {
    "Atari 2600": [("atari2600", "Atari 2600"), ("joystick", "CX40 Stick"), ("cartridge", "Cartridge"), ("pixelship", "Pixel Ship")],
    "Atari 7800": [("atari7800", "Atari 7800"), ("gamepad", "Gamepad"), ("cartridge", "Cartridge"), ("spark", "7800")],
    "Arcade Cabinet": [("cabinet", "Cabinet"), ("joystick", "Joystick"), ("coin", "Insert Coin"), ("score", "HI-SCORE")],
    "Space Invaders": [("invader", "Invader"), ("ufo", "UFO"), ("pixelship", "Laser Base"), ("star", "Starfield")],
    "Pac Maze": [("pac", "Maze"), ("ghost", "Ghost"), ("coin", "Dots"), ("heart", "Extra Life")],
    "Tetris Blocks": [("blocks", "Blocks"), ("grid", "Grid"), ("spark", "Line Clear"), ("gamepad", "Control")],
    "CRT Terminal": [("monitor", "CRT"), ("scanline", "Scanlines"), ("terminal", "C:\\>"), ("glitchbox", "Phosphor")],
    "VHS Night": [("vhs", "VHS"), ("tracking", "Tracking"), ("tape", "Tape"), ("glitchbox", "Noise")],
    "Walkman": [("walkman", "Walkman"), ("headphones", "Phones"), ("cassette", "Mixtape"), ("bolt", "Bass")],
    "Floppy Disk": [("floppy", "Floppy"), ("disk", "Disk"), ("monitor", "PC"), ("terminal", "Boot")],
    "Game Handheld": [("handheld", "Handheld"), ("blocks", "Blocks"), ("heart", "1UP"), ("gamepad", "Pad")],
    "Cassette Tape": [("cassette", "Cassette"), ("tape", "Tape Reel"), ("boombox", "Player"), ("bolt", "Rewind")],
    "Boombox": [("boombox", "Boombox"), ("equalizer", "EQ"), ("cassette", "Tape"), ("bolt", "Beat")],
    "Synthwave Palm": [("palm", "Palm"), ("sunset", "Sunset"), ("grid", "Grid"), ("glasses", "Shades")],
    "Vector Grid": [("grid", "Vector"), ("wirecube", "Wire Cube"), ("ufo", "UFO"), ("star", "Stars")],
    "Glitch Signal": [("glitchbox", "Glitch"), ("scanline", "Signal"), ("bolt", "Noise"), ("terminal", "ERR")],
    "Modem Dialup": [("modem", "Modem"), ("phone", "Dial"), ("terminal", "CONNECT"), ("spark", "56K")],
    "Pixel Racer": [("car", "Racer"), ("road", "Road"), ("flag", "Finish"), ("bolt", "Turbo")],
    "Laser Tunnel": [("tunnel", "Tunnel"), ("laser", "Laser"), ("grid", "Grid"), ("spark", "Warp")],
    "Demo Scene": [("wirecube", "Cube"), ("equalizer", "Bars"), ("star", "Stars"), ("terminal", "Demo")]
}

DEFAULT_SETTINGS = {
    "width_chars": 140,
    "charset_name": "Standard fein",
    "custom_charset": "w@ltrone1",
    "use_custom_charset": True,
    "menu_style": "CRT",
    "palette_name": "Originalfarben",
    "use_gradient": True,
    "bg_color": "#000000",
    "transparent_black": True,
    "black_threshold": 18,
    "invert_luminance": False,
    "terminal_font": "Consolas",
    "html_font_size": 8,
    "line_height": 1.0,
    "letter_spacing": 0.0,
    "effect": "CRT",
    "show_titlebar": True,
    "show_toolbar": True,
    "interactive_controls": True,
    "export_embed": False,
    "auto_browser_preview": True,
    "show_retro_toys": True,
    "retro_motif": "Atari 2600",
    "auto_rotate_retro_motifs": True,
    "retro_animation": True,
    "show_export_branding": True,
    "export_mode": "Bild + Programmname",
    "export_scale": "2x",
    "png_transparent": True,
}

try:
    RESAMPLE_LANCZOS = Image.Resampling.LANCZOS
    RESAMPLE_NEAREST = Image.Resampling.NEAREST
except AttributeError:
    RESAMPLE_LANCZOS = Image.LANCZOS
    RESAMPLE_NEAREST = Image.NEAREST


def clamp(value, minimum, maximum):
    return max(minimum, min(maximum, value))


def hex_to_rgb(value):
    value = (value or "#000000").strip().lstrip("#")
    if len(value) != 6:
        return (0, 0, 0)
    try:
        return tuple(int(value[i:i+2], 16) for i in (0, 2, 4))
    except ValueError:
        return (0, 0, 0)


def rgb_to_hex(rgb):
    r, g, b = rgb[:3]
    return f"#{r:02X}{g:02X}{b:02X}"


def brightness(rgb):
    r, g, b = rgb[:3]
    return int(0.299 * r + 0.587 * g + 0.114 * b)


def safe_suffix(text):
    text = (text or "ascii").lower()
    repl = {"ä": "ae", "ö": "oe", "ü": "ue", "ß": "ss"}
    for k, v in repl.items():
        text = text.replace(k, v)
    text = re.sub(r"[^a-z0-9_-]+", "_", text).strip("_")
    return text or "ascii"


def parse_custom_charset(raw_text):
    raw_text = (raw_text or "").strip()
    if not raw_text:
        return ""
    has_sep = any(sep in raw_text for sep in [",", " ", "\n", "\t"])
    parts = re.split(r"[\s,]+", raw_text) if has_sep else list(raw_text)
    out = []
    for part in parts:
        token = part.strip()
        if not token:
            continue
        if token.lower() in ("leer", "leerzeichen", "space", "blank"):
            ch = " "
        else:
            ch = token[0]
        if ch not in out:
            out.append(ch)
    return "".join(out)


def build_gradient(colors, steps):
    if not colors:
        return ["#FFFFFF"] * max(1, steps)
    if len(colors) == 1:
        return colors * max(1, steps)
    steps = max(1, steps)
    out = []
    for i in range(steps):
        t = i / max(1, steps - 1)
        pos = t * (len(colors) - 1)
        idx = min(len(colors) - 2, int(pos))
        local = pos - idx
        r1, g1, b1 = hex_to_rgb(colors[idx])
        r2, g2, b2 = hex_to_rgb(colors[idx + 1])
        r = int(r1 + (r2 - r1) * local)
        g = int(g1 + (g2 - g1) * local)
        b = int(b1 + (b2 - b1) * local)
        out.append(f"#{r:02X}{g:02X}{b:02X}")
    return out


def random_palette():
    base = random.random()
    colors = []
    for i in range(6):
        h = (base + i * 0.09) % 1.0
        s = 0.65 + (i % 2) * 0.2
        v = 0.22 + i * 0.13
        r, g, b = colorsys.hsv_to_rgb(h, min(s, 1), min(v, 1))
        colors.append(f"#{int(r*255):02X}{int(g*255):02X}{int(b*255):02X}")
    return colors


@dataclass
class RenderOptions:
    image_path: str = ""
    width_chars: int = 140
    charset_name: str = "Standard fein"
    custom_charset: str = ""
    use_custom_charset: bool = False
    palette_name: str = "Originalfarben"
    use_gradient: bool = True
    bg_color: str = "#000000"
    transparent_black: bool = True
    black_threshold: int = 18
    invert_luminance: bool = False
    terminal_font: str = "Consolas"
    html_font_size: int = 8
    line_height: float = 1.0
    letter_spacing: float = 0.0
    effect: str = "CRT"
    show_titlebar: bool = True
    show_toolbar: bool = True
    interactive_controls: bool = True
    export_embed: bool = False
    show_export_branding: bool = True
    export_mode: str = "Bild + Programmname"
    export_scale: str = "1x"
    png_transparent: bool = True
    matrix_code_overlay: bool = False
    matrix_code_strength: int = 18


class AsciiRenderer:
    def __init__(self):
        self._random_palette = random_palette()

    def charset(self, options: RenderOptions):
        # Eigene Zeichen sind jetzt bewusst optional.
        # So kann der User ein eigenes Set im Feld stehen lassen und trotzdem
        # schnell zwischen den normalen ASCII-Presets wechseln.
        if getattr(options, "use_custom_charset", False):
            custom = parse_custom_charset(options.custom_charset)
            if custom:
                return custom
        return ASCII_CHARSETS.get(options.charset_name, ASCII_CHARSETS["Standard fein"])

    def palette(self, options: RenderOptions, steps):
        if options.palette_name == "Random Retro":
            colors = self._random_palette
        else:
            colors = PALETTES.get(options.palette_name, [])
        if options.use_gradient:
            return build_gradient(colors, steps)
        return colors or ["#FFFFFF"]

    def reroll_palette(self):
        self._random_palette = random_palette()

    def rows_from_image(self, options: RenderOptions):
        if not options.image_path or not os.path.exists(options.image_path):
            return []
        chars = self.charset(options)
        if not chars:
            chars = ASCII_CHARSETS["Standard fein"]
        with Image.open(options.image_path) as base:
            img = base.convert("RGB")
            aspect = img.height / max(1, img.width)
            height_chars = max(1, int(options.width_chars * aspect * CHAR_ASPECT_CORRECTION))
            img = img.resize((options.width_chars, height_chars), RESAMPLE_LANCZOS)
            pixels = list(img.getdata())

        pal = self.palette(options, len(chars))
        rows = []
        for y in range(height_chars):
            row = []
            for x in range(options.width_chars):
                rgb = pixels[y * options.width_chars + x]
                lum = brightness(rgb)
                if options.invert_luminance:
                    lum = 255 - lum
                if options.transparent_black and brightness(rgb) <= options.black_threshold:
                    row.append((" ", options.bg_color, rgb))
                    continue
                idx = clamp(lum * len(chars) // 256, 0, len(chars) - 1)
                ch = chars[idx]
                if options.palette_name == "Originalfarben":
                    color = rgb_to_hex(rgb)
                else:
                    color = pal[min(idx, len(pal) - 1)]

                row.append((ch, color, rgb))
            rows.append(row)
        return rows

    def html_spans(self, rows, options=None):
        shape_mode = (
            options is not None
            and getattr(options, "charset_name", "") in ("Punkte", "Quadrate")
            and not getattr(options, "use_custom_charset", False)
        )
        shape_class = ""
        if shape_mode:
            shape_class = "ascii-dot" if getattr(options, "charset_name", "") == "Punkte" else "ascii-square"

        lines = []
        for row in rows:
            parts = []
            for ch, color, _rgb in row:
                if shape_mode:
                    if ch == " ":
                        parts.append('<span class="ascii-cell ascii-empty"></span>')
                    else:
                        parts.append(
                            f'<span class="ascii-cell ascii-shape {shape_class}" '
                            f'style="color:{html.escape(color)}"></span>'
                        )
                else:
                    safe = "&nbsp;" if ch == " " else html.escape(ch)
                    parts.append(f'<span class="ascii-ch" style="color:{html.escape(color)}">{safe}</span>')
            lines.append("".join(parts))
        return "\n".join(lines)

    def plain_text(self, rows):
        return "\n".join("".join(ch for ch, _c, _r in row) for row in rows)


class SvgBuilder:
    def document(self, rows, title, options: RenderOptions):
        scale = {"1x": 1, "2x": 2, "4x": 4, "Druckqualität": 6}.get(getattr(options, "export_scale", "1x"), 1)
        font_size = max(1, int(options.html_font_size) * scale)
        char_w = max(1.0, (int(options.html_font_size) * 0.62 + float(options.letter_spacing)) * scale)
        line_h = max(1.0, int(options.html_font_size) * float(options.line_height) * scale)
        cols = max((len(row) for row in rows), default=0)
        mode = getattr(options, "export_mode", "Bild + Programmname")
        terminal_frame = mode == "Terminal-Frame"
        show_footer = mode == "Bild + Programmname"
        pad = 10 * scale
        frame_pad = 18 * scale if terminal_frame else 0
        titlebar_h = 28 * scale if terminal_frame else 0
        footer_font = max(10 * scale, int(font_size * 0.95))
        footer_box_h = footer_font + 20 * scale
        footer_gap = (footer_box_h + 10 * scale) if show_footer else 0
        width = max(1, int(cols * char_w + pad * 2 + frame_pad * 2))
        height = max(1, int(len(rows) * line_h + pad * 2 + frame_pad * 2 + titlebar_h + footer_gap))
        font_family = html.escape(options.terminal_font, quote=True)
        title_safe = html.escape(title, quote=True)
        parts = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="{title_safe}">',
            f'<title>{title_safe}</title>',
        ]
        if terminal_frame:
            parts.append(f'<rect x="{4*scale}" y="{4*scale}" width="{width-8*scale}" height="{height-8*scale}" fill="#000000" stroke="#777777" stroke-width="{max(1,2*scale)}"/>')
            parts.append(f'<rect x="{4*scale}" y="{4*scale}" width="{width-8*scale}" height="{titlebar_h}" fill="#151515" stroke="#777777" stroke-width="{max(1,scale)}"/>')
            parts.append(f'<text x="{12*scale}" y="{20*scale}" fill="#e5e5e5" font-family="Consolas, Courier New, monospace" font-size="{10*scale}">C:\\ASCII\\EXPORT.EXE - {title_safe}</text>')
        parts.append(f'<g font-family="{font_family}, Consolas, Courier New, monospace" font-size="{font_size}" xml:space="preserve">')
        y = pad + frame_pad + titlebar_h + font_size
        for row in rows:
            x = pad + frame_pad
            for ch, color, _rgb in row:
                if ch != " ":
                    safe_color = html.escape(color, quote=True)
                    if options.charset_name == "Punkte" and not options.use_custom_charset:
                        r = max(0.7, font_size * 0.28)
                        parts.append(f'<circle cx="{x + char_w / 2:.2f}" cy="{y - font_size * 0.35:.2f}" r="{r:.2f}" fill="none" stroke="{safe_color}" stroke-width="{max(0.35, font_size * 0.06):.2f}"/>')
                    elif options.charset_name == "Quadrate" and not options.use_custom_charset:
                        size = max(1.0, font_size * 0.55)
                        parts.append(f'<rect x="{x + (char_w - size) / 2:.2f}" y="{y - font_size * 0.75:.2f}" width="{size:.2f}" height="{size:.2f}" fill="none" stroke="{safe_color}" stroke-width="{max(0.35, font_size * 0.06):.2f}"/>')
                    else:
                        safe_ch = html.escape(ch)
                        parts.append(f'<text x="{x:.2f}" y="{y:.2f}" fill="{safe_color}">{safe_ch}</text>')
                x += char_w
            y += line_h
        parts.append('</g>')
        if show_footer:
            footer_safe = html.escape(SOFTWARE_NAME)
            approx_text_w = len(SOFTWARE_NAME) * footer_font * 0.62
            box_w = approx_text_w + 24 * scale
            box_h = footer_box_h
            box_x = max(pad + frame_pad, width - pad - frame_pad - box_w)
            box_y = max(pad + titlebar_h + frame_pad, height - pad - box_h)
            text_x = width - pad - frame_pad - 12 * scale
            text_y = box_y + box_h / 2 + footer_font * 0.36
            parts.append(f'<rect x="{box_x:.2f}" y="{box_y:.2f}" width="{box_w:.2f}" height="{box_h:.2f}" fill="#050505" stroke="#2c6b3f" stroke-width="{max(1, scale)}"/>')
            parts.append(f'<rect x="{box_x - 2*scale:.2f}" y="{box_y - 2*scale:.2f}" width="{box_w + 4*scale:.2f}" height="{box_h + 4*scale:.2f}" fill="none" stroke="#4d145f" stroke-width="{max(1, scale)}" opacity="0.65"/>')
            parts.append(f'<text x="{text_x:.2f}" y="{text_y:.2f}" fill="#7aa78b" font-family="Consolas, Courier New, monospace" font-size="{footer_font}" text-anchor="end">{footer_safe}</text>')
        parts.append('</svg>')
        return "\n".join(parts)

class HtmlBuilder:
    def css(self, options: RenderOptions, embed=False):
        font_stack = f'"{options.terminal_font}", Consolas, "Lucida Console", "Courier New", monospace'
        bg = html.escape(options.bg_color)
        effect_class = self.effect_class(options.effect)
        scope = ".ascii-terminal-embed" if embed else "body"
        return f"""
:root {{ color-scheme: dark; }}
{scope} {{
    margin: 0;
    background: #000;
    color: #e5e5e5;
    font-family: {font_stack};
}}
.ascii-terminal-embed {{
    --ascii-bg: {bg};
    --ascii-font-size: {int(options.html_font_size)}px;
    --ascii-line-height: {options.line_height};
    --ascii-letter-spacing: {options.letter_spacing}px;
    background: #000;
    color: #e5e5e5;
    font-family: {font_stack};
    max-width: 100%;
}}
.ascii-art-only {{
    display: inline-flex;
    flex-direction: column;
    align-items: flex-start;
    background: transparent;
}}
.ascii-art-only .ascii-art {{
    align-self: flex-start;
}}
.ascii-terminal-window {{
    position: relative;
    min-height: {"100vh" if not embed else "auto"};
    background: var(--ascii-bg);
    overflow: auto;
    box-shadow: inset 0 0 48px rgba(0,0,0,.85), 0 0 18px rgba(0,255,100,.10);
}}
.ascii-titlebar {{
    height: 30px;
    display: flex;
    align-items: center;
    padding: 0 10px;
    box-sizing: border-box;
    background: linear-gradient(#171717,#0b0b0b);
    color: #f2f2f2;
    border-bottom: 1px solid #2d2d2d;
    font-family: "Segoe UI", Arial, sans-serif;
    font-size: 12px;
    user-select: none;
}}
.ascii-titlebar .title {{ flex: 1; overflow: hidden; white-space: nowrap; text-overflow: ellipsis; }}
.ascii-titlebar .controls {{ display: flex; gap: 12px; color: #d0d0d0; }}
.ascii-toolbar {{
    padding: 8px 10px;
    background: #000;
    border-bottom: 1px solid #202020;
    color: #c0c0c0;
    font-size: 13px;
    line-height: 1.25;
}}
.ascii-toolbar code {{ color: #00ff66; }}
.ascii-actions {{ margin-top: 8px; display: flex; flex-wrap: wrap; gap: 8px; align-items: center; }}
.ascii-btn, .ascii-select, .ascii-range {{
    background: #050505;
    color: #d0d0d0;
    border: 1px solid #777;
    font-family: inherit;
    font-size: 12px;
}}
.ascii-btn {{ padding: 4px 8px; cursor: pointer; }}
.ascii-btn:hover {{ background: #1a1a1a; color: #fff; }}
.ascii-stage {{ position: relative; overflow: auto; background: var(--ascii-bg); }}
.ascii-art {{
    position: relative;
    z-index: 2;
    margin: 0;
    padding: 10px;
    background: transparent;
    color: #f2f2f2;
    font-family: {font_stack};
    font-size: var(--ascii-font-size);
    line-height: var(--ascii-line-height);
    letter-spacing: var(--ascii-letter-spacing);
    white-space: pre;
    tab-size: 4;
    font-variant-ligatures: none;
    -webkit-font-smoothing: none;
    text-rendering: geometricPrecision;
}}
.ascii-hidden {{ display: none; }}
.ascii-export-footer {{
    display: table;
    align-self: flex-end;
    margin: 8px 0 0 0;
    padding: 10px 12px;
    color: #7aa78b;
    background: #050505;
    border: 1px solid #2c6b3f;
    box-shadow: 0 0 10px rgba(255, 0, 255, .35), inset 0 0 10px rgba(0, 255, 100, .08);
    font-family: Consolas, "Courier New", monospace;
    font-size: 12px;
    line-height: 1.25;
    text-align: right;
    box-sizing: border-box;
}}
.ascii-cell {{
    display: inline-block;
    width: calc(var(--ascii-font-size) * 0.72);
    height: calc(var(--ascii-font-size) * var(--ascii-line-height));
    position: relative;
    vertical-align: top;
}}
.ascii-shape::before {{
    content: "";
    position: absolute;
    left: 50%;
    top: 50%;
    transform: translate(-50%, -50%);
    box-sizing: border-box;
}}
.ascii-dot::before {{
    width: calc(var(--ascii-font-size) * 0.56);
    height: calc(var(--ascii-font-size) * 0.56);
    border: max(1px, calc(var(--ascii-font-size) * 0.075)) solid currentColor;
    border-radius: 50%;
}}
.ascii-square::before {{
    width: calc(var(--ascii-font-size) * 0.58);
    height: calc(var(--ascii-font-size) * 0.58);
    border: max(1px, calc(var(--ascii-font-size) * 0.075)) solid currentColor;
}}
.ascii-empty::before {{ content: ""; }}
.effect-crt-scanlines .ascii-stage::after,
.effect-retro-crt-glow .ascii-stage::after,
.effect-amber-monitor .ascii-stage::after {{
    content: "";
    pointer-events: none;
    position: absolute;
    inset: 0;
    z-index: 3;
    background: repeating-linear-gradient(to bottom, rgba(255,255,255,.035) 0, rgba(255,255,255,.035) 1px, rgba(0,0,0,.22) 2px, rgba(0,0,0,.22) 4px);
    mix-blend-mode: overlay;
}}
.effect-retro-crt-glow .ascii-art {{ text-shadow: 0 0 5px rgba(0,255,90,.45), 0 0 14px rgba(0,255,90,.22); }}
.effect-neon-terminal .ascii-art {{ text-shadow: 0 0 5px currentColor, 0 0 12px rgba(0,255,170,.45); }}
.effect-amber-monitor .ascii-art {{ filter: sepia(.45) saturate(1.35); text-shadow: 0 0 6px rgba(255,176,0,.55); }}
.effect-matrix-background .ascii-stage::before {{
    content: "01001011 10100101 0110 1101 0011 0101";
    position: absolute;
    inset: 0;
    z-index: 1;
    color: rgba(0,255,70,.08);
    font-size: 18px;
    line-height: 1.8;
    word-break: break-all;
    overflow: hidden;
    animation: matrixDrift 8s linear infinite;
}}
.effect-glitch .ascii-art {{ animation: glitchShift 1.8s infinite steps(2,end); text-shadow: 1px 0 rgba(255,0,80,.65), -1px 0 rgba(0,220,255,.65); }}

.effect-glow-soft .ascii-art {{ text-shadow: 0 0 4px rgba(255,255,255,.30), 0 0 10px rgba(0,255,150,.22); }}
.effect-glow-strong .ascii-art {{ text-shadow: 0 0 4px currentColor, 0 0 10px currentColor, 0 0 22px rgba(0,255,180,.50); }}
.effect-neon-pink .ascii-art {{ color: #fff; text-shadow: 0 0 4px #fff, 0 0 10px #ff4ddb, 0 0 22px #ff4ddb; filter: saturate(1.35); }}
.effect-neon-cyan .ascii-art {{ color: #effcff; text-shadow: 0 0 4px #fff, 0 0 10px #00e5ff, 0 0 22px #00e5ff; filter: saturate(1.35); }}
.effect-neon-lime .ascii-art {{ color: #f6fff0; text-shadow: 0 0 4px #fff, 0 0 10px #8cff00, 0 0 24px #8cff00; filter: saturate(1.45); }}
.effect-metal-chrome .ascii-art {{ filter: grayscale(.25) contrast(1.35) brightness(1.08); text-shadow: 1px 1px 0 rgba(0,0,0,.85), -1px -1px 0 rgba(255,255,255,.18), 0 0 12px rgba(210,230,255,.25); }}
.effect-arcade-80s .ascii-stage {{ background: radial-gradient(circle at 50% 120%, rgba(255,45,219,.22), transparent 45%), linear-gradient(180deg, var(--ascii-bg), #090018); }}
.effect-arcade-80s .ascii-art {{ text-shadow: 2px 0 rgba(0,217,255,.65), -2px 0 rgba(255,77,219,.55), 0 0 12px rgba(255,77,219,.35); }}
.effect-mario-retro .ascii-stage {{ background: linear-gradient(180deg, #5c94fc 0%, #5c94fc 52%, #5abf45 52%, #2f8f2f 100%); }}
.effect-mario-retro .ascii-art {{ text-shadow: 1px 1px 0 rgba(0,0,0,.8), 2px 2px 0 rgba(0,0,0,.35); filter: saturate(1.4) contrast(1.1); }}
.effect-pixel-candy .ascii-art {{ text-shadow: 1px 1px 0 rgba(255,255,255,.22), 0 0 9px rgba(255,112,166,.42), 0 0 16px rgba(125,211,252,.28); filter: saturate(1.55); }}
.effect-blue-electric .ascii-art {{ text-shadow: 0 0 5px #69d2ff, 0 0 13px #007acc, 0 0 26px rgba(0,122,204,.65); filter: saturate(1.3); }}
.effect-laser-red .ascii-art {{ text-shadow: 0 0 4px #fff, 0 0 12px #ff3030, 0 0 24px #ff0000; filter: contrast(1.18) saturate(1.4); }}
.effect-gold-shine .ascii-art {{ filter: sepia(.35) saturate(1.4) brightness(1.08); text-shadow: 0 0 5px rgba(255,210,90,.65), 0 0 16px rgba(255,170,0,.35); }}
.effect-copper-glow .ascii-art {{ filter: sepia(.55) saturate(1.25); text-shadow: 0 0 5px rgba(210,120,55,.65), 0 0 15px rgba(160,70,30,.35); }}
@keyframes matrixDrift {{ from {{ transform: translateY(-20%); }} to {{ transform: translateY(20%); }} }}
@keyframes glitchShift {{ 0%, 100% {{ transform: translate(0,0); }} 20% {{ transform: translate(1px,0); }} 40% {{ transform: translate(-1px,1px); }} 60% {{ transform: translate(0,-1px); }} }}
"""

    def effect_class(self, effect):
        return {
            "CMD Classic": "effect-cmd-classic",
            "CRT": "effect-crt-scanlines",
            "Retro": "effect-retro-crt-glow",
            "CRT Scanlines": "effect-crt-scanlines",
            "Retro CRT Glow": "effect-retro-crt-glow",
            "Glow Soft": "effect-glow-soft",
            "Glow Strong": "effect-glow-strong",
            "Neon Terminal": "effect-neon-terminal",
            "Neon Pink": "effect-neon-pink",
            "Neon Cyan": "effect-neon-cyan",
            "Neon Lime": "effect-neon-lime",
            "Matrix Background": "effect-matrix-background",
            "Glitch": "effect-glitch",
            "Amber Monitor": "effect-amber-monitor",
            "Metal Chrome": "effect-metal-chrome",
            "Arcade 80s": "effect-arcade-80s",
            "Mario Retro": "effect-mario-retro",
            "Pixel Candy": "effect-pixel-candy",
            "Blue Electric": "effect-blue-electric",
            "Laser Red": "effect-laser-red",
            "Gold Shine": "effect-gold-shine",
            "Copper Glow": "effect-copper-glow",
        }.get(effect, "effect-cmd-classic")

    def effect_options_html(self, current_class):
        parts = []
        for effect_name in EFFECTS:
            cls = self.effect_class(effect_name)
            selected = " selected" if cls == current_class else ""
            parts.append(f'<option value="{html.escape(cls)}"{selected}>{html.escape(effect_name)}</option>')
        return "\n".join(parts)

    def controls_js(self):
        return """
<script>
function asciiCopyRaw(rootId){
  const root = document.getElementById(rootId);
  const raw = root.querySelector('.ascii-raw').textContent;
  navigator.clipboard.writeText('```\\n' + raw + '\\n```').then(()=>{
    const st = root.querySelector('.ascii-status'); if(st) st.textContent='ASCII-Codeblock kopiert.';
  }).catch(()=>{
    const st = root.querySelector('.ascii-status'); if(st) st.textContent='Kopieren im Browser nicht erlaubt.';
  });
}
function asciiSetFontSize(rootId, value){ document.getElementById(rootId).style.setProperty('--ascii-font-size', value + 'px'); }
function asciiSetLineHeight(rootId, value){ document.getElementById(rootId).style.setProperty('--ascii-line-height', value); }
function asciiSetEffect(rootId, value){
  const root = document.getElementById(rootId);
  root.classList.remove('effect-cmd-classic','effect-crt-scanlines','effect-retro-crt-glow','effect-glow-soft','effect-glow-strong','effect-neon-terminal','effect-neon-pink','effect-neon-cyan','effect-neon-lime','effect-matrix-background','effect-glitch','effect-amber-monitor','effect-metal-chrome','effect-arcade-80s','effect-mario-retro','effect-pixel-candy','effect-blue-electric','effect-laser-red','effect-gold-shine','effect-copper-glow');
  root.classList.add(value);
}
</script>
"""

    def terminal_block(self, ascii_html, raw_ascii, title, options: RenderOptions, root_id="asciiTerminal", embed=False):
        effect_class = self.effect_class(options.effect)
        titlebar = ""
        if options.show_titlebar:
            titlebar = f"""<div class=\"ascii-titlebar\"><div class=\"title\">C:\\Windows\\System32\\cmd.exe - {html.escape(title)}</div><div class=\"controls\"><span>─</span><span>□</span><span>×</span></div></div>"""
        toolbar = ""
        if options.show_toolbar:
            controls = ""
            if options.interactive_controls:
                controls = f"""
                <label>Fontgröße <input class=\"ascii-range\" type=\"range\" min=\"5\" max=\"22\" value=\"{int(options.html_font_size)}\" oninput=\"asciiSetFontSize('{root_id}', this.value)\"></label>
                <label>Zeilenhöhe <input class=\"ascii-range\" type=\"range\" min=\"0.7\" max=\"1.6\" step=\"0.05\" value=\"{options.line_height}\" oninput=\"asciiSetLineHeight('{root_id}', this.value)\"></label>
                <select class=\"ascii-select\" onchange=\"asciiSetEffect('{root_id}', this.value)\">
                    {self.effect_options_html(effect_class)}
                </select>
                """
            toolbar = f"""
            <div class=\"ascii-toolbar\">
                <div>Microsoft Windows [Version Retro.HTML.{SOFTWARE_VERSION}]</div>
                <div>(c) waltrone1 ASCII Terminal Renderer</div>
                <div><code>C:\\ASCII&gt;</code> render \"{html.escape(title)}\" /palette:{html.escape(options.palette_name)}</div>
                <div class=\"ascii-actions\">
                    <button class=\"ascii-btn\" onclick=\"asciiCopyRaw('{root_id}')\">ASCII kopieren</button>
                    {controls}
                </div>
                <div class=\"ascii-status\"></div>
            </div>
            """
        return f"""
<div id=\"{root_id}\" class=\"ascii-terminal-embed {effect_class}\">
  <div class=\"ascii-terminal-window\">
    {titlebar}
    {toolbar}
    <div class=\"ascii-stage\"><pre class=\"ascii-art\">{ascii_html}</pre></div>
    <pre class=\"ascii-hidden ascii-raw\">{html.escape(raw_ascii)}</pre>
  </div>
</div>
"""

    def preview_block(self, ascii_html, raw_ascii, title, options: RenderOptions, root_id="asciiPreview"):
        """HTML block for live preview that mirrors the selected export mode."""
        mode = getattr(options, "export_mode", "Bild + Programmname")
        if mode in ("Terminal-Frame", "Embed"):
            return self.terminal_block(ascii_html, raw_ascii, title, options, root_id=root_id, embed=(mode == "Embed"))

        footer_html = ""
        if mode == "Bild + Programmname":
            footer_html = f'<div class="ascii-export-footer">{html.escape(SOFTWARE_NAME)}</div>'

        return f"""
<div id="{root_id}" class="ascii-terminal-embed {self.effect_class(options.effect)} ascii-art-only">
  <pre class="ascii-art">{ascii_html}</pre>
  {footer_html}
  <pre class="ascii-hidden ascii-raw">{html.escape(raw_ascii)}</pre>
</div>
"""

    def full_document(self, ascii_html, raw_ascii, title, options: RenderOptions):
        return f"""<!DOCTYPE html>
<html lang=\"de\">
<head>
<meta charset=\"UTF-8\">
<meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
<title>{html.escape(title)}</title>
<style>{self.css(options, embed=False)}</style>
</head>
<body>
{self.terminal_block(ascii_html, raw_ascii, title, options, root_id='asciiTerminal', embed=False)}
{self.controls_js()}
</body>
</html>
"""

    def art_only_document(self, ascii_html, raw_ascii, title, options: RenderOptions):
        footer_html = ""
        mode = getattr(options, "export_mode", "Bild + Programmname")
        if mode == "Bild + Programmname":
            footer_html = f'<div class="ascii-export-footer">{html.escape(SOFTWARE_NAME)}</div>'
        return f"""<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{html.escape(title)}</title>
<style>{self.css(options, embed=True)}
html, body {{ margin: 0; padding: 0; background: transparent; }}
.ascii-terminal-embed {{ background: transparent; }}
.ascii-art-only {{ display: inline-flex; flex-direction: column; align-items: flex-start; background: transparent; }}
.ascii-art-only .ascii-art {{ padding: 0; margin: 0; background: transparent; align-self: flex-start; }}
.ascii-export-footer {{ display: table; align-self: flex-end; margin: 8px 0 0 0; padding: 10px 12px; color: #7aa78b; background: #050505; border: 1px solid #2c6b3f; box-shadow: 0 0 10px rgba(255, 0, 255, .35), inset 0 0 10px rgba(0, 255, 100, .08); font-family: Consolas, "Courier New", monospace; font-size: 12px; line-height: 1.25; text-align: right; box-sizing: border-box; }}
</style>
</head>
<body>
<div id="asciiImage" class="ascii-terminal-embed {self.effect_class(options.effect)} ascii-art-only">
  <pre class="ascii-art">{ascii_html}</pre>
  {footer_html}
  <pre class="ascii-hidden ascii-raw">{html.escape(raw_ascii)}</pre>
</div>
</body>
</html>
"""

    def embed_document(self, ascii_html, raw_ascii, title, options: RenderOptions):
        return f"""<!-- ASCII Terminal Embed: CSS + HTML + Script in bestehende Seite kopieren -->
<style>{self.css(options, embed=True)}</style>
{self.terminal_block(ascii_html, raw_ascii, title, options, root_id='asciiTerminalEmbed', embed=True)}
{self.controls_js()}
"""


class LivePreviewServer:
    def __init__(self):
        self.tempdir = tempfile.TemporaryDirectory(prefix="ascii_html_preview_")
        self.root = Path(self.tempdir.name)
        self.payload_path = self.root / "payload.json"
        self.index_path = self.root / "index.html"
        self.server = None
        self.thread = None
        self.url = ""
        self.write_index()
        self.write_payload("<em style='color:#888'>Noch kein Bild geladen.</em>", "")

    def free_port(self):
        s = socket.socket()
        s.bind(("127.0.0.1", 0))
        port = s.getsockname()[1]
        s.close()
        return port

    def start(self):
        if self.server:
            return self.url
        port = self.free_port()
        directory = str(self.root)

        class Handler(SimpleHTTPRequestHandler):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, directory=directory, **kwargs)
            def log_message(self, format, *args):
                return

        self.server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.url = f"http://127.0.0.1:{port}/index.html"
        return self.url

    def write_index(self):
        self.index_path.write_text("""<!DOCTYPE html>
<html lang="de"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>ASCII Live Preview</title>
<style id="dynamicCss"></style>
<style>body{margin:0;background:#000;color:#ddd;font-family:Consolas,monospace}.preview-note{padding:10px;background:#050505;color:#00ff66;border-bottom:1px solid #222;font-size:13px}</style>
</head><body><div class="preview-note">LIVE PREVIEW - Änderungen aus der GUI werden automatisch übernommen.</div><div id="app"></div>
<script>
let last='';
async function tick(){
  try{
    const r = await fetch('payload.json?ts=' + Date.now(), {cache:'no-store'});
    const p = await r.json();
    if(p.version !== last){
      last = p.version;
      document.getElementById('dynamicCss').textContent = p.css;
      document.getElementById('app').innerHTML = p.html;
      if(p.script && !window.__asciiControlsLoaded){
        const s=document.createElement('script'); s.textContent=p.script; document.body.appendChild(s); window.__asciiControlsLoaded=true;
      }
    }
  }catch(e){}
}
setInterval(tick, 500); tick();
</script></body></html>""", encoding="utf-8")

    def write_payload(self, block_html, css, script=""):
        data = {"version": str(time.time()), "html": block_html, "css": css, "script": script}
        self.payload_path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

    def open(self):
        webbrowser.open(self.start())

    def shutdown(self):
        try:
            if self.server:
                self.server.shutdown()
        except Exception:
            pass
        try:
            self.tempdir.cleanup()
        except Exception:
            pass


class RetroAsciiApp:
    def __init__(self, root):
        self.root = root
        self.root.title(SOFTWARE_NAME)
        self.window_width = 1680
        self.window_height = 980
        self.root.minsize(1500, 900)
        self.root.configure(bg="#050505")
        self.center_start_window()
        self.root.after(120, self.maximize_start_window)
        self.root.bind("<F11>", self.toggle_borderless_fullscreen)
        self.root.bind("<Escape>", self.exit_borderless_fullscreen)
        self.renderer = AsciiRenderer()
        self.builder = HtmlBuilder()
        self.svg_builder = SvgBuilder()
        self.preview_server = LivePreviewServer()
        self.preview_after = None
        self.ui_blink_after = None
        self.sprite_after = None
        self.blink_state = False
        self.sprite_phase = 0
        self.retro_after = None
        self.reset_pulse_after = None
        self.reset_pulse_state = False
        self.retro_rotation_index = 0
        self.preview_browser_opened = False
        self.themable_widgets = []
        self.last_rows = []
        self.last_ascii_html = ""
        self.last_raw_ascii = ""
        self.thumb_image = None

        self.vars = {
            "image_path": tk.StringVar(value=""),
            "width_chars": tk.IntVar(value=140),
            "charset_name": tk.StringVar(value="Standard fein"),
            "custom_charset": tk.StringVar(value="w@ltrone1"),
            "use_custom_charset": tk.BooleanVar(value=True),
            "menu_style": tk.StringVar(value="CRT"),
            "palette_name": tk.StringVar(value="Originalfarben"),
            "use_gradient": tk.BooleanVar(value=True),
            "bg_color": tk.StringVar(value="#000000"),
            "transparent_black": tk.BooleanVar(value=True),
            "black_threshold": tk.IntVar(value=18),
            "invert_luminance": tk.BooleanVar(value=False),
            "terminal_font": tk.StringVar(value="Consolas"),
            "html_font_size": tk.IntVar(value=8),
            "line_height": tk.DoubleVar(value=1.0),
            "letter_spacing": tk.DoubleVar(value=0.0),
            "effect": tk.StringVar(value="CRT"),
            "show_titlebar": tk.BooleanVar(value=True),
            "show_toolbar": tk.BooleanVar(value=True),
            "interactive_controls": tk.BooleanVar(value=True),
            "export_embed": tk.BooleanVar(value=False),
            "auto_browser_preview": tk.BooleanVar(value=True),
            "show_retro_toys": tk.BooleanVar(value=True),
            "retro_motif": tk.StringVar(value="Atari 2600"),
            "auto_rotate_retro_motifs": tk.BooleanVar(value=True),
            "retro_animation": tk.BooleanVar(value=True),
            "show_export_branding": tk.BooleanVar(value=True),
            "export_mode": tk.StringVar(value="Bild + Programmname"),
            "export_scale": tk.StringVar(value="2x"),
            "png_transparent": tk.BooleanVar(value=True),
        }
        self.status = tk.StringVar(value="Bild laden, Stil wählen, Live-Vorschau öffnen und HTML exportieren.")
        self.image_name_var = tk.StringVar(value="Noch kein Bild geladen")
        self.custom_charset_notice_var = tk.StringVar(value="")
        self.setup_style()
        self.build_ui()
        self.bind_changes()
        self.schedule_preview()
        self.start_load_button_blink()
        self.draw_internal_preview()
        self.start_retro_rotation()

    def center_start_window(self):
        width = getattr(self, "window_width", 1680)
        height = getattr(self, "window_height", 980)
        self.root.update_idletasks()
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        x = max(0, (screen_w - width) // 2)
        y = max(0, (screen_h - height) // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def maximize_start_window(self):
        # Beim Start maximiert oeffnen, aber nicht randlos erzwingen.
        # So bleiben Taskleiste und Fensterbuttons normal nutzbar.
        try:
            self.root.state("zoomed")
            return
        except tk.TclError:
            pass
        try:
            self.root.attributes("-zoomed", True)
            return
        except tk.TclError:
            pass
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        self.root.geometry(f"{screen_w}x{screen_h}+0+0")

    def toggle_borderless_fullscreen(self, event=None):
        current = bool(self.root.attributes("-fullscreen"))
        self.root.attributes("-fullscreen", not current)
        return "break"

    def exit_borderless_fullscreen(self, event=None):
        try:
            self.root.attributes("-fullscreen", False)
        except tk.TclError:
            pass
        return "break"

    def current_skin(self):
        return "Retro Dark"

    def skin_colors(self):
        return {
            "root": "#050505", "panel": "#0B0F0B", "text": "#D7FFD7", "muted": "#9FD09F",
            "accent": "#00FF66", "accent2": "#003B18", "entry_bg": "#001B0B", "entry_fg": "#D7FFD7",
            "entry_insert": "#00FF66", "scale_bg": "#0B0F0B", "scale_fg": "#00FF66", "trough": "#001E0C",
            "canvas": "#000000", "tab": "#101810", "tab_sel": "#003B18", "tab_fg": "#9FEF9F",
        }

    def setup_style(self):
        style = ttk.Style(self.root)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        self.apply_gui_skin(initial=True)

    def apply_gui_skin(self, initial=False):
        colors = self.skin_colors()
        style = ttk.Style(self.root)
        self.root.configure(bg=colors["root"])
        style.configure("Retro.TFrame", background=colors["root"])
        style.configure("Panel.TFrame", background=colors["panel"], borderwidth=1, relief="solid")
        style.configure("Retro.TLabel", background=colors["root"], foreground=colors["text"], font=("Consolas", 10))
        style.configure("Title.TLabel", background=colors["root"], foreground=colors["accent"], font=("Consolas", 18, "bold"))
        style.configure("Section.TLabel", background=colors["panel"], foreground=colors["accent"], font=("Consolas", 11, "bold"))
        style.configure("Hint.TLabel", background=colors["panel"], foreground=colors["muted"], font=("Consolas", 9))
        style.configure("Retro.TButton", background=colors["tab"], foreground=colors["text"], borderwidth=1, font=("Consolas", 10))
        style.map("Retro.TButton", background=[("active", colors["tab_sel"])], foreground=[("active", "#FFFFFF")])
        style.configure("Accent.TButton", background=colors["accent2"], foreground=colors["accent"], borderwidth=1, font=("Consolas", 11, "bold"))
        style.map("Accent.TButton", background=[("active", "#006B2A")], foreground=[("active", "#FFFFFF")])
        style.configure("Retro.TCheckbutton", background=colors["panel"], foreground=colors["text"], font=("Consolas", 9))
        style.map("Retro.TCheckbutton", background=[("active", colors["panel"])], foreground=[("active", colors["accent"])])
        style.configure("Retro.TNotebook", background=colors["root"], borderwidth=0)
        style.configure("Retro.TNotebook.Tab", background=colors["tab"], foreground=colors["tab_fg"], padding=(12, 7), font=("Consolas", 10, "bold"))
        style.map("Retro.TNotebook.Tab", background=[("selected", colors["tab_sel"]), ("active", colors["accent2"])], foreground=[("selected", colors["accent"]), ("active", "#FFFFFF")], padding=[("selected", (18, 10)), ("!selected", (12, 7))])
        style.configure("TCombobox", fieldbackground=colors["entry_bg"], background=colors["entry_bg"], foreground=colors["entry_fg"], arrowcolor=colors["accent"], bordercolor=colors["accent2"], lightcolor=colors["accent2"], darkcolor=colors["accent2"])
        style.map("TCombobox", fieldbackground=[("readonly", colors["entry_bg"])], foreground=[("readonly", colors["entry_fg"])])
        for widget, kind in getattr(self, "themable_widgets", []):
            try:
                if kind == "entry":
                    widget.configure(bg=colors["entry_bg"], fg=colors["entry_fg"], insertbackground=colors["entry_insert"], highlightbackground=colors["accent2"], highlightcolor=colors["accent"], selectbackground=colors["accent2"], selectforeground="#FFFFFF")
                elif kind == "scale":
                    widget.configure(bg=colors["scale_bg"], fg=colors["scale_fg"], troughcolor=colors["trough"], activebackground=colors["accent"])
                elif kind == "canvas":
                    widget.configure(bg=colors["canvas"], highlightbackground=colors["accent2"])
                elif kind == "tab_canvas":
                    widget.configure(bg=colors["panel"])
                elif kind == "load_button":
                    widget.configure(bg="#001B0B", fg="#00FF66", activebackground="#003B18", activeforeground="#FFFFFF", highlightbackground="#00AA44", highlightcolor="#00FF66")
            except Exception:
                pass
        if not initial:
            self.draw_internal_preview()

    def build_ui(self):
        main = ttk.Frame(self.root, style="Retro.TFrame", padding=14)
        main.pack(fill="both", expand=True)
        main.columnconfigure(0, weight=0)
        main.columnconfigure(1, weight=1)
        main.rowconfigure(1, weight=1)

        header = ttk.Frame(main, style="Retro.TFrame")
        header.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        header.columnconfigure(0, weight=1)
        ttk.Label(header, text=SOFTWARE_NAME, style="Title.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(header, text="HTML-only | Bild-only | echter Browser-Live-Preview", style="Retro.TLabel").grid(row=1, column=0, sticky="w")
        ttk.Button(header, text="⚙ Einstellungen", command=self.open_app_settings_tab, style="Retro.TButton").grid(row=0, column=1, rowspan=2, sticky="ne", padx=(12, 0))

        left = ttk.Frame(main, style="Panel.TFrame", padding=12)
        left.grid(row=1, column=0, sticky="nsw", padx=(0, 12))
        left.configure(width=720)
        left.pack_propagate(False)

        right = ttk.Frame(main, style="Panel.TFrame", padding=12)
        right.grid(row=1, column=1, sticky="nsew")
        right.rowconfigure(2, weight=1)
        right.columnconfigure(0, weight=1)

        ttk.Label(left, text="COMMAND MENU", style="Section.TLabel").pack(anchor="w", pady=(0, 8))
        self.load_button = tk.Button(left, text=">>> PRESS START: BILD LADEN <<<", command=self.load_image, bg="#001B0B", fg="#00FF66", activebackground="#003B18", activeforeground="#FFFFFF", relief="solid", bd=2, highlightthickness=2, highlightbackground="#00AA44", font=("Consolas", 11, "bold"), cursor="hand2")
        self.load_button.pack(fill="x", ipady=5, pady=(0, 8))
        self.themable_widgets.append((self.load_button, "load_button"))
        self.notebook = ttk.Notebook(left, style="Retro.TNotebook")
        self.notebook.pack(fill="both", expand=True)

        self.retro_toys_frame = ttk.Frame(left, style="Panel.TFrame", padding=(0, 10, 0, 0))
        self.retro_toys_frame.pack(fill="x")
        ttk.Label(self.retro_toys_frame, text="RETRO-ECKE", style="Section.TLabel").pack(anchor="w", pady=(0, 6))
        self.retro_toys_canvas = tk.Canvas(self.retro_toys_frame, height=132, bg="#000000", highlightthickness=1, highlightbackground="#1E3A1E")
        self.retro_toys_canvas.pack(fill="x")
        self.themable_widgets.append((self.retro_toys_canvas, "canvas"))

        tab_settings_shell = ttk.Frame(self.notebook, style="Panel.TFrame")
        tab_export_shell = ttk.Frame(self.notebook, style="Panel.TFrame")
        self.tab_app_settings_shell = ttk.Frame(self.notebook, style="Panel.TFrame")
        self.notebook.add(tab_settings_shell, text="Palette")
        self.notebook.add(tab_export_shell, text="Export")
        self.notebook.add(self.tab_app_settings_shell, text="⚙ Einstellungen")

        tab_settings = self.make_scrollable_tab(tab_settings_shell)
        tab_export = self.make_scrollable_tab(tab_export_shell)
        tab_app_settings = self.make_scrollable_tab(self.tab_app_settings_shell)
        self.build_settings_tab(tab_settings)
        self.build_export_tab(tab_export)
        self.build_app_settings_tab(tab_app_settings)

        ttk.Label(right, text="BROWSER LIVE-PREVIEW / ARCADE STATUS", style="Section.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(right, textvariable=self.image_name_var, style="Hint.TLabel", wraplength=760).grid(row=0, column=0, sticky="e")
        preview_controls = ttk.Frame(right, style="Panel.TFrame")
        preview_controls.grid(row=1, column=0, sticky="ew", pady=(8, 8))
        ttk.Button(preview_controls, text="Browser Live-Vorschau öffnen", command=self.open_live_preview, style="Accent.TButton").pack(side="left", padx=(0, 8))
        ttk.Button(preview_controls, text="Vorschau aktualisieren", command=self.update_preview_now, style="Retro.TButton").pack(side="left", padx=(0, 8))
        ttk.Checkbutton(preview_controls, text="Auto-Browser", variable=self.vars["auto_browser_preview"], style="Retro.TCheckbutton").pack(side="left", padx=(0, 8))
        ttk.Label(preview_controls, textvariable=self.status, style="Hint.TLabel").pack(side="left", fill="x", expand=True)

        self.terminal_canvas = tk.Canvas(right, bg="#000000", highlightthickness=1, highlightbackground="#1E3A1E")
        self.themable_widgets.append((self.terminal_canvas, "canvas"))
        self.terminal_canvas.grid(row=2, column=0, sticky="nsew")
        self.terminal_canvas.bind("<Configure>", lambda e: self.draw_internal_preview())

        danger_bar = ttk.Frame(right, style="Panel.TFrame")
        danger_bar.grid(row=3, column=0, sticky="ew", pady=(8, 0))
        danger_bar.columnconfigure(0, weight=1)
        self.reset_button = tk.Button(
            danger_bar,
            text="☢ RETRO NUKE RESET ☢\nALLE SETTINGS AUF STANDARD",
            command=self.reset_all_to_defaults,
            bg="#260000", fg="#FFCC33", activebackground="#D00000", activeforeground="#FFFFFF",
            relief="raised", bd=4, highlightthickness=3, highlightbackground="#FF3030",
            font=("Consolas", 11, "bold"), cursor="hand2", justify="center", padx=16, pady=5
        )
        self.reset_button.grid(row=0, column=1, sticky="e")
        self.reset_button.bind("<Enter>", lambda e: self.reset_button.configure(bg="#7A0000", fg="#FFFFFF", text="☢ ARM RETRO NUKE? ☢\nKLICK = RESET"))
        self.reset_button.bind("<Leave>", lambda e: self.reset_button.configure(bg="#260000", fg="#FFCC33", text="☢ RETRO NUKE RESET ☢\nALLE SETTINGS AUF STANDARD"))
        self.refresh_retro_toys_visibility()
        self.draw_retro_toys()
        self.start_reset_button_pulse()


    def make_scrollable_tab(self, parent):
        # Das Startfenster ist jetzt bewusst groesser.
        # Dadurch passen die Menues ohne separate Tab-Scrollbar hinein.
        frame = ttk.Frame(parent, style="Panel.TFrame", padding=10)
        frame.pack(fill="both", expand=True)
        return frame

    def start_load_button_blink(self):
        if not hasattr(self, "load_button"):
            return
        if self.vars["image_path"].get():
            self.load_button.configure(text="[ OK ] BILD GELADEN - NEUES BILD LADEN")
            return
        self.blink_state = not self.blink_state
        bg1, fg1, bg2, fg2 = "#001B0B", "#00FF66", "#00FF66", "#001B0B"
        self.load_button.configure(
            text=(">>> PRESS START: BILD LADEN <<<" if self.blink_state else "*** INSERT IMAGE TO CONTINUE ***"),
            bg=(bg1 if self.blink_state else bg2),
            fg=(fg1 if self.blink_state else fg2),
        )
        self.ui_blink_after = self.root.after(650, self.start_load_button_blink)

    def start_sprite_animation(self):
        self.sprite_phase = (self.sprite_phase + 1) % 100000
        self.draw_internal_preview()
        self.sprite_after = self.root.after(700, self.start_sprite_animation)

    def refresh_retro_toys_visibility(self):
        frame = getattr(self, "retro_toys_frame", None)
        if not frame:
            return
        if self.vars["show_retro_toys"].get():
            if not frame.winfo_manager():
                frame.pack(fill="x")
            self.draw_retro_toys()
        else:
            try:
                frame.pack_forget()
            except Exception:
                pass

    def start_retro_rotation(self):
        if self.retro_after:
            try:
                self.root.after_cancel(self.retro_after)
            except Exception:
                pass
            self.retro_after = None
        if self.vars.get("show_retro_toys").get() and self.vars.get("auto_rotate_retro_motifs").get():
            self.retro_after = self.root.after(3200, self.rotate_retro_motif)

    def rotate_retro_motif(self):
        if not self.vars.get("show_retro_toys").get() or not self.vars.get("auto_rotate_retro_motifs").get():
            self.retro_after = None
            return
        motifs = list(RETRO_MOTIFS)
        current = self.vars["retro_motif"].get()
        try:
            idx = motifs.index(current)
        except ValueError:
            idx = self.retro_rotation_index
        idx = (idx + 1) % len(motifs)
        self.retro_rotation_index = idx
        self.vars["retro_motif"].set(motifs[idx])
        self.draw_retro_toys()
        self.retro_after = self.root.after(3200, self.rotate_retro_motif)

    def draw_retro_toys(self):
        canvas = getattr(self, "retro_toys_canvas", None)
        if not canvas:
            return
        if not self.vars["show_retro_toys"].get():
            canvas.delete("all")
            return
        canvas.delete("all")
        canvas.update_idletasks()
        w = max(620, canvas.winfo_width())
        h = max(120, canvas.winfo_height())
        tick = int(time.time() * 4) if self.vars.get("retro_animation").get() else 0
        jitter = (tick % 3) - 1 if self.vars.get("retro_animation").get() else 0
        canvas.create_rectangle(0, 0, w, h, fill="#000000", outline="")
        canvas.create_rectangle(8 + jitter, 8, w - 8 + jitter, h - 8, outline="#1f5d38")
        motif = self.vars["retro_motif"].get()
        auto = "AUTO" if self.vars["auto_rotate_retro_motifs"].get() else "MANUAL"
        title = f"{auto} MOTIF {RETRO_MOTIFS.index(motif)+1:02d}/20: {motif}" if motif in RETRO_MOTIFS else f"MOTIF: {motif}"
        title_color = "#00ff66" if tick % 2 == 0 else "#7CFFB2"
        canvas.create_text(18 + jitter, 18, anchor="w", text=title, fill=title_color, font=("Consolas", 10, "bold"))
        # dezenter, beweglicher Scanline-/Glitch-Hintergrund
        if self.vars.get("retro_animation").get():
            for yy in range(36 + (tick % 8), h - 12, 14):
                canvas.create_line(12, yy, w - 12, yy, fill="#062b16")
            if tick % 5 == 0:
                canvas.create_line(18, 34, w - 18, 34, fill="#ff4ddb")
                canvas.create_line(22, 35, w - 22, 35, fill="#00d9ff")
        items = RETRO_MOTIF_ITEMS.get(motif, RETRO_MOTIF_ITEMS["Atari 2600"])
        positions = [(85, 72), (235, 72), (385, 72), (535, 72)]
        for i, ((kind, label), (x, y)) in enumerate(zip(items, positions)):
            wobble = ((tick + i) % 3) - 1 if self.vars.get("retro_animation").get() else 0
            self.draw_retro_icon(canvas, kind, x + wobble, y)
            canvas.create_text(x, 114, text=label, fill="#9fd09f", font=("Consolas", 9))

    def draw_retro_icon(self, canvas, kind, x, y):
        line = "#00ff66"
        alt = "#ff4ddb"
        blue = "#00d9ff"
        yellow = "#ffcc33"
        red = "#ff4d4d"
        gray = "#c0c0c0"
        def px(x0, y0, x1, y1, color=line, fill=""):
            canvas.create_rectangle(x + x0, y + y0, x + x1, y + y1, outline=color, fill=fill, width=1)
        if kind == "joystick":
            px(-22, 10, 22, 18, blue)
            px(-10, 0, 10, 10, line)
            canvas.create_line(x, y - 20, x, y + 2, fill=line, width=2)
            canvas.create_oval(x - 5, y - 28, x + 5, y - 18, outline=alt, width=2)
            canvas.create_oval(x + 12, y + 2, x + 18, y + 8, outline=red)
            canvas.create_oval(x + 20, y - 2, x + 26, y + 4, outline=yellow)
        elif kind == "gamepad":
            canvas.create_line(x - 24, y, x - 14, y - 10, x + 14, y - 10, x + 24, y, x + 14, y + 10, x - 14, y + 10, x - 24, y, fill=line, smooth=True, width=2)
            canvas.create_line(x - 12, y, x - 4, y, fill=gray, width=2)
            canvas.create_line(x - 8, y - 4, x - 8, y + 4, fill=gray, width=2)
            canvas.create_oval(x + 8, y - 5, x + 14, y + 1, outline=alt)
            canvas.create_oval(x + 15, y - 1, x + 21, y + 5, outline=blue)
        elif kind == "invader":
            pts = [(-18,-10),(-10,-18),(-2,-18),(2,-18),(10,-18),(18,-10),(18,-2),(10,-2),(6,6),(14,14),(6,14),(2,6),(-2,6),(-6,14),(-14,14),(-6,6),(-10,-2),(-18,-2)]
            canvas.create_polygon(*[coord for p in pts for coord in (x+p[0], y+p[1])], outline=line, fill="", width=2)
        elif kind == "heart":
            canvas.create_line(x, y + 16, x - 18, y - 2, x - 10, y - 14, x, y - 6, x + 10, y - 14, x + 18, y - 2, x, y + 16, fill=alt, smooth=True, width=2)
        elif kind == "floppy":
            px(-18, -18, 18, 18, blue)
            px(-10, -18, 10, -6, line)
            px(-6, 2, 6, 12, gray)
            px(6, -18, 12, -10, yellow, fill=yellow)
        elif kind == "monitor":
            px(-22, -16, 22, 10, line)
            canvas.create_line(x - 18, y - 12, x + 18, y - 12, fill=blue)
            canvas.create_line(x - 18, y - 6, x + 18, y - 6, fill=alt)
            canvas.create_line(x - 10, y + 14, x + 10, y + 14, fill=gray, width=2)
            canvas.create_line(x, y + 10, x, y + 14, fill=gray, width=2)
        elif kind == "cassette":
            px(-22, -14, 22, 14, yellow)
            px(-14, -4, 14, 4, gray)
            canvas.create_oval(x - 10, y, x - 4, y + 6, outline=line)
            canvas.create_oval(x + 4, y, x + 10, y + 6, outline=line)
        elif kind == "disk":
            canvas.create_oval(x - 18, y - 18, x + 18, y + 18, outline=gray, width=2)
            canvas.create_oval(x - 5, y - 5, x + 5, y + 5, outline=blue, width=2)
            canvas.create_line(x + 8, y - 12, x + 14, y - 18, fill=alt, width=2)
        elif kind == "ufo":
            canvas.create_oval(x - 24, y - 8, x + 24, y + 8, outline=blue, width=2)
            canvas.create_arc(x - 14, y - 18, x + 14, y + 6, start=0, extent=180, style="arc", outline=alt, width=2)
            for off in (-12, 0, 12):
                canvas.create_line(x + off, y + 8, x + off - 5, y + 22, fill=line)
        elif kind == "rocket":
            canvas.create_polygon(x, y - 24, x + 12, y - 4, x + 6, y + 18, x, y + 10, x - 6, y + 18, x - 12, y - 4, outline=line, fill="", width=2)
            canvas.create_oval(x - 4, y - 10, x + 4, y - 2, outline=blue)
            canvas.create_line(x - 5, y + 18, x - 10, y + 28, fill=red, width=2)
            canvas.create_line(x, y + 18, x, y + 30, fill=yellow, width=2)
            canvas.create_line(x + 5, y + 18, x + 10, y + 28, fill=red, width=2)
        elif kind == "atom":
            canvas.create_oval(x - 18, y - 8, x + 18, y + 8, outline=line)
            canvas.create_oval(x - 10, y - 20, x + 10, y + 20, outline=alt)
            canvas.create_oval(x - 18, y - 8, x + 18, y + 8, outline=blue)
            canvas.create_oval(x - 2, y - 2, x + 2, y + 2, outline=yellow, fill=yellow)
        elif kind == "star":
            pts = [(0,-20),(5,-6),(18,-6),(8,2),(12,16),(0,8),(-12,16),(-8,2),(-18,-6),(-5,-6)]
            canvas.create_polygon(*[coord for p in pts for coord in (x+p[0], y+p[1])], outline=yellow, fill="", width=2)
        elif kind == "boombox":
            px(-24, -14, 24, 14, gray)
            px(-18, -6, -4, 8, line)
            px(4, -6, 18, 8, line)
            px(-6, -18, 6, -10, alt)
            canvas.create_line(x - 16, y - 18, x - 10, y - 28, fill=gray, width=2)
            canvas.create_line(x + 16, y - 18, x + 10, y - 28, fill=gray, width=2)
        elif kind == "glasses":
            canvas.create_oval(x - 22, y - 8, x - 6, y + 8, outline=alt, width=2)
            canvas.create_oval(x + 6, y - 8, x + 22, y + 8, outline=blue, width=2)
            canvas.create_line(x - 6, y, x + 6, y, fill=gray, width=2)
        elif kind == "palm":
            canvas.create_line(x, y + 18, x, y - 6, fill=line, width=2)
            for dx in (-14, -6, 6, 14):
                canvas.create_line(x, y - 6, x + dx, y - 18, fill=alt if dx < 0 else blue, width=2)
        elif kind == "lightning":
            canvas.create_line(x - 8, y - 20, x + 2, y - 6, x - 2, y - 6, x + 8, y + 12, x - 4, y + 2, x, y + 2, fill=yellow, width=2)


        elif kind == "atari2600":
            px(-26, -12, 26, 12, gray)
            px(-20, -6, -4, 4, line)
            px(4, -6, 20, 4, alt)
            canvas.create_line(x - 24, y - 16, x + 24, y - 16, fill=yellow, width=2)
            canvas.create_text(x, y + 1, text="2600", fill="#00d9ff", font=("Consolas", 8, "bold"))
        elif kind == "atari7800":
            px(-28, -12, 28, 12, gray)
            canvas.create_line(x - 22, y - 6, x + 22, y - 6, fill=line, width=2)
            canvas.create_line(x - 22, y + 2, x + 22, y + 2, fill=alt, width=2)
            canvas.create_text(x, y + 12, text="7800", fill="#ffcc33", font=("Consolas", 8, "bold"))
        elif kind == "cartridge":
            px(-18, -20, 18, 20, blue)
            px(-12, -14, 12, 2, gray)
            canvas.create_text(x, y + 11, text="ROM", fill=yellow, font=("Consolas", 7, "bold"))
        elif kind == "pixelship":
            canvas.create_polygon(x, y - 22, x + 18, y + 12, x, y + 6, x - 18, y + 12, outline=line, fill="", width=2)
            canvas.create_line(x, y - 22, x, y - 34, fill=red, width=2)
        elif kind == "cabinet":
            px(-18, -26, 18, 24, blue)
            px(-12, -18, 12, 2, line)
            canvas.create_line(x - 10, y + 8, x + 10, y + 8, fill=alt, width=2)
            canvas.create_oval(x + 8, y + 12, x + 14, y + 18, outline=yellow)
        elif kind == "coin":
            canvas.create_oval(x - 15, y - 15, x + 15, y + 15, outline=yellow, width=2)
            canvas.create_text(x, y, text="25", fill=yellow, font=("Consolas", 8, "bold"))
        elif kind == "score":
            canvas.create_text(x, y - 8, text="HI", fill=alt, font=("Consolas", 12, "bold"))
            canvas.create_text(x, y + 8, text="9999", fill=line, font=("Consolas", 10, "bold"))
        elif kind == "pac":
            canvas.create_arc(x - 20, y - 20, x + 20, y + 20, start=35, extent=290, outline=yellow, style="arc", width=3)
            canvas.create_oval(x + 4, y - 10, x + 8, y - 6, outline=yellow, fill=yellow)
        elif kind == "ghost":
            canvas.create_arc(x - 18, y - 22, x + 18, y + 14, start=0, extent=180, outline=alt, width=2)
            canvas.create_line(x - 18, y - 4, x - 18, y + 18, x - 8, y + 10, x, y + 18, x + 8, y + 10, x + 18, y + 18, x + 18, y - 4, fill=alt, width=2)
            canvas.create_oval(x - 8, y - 6, x - 4, y - 2, outline=blue, fill=blue)
            canvas.create_oval(x + 5, y - 6, x + 9, y - 2, outline=blue, fill=blue)
        elif kind == "blocks":
            for bx, by, col in [(-18,-18,line),(-6,-18,alt),(6,-18,blue),(6,-6,yellow),(-6,6,line)]:
                px(bx, by, bx + 11, by + 11, col)
        elif kind == "grid":
            for off in range(-24, 25, 12):
                canvas.create_line(x + off, y - 24, x + off, y + 24, fill="#144d2a")
                canvas.create_line(x - 28, y + off, x + 28, y + off, fill="#144d2a")
            canvas.create_rectangle(x - 28, y - 24, x + 28, y + 24, outline=blue)
        elif kind == "scanline":
            px(-24, -18, 24, 18, line)
            for yy in range(-12, 17, 6):
                canvas.create_line(x - 20, y + yy, x + 20, y + yy, fill=blue)
        elif kind == "terminal":
            px(-24, -16, 24, 16, line)
            canvas.create_text(x, y, text="C:\\>", fill="#00ff66", font=("Consolas", 10, "bold"))
        elif kind == "glitchbox":
            px(-24, -18, 24, 18, alt)
            canvas.create_line(x - 20, y - 6, x + 8, y - 6, fill=blue, width=2)
            canvas.create_line(x - 8, y + 2, x + 20, y + 2, fill=line, width=2)
            canvas.create_line(x - 22, y + 10, x + 2, y + 10, fill=red, width=2)
        elif kind == "vhs":
            px(-26, -16, 26, 16, gray)
            canvas.create_oval(x - 16, y - 8, x - 6, y + 2, outline=line)
            canvas.create_oval(x + 6, y - 8, x + 16, y + 2, outline=line)
            canvas.create_text(x, y + 12, text="VHS", fill=yellow, font=("Consolas", 8, "bold"))
        elif kind == "tracking":
            for yy in range(-18, 19, 6):
                canvas.create_line(x - 24, y + yy, x + 24, y + yy + (yy % 2) * 2, fill=alt if yy % 12 else blue)
        elif kind == "tape":
            canvas.create_line(x - 22, y, x + 22, y, fill=gray, width=2)
            canvas.create_oval(x - 22, y - 12, x + 2, y + 12, outline=line)
            canvas.create_oval(x - 2, y - 12, x + 22, y + 12, outline=blue)
        elif kind == "walkman":
            px(-24, -18, 24, 18, blue)
            px(-14, -8, 14, 6, gray)
            canvas.create_line(x - 12, y - 18, x - 18, y - 28, x + 18, y - 28, x + 12, y - 18, fill=alt, width=2)
        elif kind == "headphones":
            canvas.create_arc(x - 22, y - 24, x + 22, y + 18, start=0, extent=180, outline=blue, width=2)
            px(-24, -2, -14, 16, alt)
            px(14, -2, 24, 16, alt)
        elif kind == "bolt":
            canvas.create_line(x - 8, y - 20, x + 2, y - 6, x - 2, y - 6, x + 8, y + 12, x - 4, y + 2, x, y + 2, fill=yellow, width=2)
        elif kind == "handheld":
            px(-24, -22, 24, 22, gray)
            px(-14, -14, 14, 2, blue)
            canvas.create_line(x - 16, y + 12, x - 6, y + 12, fill=line, width=2)
            canvas.create_oval(x + 8, y + 8, x + 14, y + 14, outline=alt)
        elif kind == "equalizer":
            for i, ht in enumerate([10, 24, 16, 28, 12]):
                bx = x - 20 + i * 10
                canvas.create_rectangle(bx, y + 18 - ht, bx + 6, y + 18, outline=[line, alt, blue, yellow, red][i])
        elif kind == "sunset":
            canvas.create_arc(x - 24, y - 20, x + 24, y + 28, start=0, extent=180, outline=alt, width=2)
            for yy in range(-2, 20, 6):
                canvas.create_line(x - 20, y + yy, x + 20, y + yy, fill=yellow)
        elif kind == "wirecube":
            px(-18, -18, 10, 10, blue)
            px(-8, -8, 20, 20, alt)
            for x1,y1,x2,y2 in [(-18,-18,-8,-8),(10,-18,20,-8),(-18,10,-8,20),(10,10,20,20)]:
                canvas.create_line(x+x1, y+y1, x+x2, y+y2, fill=line)
        elif kind == "modem":
            px(-24, -12, 24, 12, gray)
            for i in range(4):
                canvas.create_oval(x - 16 + i*10, y - 3, x - 12 + i*10, y + 1, outline=line, fill=line)
            canvas.create_line(x + 18, y - 12, x + 26, y - 24, fill=blue, width=2)
        elif kind == "phone":
            canvas.create_arc(x - 22, y - 18, x + 22, y + 18, start=200, extent=140, outline=alt, width=3)
            px(-20, 8, 20, 18, gray)
        elif kind == "car":
            px(-22, -2, 22, 12, red)
            canvas.create_line(x - 12, y - 2, x - 4, y - 12, x + 10, y - 12, x + 18, y - 2, fill=blue, width=2)
            canvas.create_oval(x - 18, y + 10, x - 10, y + 18, outline=yellow)
            canvas.create_oval(x + 10, y + 10, x + 18, y + 18, outline=yellow)
        elif kind == "road":
            canvas.create_line(x - 24, y + 20, x - 6, y - 18, fill=gray, width=2)
            canvas.create_line(x + 24, y + 20, x + 6, y - 18, fill=gray, width=2)
            canvas.create_line(x, y + 20, x, y - 18, fill=yellow)
        elif kind == "flag":
            canvas.create_line(x - 14, y - 20, x - 14, y + 20, fill=gray, width=2)
            for i in range(3):
                for j in range(2):
                    col = line if (i+j)%2 else alt
                    canvas.create_rectangle(x - 12 + i*10, y - 20 + j*8, x - 2 + i*10, y - 12 + j*8, outline=col)
        elif kind == "tunnel":
            for r, col in [(28,blue),(20,alt),(12,line),(4,yellow)]:
                canvas.create_rectangle(x-r, y-r, x+r, y+r, outline=col)
        elif kind == "laser":
            canvas.create_line(x - 28, y - 18, x + 28, y + 18, fill=red, width=2)
            canvas.create_line(x - 28, y + 18, x + 28, y - 18, fill=blue, width=2)
        elif kind == "spark":
            canvas.create_line(x, y - 24, x, y + 24, fill=yellow, width=2)
            canvas.create_line(x - 24, y, x + 24, y, fill=yellow, width=2)
            canvas.create_line(x - 16, y - 16, x + 16, y + 16, fill=alt)
            canvas.create_line(x - 16, y + 16, x + 16, y - 16, fill=blue)
    def draw_arcade_border(self, c, w, h):
        # Performance: die animierten Arcade-Zeichen am unteren/rechten Rand sind entfernt.
        # Die interne Vorschau bleibt dadurch ruhiger und schneller.
        return

    def open_app_settings_tab(self):
        if hasattr(self, "notebook") and hasattr(self, "tab_app_settings_shell"):
            self.notebook.select(self.tab_app_settings_shell)

    def build_app_settings_tab(self, parent):
        self.section(parent, "⚙ Ausgabe- und Interface-Einstellungen")
        ttk.Label(
            parent,
            text="Hier liegen Optionen, die eher die Ausgabe-Oberfläche und das exportierte HTML steuern.",
            style="Hint.TLabel",
            wraplength=500,
        ).pack(anchor="w", pady=(0, 8))
        ttk.Checkbutton(parent, text="CMD-Titelzeile anzeigen", variable=self.vars["show_titlebar"], style="Retro.TCheckbutton").pack(anchor="w", pady=3)
        ttk.Checkbutton(parent, text="Terminal-Toolbar anzeigen", variable=self.vars["show_toolbar"], style="Retro.TCheckbutton").pack(anchor="w", pady=3)
        ttk.Checkbutton(parent, text="Interaktive Regler im exportierten HTML", variable=self.vars["interactive_controls"], style="Retro.TCheckbutton").pack(anchor="w", pady=3)
        ttk.Label(parent, text="Programmname wird nur im Export-Modus Bild + Programmname angezeigt.", style="Hint.TLabel", wraplength=500).pack(anchor="w", pady=3)

        self.section(parent, "Retro-Spielereien")
        ttk.Checkbutton(parent, text="Retro-Spielereien im Menü anzeigen", variable=self.vars["show_retro_toys"], style="Retro.TCheckbutton").pack(anchor="w", pady=3)
        ttk.Checkbutton(parent, text="Motive automatisch wechseln", variable=self.vars["auto_rotate_retro_motifs"], style="Retro.TCheckbutton").pack(anchor="w", pady=3)
        ttk.Checkbutton(parent, text="Bewegung / Glitch-Effekt aktiv", variable=self.vars["retro_animation"], style="Retro.TCheckbutton").pack(anchor="w", pady=3)
        self.combo(parent, "Retro-Motiv", "retro_motif", RETRO_MOTIFS)
        ttk.Label(parent, text="20 kultige Retro-Motive wechseln automatisch wie ein kleiner Metasploit-Banner: Atari 2600, Atari 7800, Arcade, VHS, Walkman, Glitch, Vector Grid und mehr.", style="Hint.TLabel", wraplength=500).pack(anchor="w", pady=(0, 8))

        self.section(parent, "Browser-Vorschau")
        ttk.Checkbutton(parent, text="Browser-Vorschau nach Bildauswahl automatisch öffnen", variable=self.vars["auto_browser_preview"], style="Retro.TCheckbutton").pack(anchor="w", pady=3)

    def build_settings_tab(self, parent):
        parent.columnconfigure(0, weight=1)
        parent.columnconfigure(1, weight=1)

        left_col = ttk.Frame(parent, style="Panel.TFrame", padding=(0, 0, 8, 0))
        right_col = ttk.Frame(parent, style="Panel.TFrame", padding=(8, 0, 0, 0))
        left_col.grid(row=0, column=0, sticky="nsew")
        right_col.grid(row=0, column=1, sticky="nsew")

        # LINKS: die wichtigsten Preview-Regler direkt oben, danach die Dropdowns.
        self.section(left_col, "Regler")
        self.scale(left_col, "Breite", "width_chars", 40, 420)
        self.scale(left_col, "Schriftgröße px", "html_font_size", 5, 22)

        self.section(left_col, "Dropdowns / Auswahl")
        self.combo(left_col, "Font", "terminal_font", TERMINAL_FONTS)
        self.combo(left_col, "Look / Effekt", "effect", EFFECTS)
        palette_values = list(PALETTES.keys()) + ["Random Retro"]
        self.combo(left_col, "Farbvariationen", "palette_name", palette_values)
        self.combo(left_col, "Preset", "charset_name", list(ASCII_CHARSETS.keys()))
        ttk.Label(
            left_col,
            text="Hinweis: Presets funktionieren nur, wenn Eigene Zeichen deaktiviert ist.",
            style="Hint.TLabel",
            wraplength=300,
        ).pack(anchor="w", pady=(0, 6))

        self.section(left_col, "Eigene Zeichen")
        self.entry(left_col, "custom_charset")
        self.use_custom_charset_check = ttk.Checkbutton(
            left_col,
            text="Eigene Zeichen verwenden",
            variable=self.vars["use_custom_charset"],
            style="Retro.TCheckbutton",
        )
        self.use_custom_charset_check.pack(anchor="w", pady=(0, 4))
        ttk.Label(left_col, textvariable=self.custom_charset_notice_var, style="Hint.TLabel", wraplength=300).pack(anchor="w", pady=(0, 8))

        self.section(right_col, "Hintergrund & Optionen")
        ttk.Checkbutton(right_col, text="Farbverlauf weich mischen", variable=self.vars["use_gradient"], style="Retro.TCheckbutton").pack(anchor="w", pady=2)
        bg_action_row = ttk.Frame(right_col, style="Panel.TFrame")
        bg_action_row.pack(fill="x", pady=(4, 8))
        bg_action_row.columnconfigure(0, weight=1)
        bg_action_row.columnconfigure(1, weight=1)
        ttk.Button(bg_action_row, text="Random würfeln", command=self.reroll_random, style="Retro.TButton").grid(row=0, column=0, sticky="ew", padx=(0, 4))
        ttk.Button(bg_action_row, text="BG zurücksetzen", command=self.reset_background, style="Retro.TButton").grid(row=0, column=1, sticky="ew", padx=(4, 0))
        self.bg_picker(right_col)

        # RECHTS: die restlichen Regler bleiben rechts.
        self.section(right_col, "Regler")
        self.scale(right_col, "Schwellwert", "black_threshold", 0, 90)
        self.scale_double(right_col, "Zeilenhöhe", "line_height", 0.70, 1.60, 0.05)
        self.scale_double(right_col, "Zeichenabstand", "letter_spacing", -1.0, 3.0, 0.1)
        ttk.Button(right_col, text="Proportionen zurücksetzen", command=self.reset_proportions, style="Retro.TButton").pack(fill="x", pady=(0, 8))

        self.section(right_col, "Schalter")
        ttk.Checkbutton(right_col, text="Dunkle Pixel als Leerzeichen", variable=self.vars["transparent_black"], style="Retro.TCheckbutton").pack(anchor="w", pady=2)
        ttk.Checkbutton(right_col, text="Helligkeit invertieren", variable=self.vars["invert_luminance"], style="Retro.TCheckbutton").pack(anchor="w", pady=2)
        ttk.Label(
            right_col,
            text="Look/Effekt wird in der Browser-Livevorschau exakt als HTML/CSS angezeigt.",
            style="Hint.TLabel",
            wraplength=240,
        ).pack(anchor="w", pady=(8, 4))


    def build_style_tab(self, parent):
        self.section(parent, "Größe / Zeichenanzahl")
        self.scale(parent, "Breite", "width_chars", 40, 420)

        self.section(parent, "Stil / ASCII-Zeichensatz")
        self.combo(parent, "Preset", "charset_name", list(ASCII_CHARSETS.keys()))
        ttk.Label(parent, text="Eigene Zeichen: dunkel → hell. Genau dieses Feld ist absichtlich groß und kontrastreich. Beispiele: █ ▓ ▒ ░ . oder @ # + . Leer", style="Hint.TLabel", wraplength=340).pack(anchor="w", pady=(4, 2))
        self.entry(parent, "custom_charset")

        self.section(parent, "Farben")
        self.combo(parent, "Palette", "palette_name", list(PALETTES.keys()) + ["Random Retro"])
        ttk.Checkbutton(parent, text="Farbverlauf weich mischen", variable=self.vars["use_gradient"], style="Retro.TCheckbutton").pack(anchor="w", pady=2)
        ttk.Button(parent, text="Random Retro neu würfeln", command=self.reroll_random, style="Retro.TButton").pack(fill="x", pady=(4, 8))
        self.bg_picker(parent)

        self.section(parent, "Schwarz als transparent / keine Zeichen")
        ttk.Checkbutton(parent, text="Dunkle Pixel als Leerzeichen", variable=self.vars["transparent_black"], style="Retro.TCheckbutton").pack(anchor="w", pady=2)
        self.scale(parent, "Schwellwert", "black_threshold", 0, 90)
        ttk.Checkbutton(parent, text="Helligkeit invertieren", variable=self.vars["invert_luminance"], style="Retro.TCheckbutton").pack(anchor="w", pady=2)

    def build_html_tab(self, parent):
        self.section(parent, "Terminal Schrift")
        self.combo(parent, "Font", "terminal_font", TERMINAL_FONTS)
        self.scale(parent, "Schriftgröße px", "html_font_size", 5, 22)
        self.scale_double(parent, "Zeilenhöhe", "line_height", 0.70, 1.60, 0.05)
        self.scale_double(parent, "Zeichenabstand", "letter_spacing", -1.0, 3.0, 0.1)

        self.section(parent, "Terminal Effekte")
        self.combo(parent, "Effekt", "effect", EFFECTS)
        ttk.Checkbutton(parent, text="CMD-Titelzeile anzeigen", variable=self.vars["show_titlebar"], style="Retro.TCheckbutton").pack(anchor="w", pady=2)
        ttk.Checkbutton(parent, text="Terminal-Toolbar anzeigen", variable=self.vars["show_toolbar"], style="Retro.TCheckbutton").pack(anchor="w", pady=2)
        ttk.Checkbutton(parent, text="Interaktive Regler im exportierten HTML", variable=self.vars["interactive_controls"], style="Retro.TCheckbutton").pack(anchor="w", pady=2)

    def build_export_tab(self, parent):
        self.section(parent, "Export-Modus")
        self.combo(parent, "Modus", "export_mode", EXPORT_MODES)
        ttk.Label(
            parent,
            text="Nur ASCII-Bild = sauber zum Einbetten. Bild + Programmname = dezentes Branding. Terminal-Frame = kompletter Retro-Terminal-Look. Embed = HTML-Ausschnitt.",
            style="Hint.TLabel",
            wraplength=340,
        ).pack(anchor="w", pady=(0, 8))

        self.section(parent, "Größe / Skalierung")
        self.combo(parent, "Export-Größe", "export_scale", EXPORT_SCALES)
        ttk.Label(parent, text="Skalierung wirkt auf SVG und PNG. HTML bleibt flexibel per CSS.", style="Hint.TLabel", wraplength=340).pack(anchor="w", pady=(0, 8))
        ttk.Checkbutton(parent, text="PNG mit transparentem Hintergrund", variable=self.vars["png_transparent"], style="Retro.TCheckbutton").pack(anchor="w", pady=(0, 8))

        self.section(parent, "Datei exportieren")
        ttk.Button(parent, text="HTML exportieren", command=self.export_html, style="Accent.TButton").pack(fill="x", pady=(6, 8))
        ttk.Button(parent, text="SVG/Vektor exportieren", command=self.export_svg, style="Retro.TButton").pack(fill="x", pady=(0, 8))
        ttk.Button(parent, text="PNG exportieren", command=self.export_png, style="Retro.TButton").pack(fill="x", pady=(0, 8))

        self.section(parent, "Vorschau")
        ttk.Checkbutton(parent, text="Browser-Vorschau nach Bildauswahl automatisch öffnen", variable=self.vars["auto_browser_preview"], style="Retro.TCheckbutton").pack(anchor="w", pady=(0, 8))
        ttk.Button(parent, text="Live-Vorschau öffnen", command=self.open_live_preview, style="Retro.TButton").pack(fill="x", pady=(0, 8))

    def section(self, parent, text):
        ttk.Label(parent, text=text, style="Section.TLabel").pack(anchor="w", pady=(12, 4))

    def combo(self, parent, label, key, values):
        ttk.Label(parent, text=label, style="Hint.TLabel").pack(anchor="w")
        cb = ttk.Combobox(parent, textvariable=self.vars[key], values=values, state="readonly")
        cb.pack(fill="x", pady=(0, 6))

        if key == "charset_name":
            self.charset_combo = cb
            self.update_charset_preset_state()

        def show_custom_charset_notice():
            msg = "Preset ist deaktiviert. Bitte Eigene Zeichen deaktivieren, um Presets zu nutzen."
            self.custom_charset_notice_var.set(msg)
            self.status.set(msg)
            self.blink_custom_charset_checkbox()
            try:
                self.root.bell()
            except Exception:
                pass

        def cycle_combo(event, direction):
            if key == "charset_name" and self.vars["use_custom_charset"].get():
                show_custom_charset_notice()
                return "break"
            vals = list(cb.cget("values"))
            if not vals:
                return "break"
            current = self.vars[key].get()
            try:
                idx = vals.index(current)
            except ValueError:
                idx = 0
            self.vars[key].set(vals[(idx + direction) % len(vals)])
            return "break"

        def block_if_custom_charset(event=None):
            if key == "charset_name" and self.vars["use_custom_charset"].get():
                show_custom_charset_notice()
                return "break"
            return None

        # Dropdowns koennen mit Cursor hoch/runter gewechselt werden,
        # ohne dass das Menue per Mausrad versehentlich Werte aendert.
        cb.bind("<Up>", lambda e: cycle_combo(e, -1))
        cb.bind("<Down>", lambda e: cycle_combo(e, 1))
        cb.bind("<Button-1>", block_if_custom_charset)
        cb.bind("<space>", block_if_custom_charset)
        cb.bind("<Return>", block_if_custom_charset)
        cb.bind("<<ComboboxSelected>>", lambda e: self.update_charset_preset_state() if key == "charset_name" else None, add="+")
        cb.bind("<MouseWheel>", lambda e: "break")
        cb.bind("<Button-4>", lambda e: "break")
        cb.bind("<Button-5>", lambda e: "break")
        return cb

    def update_charset_preset_state(self):
        if not hasattr(self, "charset_combo"):
            return
        # Das Preset bleibt technisch klickbar, damit ein Hinweis + Blink-Feedback erscheinen kann.
        try:
            self.charset_combo.configure(state="readonly")
        except Exception:
            pass
        if self.vars["use_custom_charset"].get():
            self.custom_charset_notice_var.set("Preset deaktiviert: Bitte Eigene Zeichen deaktivieren.")
        else:
            self.custom_charset_notice_var.set("Preset aktiv: Eigene Zeichen sind deaktiviert.")

    def blink_custom_charset_checkbox(self, cycles=6):
        widget = getattr(self, "use_custom_charset_check", None)
        if not widget:
            return
        style = ttk.Style(self.root)
        style.configure(
            "Blink.TCheckbutton",
            background="#00FF66",
            foreground="#001B0B",
            font=("Consolas", 9, "bold"),
        )

        def step(i=0):
            try:
                widget.configure(style="Blink.TCheckbutton" if i % 2 == 0 else "Retro.TCheckbutton")
            except Exception:
                return
            if i < cycles - 1:
                self.root.after(180, lambda: step(i + 1))
            else:
                try:
                    widget.configure(style="Retro.TCheckbutton")
                    widget.focus_set()
                except Exception:
                    pass

        step()

    def entry(self, parent, key):
        ent = tk.Entry(
            parent,
            textvariable=self.vars[key],
            bg="#001B0B",
            fg="#D7FFD7",
            insertbackground="#00FF66",
            relief="solid",
            bd=2,
            highlightthickness=2,
            highlightbackground="#00AA44",
            highlightcolor="#00FF66",
            font=("Consolas", 12, "bold"),
        )
        ent.pack(fill="x", ipady=6, pady=(0, 8))
        self.themable_widgets.append((ent, "entry"))
        return ent

    def scale(self, parent, label, key, minimum, maximum):
        row = ttk.Frame(parent, style="Panel.TFrame")
        row.pack(fill="x", pady=(0, 4))
        ttk.Label(row, text=label, style="Hint.TLabel").pack(side="left")
        ttk.Label(row, textvariable=self.vars[key], style="Hint.TLabel").pack(side="right")
        sc = tk.Scale(parent, from_=minimum, to=maximum, orient="horizontal", variable=self.vars[key], bg="#0B0F0B", fg="#00FF66", troughcolor="#001E0C", highlightthickness=0)
        sc.pack(fill="x", pady=(0, 6))
        self.themable_widgets.append((sc, "scale"))
        return sc

    def scale_double(self, parent, label, key, minimum, maximum, resolution):
        row = ttk.Frame(parent, style="Panel.TFrame")
        row.pack(fill="x", pady=(0, 4))
        ttk.Label(row, text=label, style="Hint.TLabel").pack(side="left")
        ttk.Label(row, textvariable=self.vars[key], style="Hint.TLabel").pack(side="right")
        sc = tk.Scale(parent, from_=minimum, to=maximum, resolution=resolution, orient="horizontal", variable=self.vars[key], bg="#0B0F0B", fg="#00FF66", troughcolor="#001E0C", highlightthickness=0)
        sc.pack(fill="x", pady=(0, 6))
        self.themable_widgets.append((sc, "scale"))
        return sc

    def bg_picker(self, parent):
        row = ttk.Frame(parent, style="Panel.TFrame")
        row.pack(fill="x", pady=(0, 8))
        ttk.Label(row, text="Hintergrund", style="Hint.TLabel").pack(side="left")
        ttk.Button(row, textvariable=self.vars["bg_color"], command=self.choose_bg, style="Retro.TButton").pack(side="right")


    def bind_changes(self):
        for key, var in self.vars.items():
            try:
                if key == "menu_style":
                    var.trace_add("write", lambda *_: self.apply_menu_style())
                elif key == "use_custom_charset":
                    var.trace_add("write", lambda *_: (self.update_charset_preset_state(), self.schedule_preview()))
                elif key in ("show_retro_toys", "retro_motif", "auto_rotate_retro_motifs", "retro_animation"):
                    var.trace_add("write", lambda *_: (self.refresh_retro_toys_visibility(), self.draw_retro_toys(), self.start_retro_rotation()))
                else:
                    var.trace_add("write", lambda *_: self.schedule_preview())
            except Exception:
                pass

    def apply_menu_style(self):
        effect = MENU_STYLE_EFFECT_MAP.get(self.vars["menu_style"].get())
        if effect and self.vars["effect"].get() != effect:
            self.vars["effect"].set(effect)
        self.schedule_preview()

    def options(self):
        return RenderOptions(
            image_path=self.vars["image_path"].get(),
            width_chars=int(self.vars["width_chars"].get()),
            charset_name=self.vars["charset_name"].get(),
            custom_charset=self.vars["custom_charset"].get(),
            use_custom_charset=bool(self.vars["use_custom_charset"].get()),
            palette_name=self.vars["palette_name"].get(),
            use_gradient=bool(self.vars["use_gradient"].get()),
            bg_color=self.vars["bg_color"].get(),
            transparent_black=bool(self.vars["transparent_black"].get()),
            black_threshold=int(self.vars["black_threshold"].get()),
            invert_luminance=bool(self.vars["invert_luminance"].get()),
            terminal_font=self.vars["terminal_font"].get(),
            html_font_size=int(self.vars["html_font_size"].get()),
            line_height=float(self.vars["line_height"].get()),
            letter_spacing=float(self.vars["letter_spacing"].get()),
            effect=self.vars["effect"].get(),
            show_titlebar=bool(self.vars["show_titlebar"].get()),
            show_toolbar=bool(self.vars["show_toolbar"].get()),
            interactive_controls=bool(self.vars["interactive_controls"].get()),
            export_embed=bool(self.vars["export_embed"].get()),
            show_export_branding=bool(self.vars["show_export_branding"].get()),
            export_mode=self.vars["export_mode"].get(),
            export_scale=self.vars["export_scale"].get(),
            png_transparent=bool(self.vars["png_transparent"].get()),
            matrix_code_overlay=False,
            matrix_code_strength=0,
        )

    def load_image(self):
        path = filedialog.askopenfilename(title="Bild laden", filetypes=[("Bilddateien", "*.jpg *.jpeg *.png *.bmp *.gif *.webp"), ("Alle Dateien", "*.*")])
        if not path:
            return
        self.vars["image_path"].set(path)
        self.image_name_var.set("Bild geladen: " + os.path.basename(path))
        if hasattr(self, "load_button"):
            self.load_button.configure(text="[ OK ] BILD GELADEN - NEUES BILD LADEN")
        self.make_thumbnail(path)
        self.schedule_preview()
        if self.vars.get("auto_browser_preview").get() and not self.preview_browser_opened:
            self.root.after(450, self.open_live_preview)
            self.preview_browser_opened = True

    def make_thumbnail(self, path):
        try:
            with Image.open(path) as img:
                thumb = img.convert("RGB")
                thumb.thumbnail((260, 160), RESAMPLE_LANCZOS)
                self.thumb_image = ImageTk.PhotoImage(thumb)
        except Exception:
            self.thumb_image = None

    def choose_bg(self):
        color = colorchooser.askcolor(color=self.vars["bg_color"].get(), parent=self.root)[1]
        if color:
            self.vars["bg_color"].set(color.upper())

    def set_original_colors(self):
        self.vars["palette_name"].set("Originalfarben")
        self.status.set("Originalfarben aus dem Bild aktiviert.")
        self.schedule_preview()

    def reroll_random(self):
        self.renderer.reroll_palette()
        self.vars["palette_name"].set("Random Retro")
        self.schedule_preview()

    def title_for_image(self):
        path = self.vars["image_path"].get()
        if path:
            return f"{Path(path).stem} ASCII Art"
        return "ASCII Art"

    def schedule_preview(self):
        if self.preview_after:
            try:
                self.root.after_cancel(self.preview_after)
            except Exception:
                pass
        self.preview_after = self.root.after(250, self.update_preview_now)

    def update_preview_now(self):
        self.preview_after = None
        try:
            opts = self.options()
            rows = self.renderer.rows_from_image(opts)
            self.last_rows = rows
            if rows:
                self.last_ascii_html = self.renderer.html_spans(rows, opts)
                self.last_raw_ascii = self.renderer.plain_text(rows)
                block = self.builder.preview_block(self.last_ascii_html, self.last_raw_ascii, self.title_for_image(), opts, root_id="asciiLive")
                css = self.builder.css(opts, embed=(getattr(opts, "export_mode", "Bild + Programmname") != "Terminal-Frame"))
                script = self.builder.controls_js().replace("<script>", "").replace("</script>", "")
                self.preview_server.write_payload(block, css, script)
                self.status.set(f"Live bereit: {len(rows[0]) if rows else 0} x {len(rows)} Zeichen | Vorschau-Modus: {opts.export_mode}")
            else:
                self.preview_server.write_payload("<div style='padding:20px;color:#00ff66'>C:&#92;ASCII&gt; Bitte Bild laden...</div>", self.builder.css(opts, embed=True), "")
                self.status.set("Bitte zuerst ein Bild laden.")
        except Exception as exc:
            self.status.set(f"Vorschau-Fehler: {exc}")
            try:
                self.preview_server.write_payload(f"<div style='padding:20px;color:#ff6666'>Vorschau-Fehler: {html.escape(str(exc))}</div>", "body{background:#000;color:#ff6666;font-family:Consolas,monospace}", "")
            except Exception:
                pass
        self.draw_internal_preview()

    def draw_internal_preview(self):
        c = self.terminal_canvas
        c.delete("all")
        w = max(400, c.winfo_width())
        h = max(300, c.winfo_height())
        opts = self.options()
        mode = getattr(opts, "export_mode", "Bild + Programmname")

        c.create_rectangle(0, 0, w, h, fill="#000000", outline="")
        c.create_text(10, 8, anchor="nw", text=f"Vorschau-Modus: {mode}", fill="#7aa78b", font=("Consolas", 10, "bold"))

        if mode in ("Terminal-Frame", "Embed"):
            c.create_rectangle(0, 30, w, 60, fill="#111111", outline="#2b2b2b")
            c.create_text(10, 45, anchor="w", text=f"C:\\Windows\\System32\\cmd.exe - {self.title_for_image()}", fill="#f2f2f2", font=("Segoe UI", 9))
            c.create_text(w-55, 45, text="-   []   X", fill="#d0d0d0", font=("Segoe UI", 9))
            toolbar_bottom = 108 if opts.show_toolbar else 64
            if opts.show_toolbar:
                c.create_rectangle(0, 60, w, toolbar_bottom, fill="#000000", outline="#1f1f1f")
                c.create_text(10, 72, anchor="w", text="Microsoft Windows [Version Retro.HTML.2]", fill="#c0c0c0", font=("Consolas", 9))
                c.create_text(10, 90, anchor="w", text=f"C:\\ASCII> render \"{self.title_for_image()}\" /palette:{opts.palette_name}", fill="#00ff66", font=("Consolas", 9))
            if self.thumb_image:
                c.create_image(w-150, toolbar_bottom + 8, anchor="n", image=self.thumb_image)
            art_top = toolbar_bottom + 14
        else:
            c.create_rectangle(8, 30, w - 8, h - 10, fill="#000000", outline="#16321b")
            if self.thumb_image:
                c.create_image(w-150, 42, anchor="n", image=self.thumb_image)
            art_top = 44

        rows = self.last_rows
        if not rows:
            c.create_text(20, max(80, art_top), anchor="nw", text="C:\\ASCII> Kein Bild geladen.", fill="#00ff66", font=("Consolas", 12))
            return

        # Internal overview preview. Exact rendering is in browser; this is a fast terminal-style approximation.
        max_cols = min(160, max(10, (w - 30) // 5))
        max_lines = min(len(rows), max(8, (h - art_top - 40) // 8))
        step_y = max(1, len(rows) // max_lines)
        font_size = max(5, min(8, opts.html_font_size))
        y = art_top
        for row in rows[::step_y][:max_lines]:
            line = row[:max_cols]
            x = 12
            for ch, color, _rgb in line:
                if ch != " ":
                    font_tuple = (opts.terminal_font, font_size)
                    if opts.charset_name in ("Punkte", "Quadrate") and not opts.use_custom_charset:
                        size = max(2, font_size - 1)
                        if opts.charset_name == "Punkte":
                            c.create_oval(x, y, x + size, y + size, outline=color, fill="")
                        else:
                            c.create_rectangle(x, y, x + size, y + size, outline=color, fill="")
                    elif opts.effect == "Glitch":
                        offset = -1 if (self.sprite_phase + int(x) + int(y)) % 2 else 1
                        c.create_text(x - 1, y + offset, anchor="nw", text=ch, fill="#FF2CDF", font=font_tuple)
                        c.create_text(x + 1, y - offset, anchor="nw", text=ch, fill="#00D9FF", font=font_tuple)
                    elif opts.effect in ("Glow Soft", "Glow Strong", "Retro CRT Glow", "Neon Terminal", "Neon Pink", "Neon Cyan", "Neon Lime", "Blue Electric", "Laser Red"):
                        glow = "#00FF66"
                        if opts.effect == "Neon Pink": glow = "#FF4DDB"
                        elif opts.effect == "Neon Cyan": glow = "#00D9FF"
                        elif opts.effect == "Neon Lime": glow = "#8CFF00"
                        elif opts.effect == "Blue Electric": glow = "#69D2FF"
                        elif opts.effect == "Laser Red": glow = "#FF3030"
                        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
                            c.create_text(x + dx, y + dy, anchor="nw", text=ch, fill=glow, font=font_tuple)
                    elif opts.effect in ("Metal Chrome", "Gold Shine", "Copper Glow"):
                        c.create_text(x + 1, y + 1, anchor="nw", text=ch, fill="#000000", font=font_tuple)
                        c.create_text(x - 1, y - 1, anchor="nw", text=ch, fill="#FFFFFF", font=font_tuple)
                    elif opts.effect == "Arcade 80s":
                        c.create_text(x + 1, y, anchor="nw", text=ch, fill="#00D9FF", font=font_tuple)
                        c.create_text(x - 1, y, anchor="nw", text=ch, fill="#FF4DDB", font=font_tuple)
                    elif opts.effect == "Mario Retro":
                        c.create_text(x + 1, y + 1, anchor="nw", text=ch, fill="#000000", font=font_tuple)
                    if not (opts.charset_name in ("Punkte", "Quadrate") and not opts.use_custom_charset):
                        c.create_text(x, y, anchor="nw", text=ch, fill=color, font=font_tuple)
                x += max(4, font_size * 0.62)
            y += max(6, int(font_size * 1.2))
        if mode == "Bild + Programmname":
            footer_font = ("Consolas", 10)
            char_step = max(4, font_size * 0.62)
            art_left = 12
            visible_cols = min(max_cols, max((len(row) for row in rows), default=max_cols))
            art_right = min(w - 12, art_left + visible_cols * char_step)
            approx_w = len(SOFTWARE_NAME) * 7 + 24
            box_w = min(max(approx_w, 260), max(260, art_right - art_left))
            box_h = 42
            box_x = max(art_left, art_right - box_w)
            box_y = min(h - box_h - 12, y + 8)
            box_y = max(34, box_y)
            c.create_rectangle(box_x - 2, box_y - 2, box_x + box_w + 2, box_y + box_h + 2, outline="#4d145f", fill="")
            c.create_rectangle(box_x, box_y, box_x + box_w, box_y + box_h, outline="#2c6b3f", fill="#050505")
            c.create_text(box_x + box_w - 12, box_y + box_h // 2, anchor="e", text=SOFTWARE_NAME, fill="#7aa78b", font=footer_font)
        self.draw_arcade_border(c, w, h)

    def open_live_preview(self):
        self.update_preview_now()
        self.preview_server.open()

    def export_scale_factor(self, opts=None):
        opts = opts or self.options()
        return {"1x": 1, "2x": 2, "4x": 4, "Druckqualität": 6}.get(getattr(opts, "export_scale", "1x"), 1)

    def export_mode_slug(self, opts=None):
        opts = opts or self.options()
        return {
            "Nur ASCII-Bild": "bild",
            "Bild + Programmname": "branding",
            "Terminal-Frame": "terminal",
            "Embed": "embed",
        }.get(getattr(opts, "export_mode", "Bild + Programmname"), "export")

    def automatic_export_name(self, extension, opts=None):
        opts = opts or self.options()
        image_name = safe_suffix(Path(opts.image_path).stem) if opts.image_path else "ascii"
        effect = safe_suffix(opts.effect)
        palette = safe_suffix(opts.palette_name)
        mode = self.export_mode_slug(opts)
        scale = safe_suffix(getattr(opts, "export_scale", "1x"))
        return f"{image_name}_ascii_{int(opts.width_chars)}w_{effect}_{palette}_{mode}_{scale}.{extension}"

    def export_png(self):
        opts = self.options()
        if not opts.image_path or not os.path.exists(opts.image_path):
            messagebox.showwarning("Hinweis", "Bitte zuerst ein Bild laden.")
            return
        self.update_preview_now()
        if not self.last_rows:
            messagebox.showerror("Fehler", "Es konnte keine PNG-Ausgabe erstellt werden.")
            return
        default_name = self.automatic_export_name("png", opts)
        path = filedialog.asksaveasfilename(
            title="PNG speichern",
            initialfile=default_name,
            defaultextension=".png",
            filetypes=[("PNG", "*.png"), ("Alle Dateien", "*.*")],
        )
        if not path:
            return
        image = self.render_png_image(self.last_rows, opts)
        image.save(path, "PNG")
        self.status.set(f"PNG gespeichert: {path}")
        if messagebox.askyesno("PNG gespeichert", "PNG wurde gespeichert. Jetzt öffnen?"):
            webbrowser.open(Path(path).as_uri())

    def find_png_font(self, size):
        candidates = [
            "C:/Windows/Fonts/consola.ttf",
            "C:/Windows/Fonts/cour.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
            "/usr/share/fonts/truetype/liberation2/LiberationMono-Regular.ttf",
        ]
        for font_path in candidates:
            try:
                if os.path.exists(font_path):
                    return ImageFont.truetype(font_path, size)
            except Exception:
                pass
        return ImageFont.load_default()

    def render_png_image(self, rows, opts):
        scale = self.export_scale_factor(opts)
        font_size = max(5, int(opts.html_font_size) * scale)
        font = self.find_png_font(font_size)
        char_w = max(1, int((int(opts.html_font_size) * 0.62 + float(opts.letter_spacing)) * scale))
        line_h = max(1, int(int(opts.html_font_size) * float(opts.line_height) * scale))
        cols = max((len(row) for row in rows), default=0)
        mode = getattr(opts, "export_mode", "Bild + Programmname")
        show_footer = mode == "Bild + Programmname"
        terminal_frame = mode == "Terminal-Frame"
        pad = 10 * scale
        frame_pad = 18 * scale if terminal_frame else 0
        titlebar_h = 28 * scale if terminal_frame else 0
        footer_h = 42 * scale if show_footer else 0
        width = max(1, int(cols * char_w + pad * 2 + frame_pad * 2))
        height = max(1, int(len(rows) * line_h + pad * 2 + frame_pad * 2 + titlebar_h + footer_h))
        bg_rgb = hex_to_rgb(opts.bg_color)
        transparent = bool(getattr(opts, "png_transparent", True)) and not terminal_frame
        bg = (0, 0, 0, 0) if transparent else (*bg_rgb, 255)
        img = Image.new("RGBA", (width, height), bg)
        draw = ImageDraw.Draw(img)
        if terminal_frame:
            draw.rectangle((4*scale, 4*scale, width-4*scale, height-4*scale), outline=(120,120,120,255), fill=(*bg_rgb, 255), width=max(1, 2*scale))
            draw.rectangle((4*scale, 4*scale, width-4*scale, 4*scale+titlebar_h), fill=(21,21,21,255), outline=(120,120,120,255), width=max(1, scale))
            draw.text((12*scale, 10*scale), f"C:\\ASCII\\EXPORT.EXE - {self.title_for_image()}", font=self.find_png_font(max(8, 10*scale)), fill=(229,229,229,255))
        y = pad + frame_pad + titlebar_h
        for row in rows:
            x = pad + frame_pad
            for ch, color, _rgb in row:
                if ch != " ":
                    rgb = hex_to_rgb(color)
                    fill = (*rgb, 255)
                    if opts.charset_name == "Punkte" and not opts.use_custom_charset:
                        r = max(1, int(font_size * 0.28))
                        cx = x + char_w // 2
                        cy = y + line_h // 2
                        draw.ellipse((cx-r, cy-r, cx+r, cy+r), outline=fill, width=max(1, int(font_size * 0.06)))
                    elif opts.charset_name == "Quadrate" and not opts.use_custom_charset:
                        s = max(1, int(font_size * 0.55))
                        x0 = x + (char_w - s) // 2
                        y0 = y + (line_h - s) // 2
                        draw.rectangle((x0, y0, x0+s, y0+s), outline=fill, width=max(1, int(font_size * 0.06)))
                    else:
                        draw.text((x, y), ch, font=font, fill=fill)
                x += char_w
            y += line_h
        if show_footer:
            footer_font = self.find_png_font(max(8, 10 * scale))
            footer_text = SOFTWARE_NAME
            try:
                bbox = draw.textbbox((0, 0), footer_text, font=footer_font)
                text_w = bbox[2] - bbox[0]
                text_h = bbox[3] - bbox[1]
            except Exception:
                text_w = len(footer_text) * max(6, 6 * scale)
                text_h = max(10 * scale, 10)
            box_pad_x = 12 * scale
            box_pad_y = 8 * scale
            box_w = text_w + box_pad_x * 2
            box_h = text_h + box_pad_y * 2
            box_x = max(pad + frame_pad, width - pad - frame_pad - box_w)
            box_y = max(pad + titlebar_h + frame_pad, height - pad - box_h)
            shadow = max(2, 2 * scale)
            draw.rectangle((box_x - shadow, box_y - shadow, box_x + box_w + shadow, box_y + box_h + shadow), outline=(77,20,95,180), fill=None, width=max(1, scale))
            draw.rectangle((box_x, box_y, box_x + box_w, box_y + box_h), fill=(5, 5, 5, 255), outline=(44, 107, 63, 255), width=max(1, scale))
            draw.text((box_x + box_pad_x, box_y + box_pad_y), footer_text, font=footer_font, fill=(122,167,139,255))
        return img

    def export_html(self):
        opts = self.options()
        if not opts.image_path or not os.path.exists(opts.image_path):
            messagebox.showwarning("Hinweis", "Bitte zuerst ein Bild laden.")
            return
        self.update_preview_now()
        if not self.last_rows:
            messagebox.showerror("Fehler", "Es konnte keine ASCII-Ausgabe erstellt werden.")
            return
        default_name = self.automatic_export_name("html", opts)
        path = filedialog.asksaveasfilename(title="HTML speichern", initialfile=default_name, defaultextension=".html", filetypes=[("HTML", "*.html"), ("Alle Dateien", "*.*")])
        if not path:
            return
        title = self.title_for_image()
        mode = getattr(opts, "export_mode", "Bild + Programmname")
        if mode == "Embed":
            doc = self.builder.embed_document(self.last_ascii_html, self.last_raw_ascii, title, opts)
        elif mode == "Terminal-Frame":
            doc = self.builder.full_document(self.last_ascii_html, self.last_raw_ascii, title, opts)
        else:
            doc = self.builder.art_only_document(self.last_ascii_html, self.last_raw_ascii, title, opts)
        Path(path).write_text(doc, encoding="utf-8")
        self.status.set(f"HTML gespeichert: {path}")
        if messagebox.askyesno("HTML gespeichert", "Datei wurde gespeichert. Jetzt im Browser öffnen?"):
            webbrowser.open(Path(path).as_uri())

    def export_svg(self):
        opts = self.options()
        if not opts.image_path or not os.path.exists(opts.image_path):
            messagebox.showwarning("Hinweis", "Bitte zuerst ein Bild laden.")
            return
        self.update_preview_now()
        if not self.last_rows:
            messagebox.showerror("Fehler", "Es konnte keine SVG-Ausgabe erstellt werden.")
            return
        default_name = self.automatic_export_name("svg", opts)
        path = filedialog.asksaveasfilename(
            title="SVG/Vektor speichern",
            initialfile=default_name,
            defaultextension=".svg",
            filetypes=[("SVG / Vektor", "*.svg"), ("Alle Dateien", "*.*")],
        )
        if not path:
            return
        doc = self.svg_builder.document(self.last_rows, self.title_for_image(), opts)
        Path(path).write_text(doc, encoding="utf-8")
        self.status.set(f"SVG gespeichert: {path}")
        if messagebox.askyesno("SVG gespeichert", "SVG wurde gespeichert. Jetzt im Browser öffnen?"):
            webbrowser.open(Path(path).as_uri())

    def reset_background(self):
        self.vars["bg_color"].set(DEFAULT_SETTINGS["bg_color"])
        self.vars["transparent_black"].set(DEFAULT_SETTINGS["transparent_black"])
        self.vars["black_threshold"].set(DEFAULT_SETTINGS["black_threshold"])
        self.vars["invert_luminance"].set(DEFAULT_SETTINGS["invert_luminance"])
        self.status.set("Hintergrund/Transparenz auf Standard zurückgesetzt.")

    def reset_proportions(self):
        self.vars["width_chars"].set(DEFAULT_SETTINGS["width_chars"])
        self.vars["html_font_size"].set(DEFAULT_SETTINGS["html_font_size"])
        self.vars["line_height"].set(DEFAULT_SETTINGS["line_height"])
        self.vars["letter_spacing"].set(DEFAULT_SETTINGS["letter_spacing"])
        self.status.set("Proportionen auf Standard zurückgesetzt.")

    def start_reset_button_pulse(self):
        if not hasattr(self, "reset_button"):
            return
        self.reset_pulse_state = not self.reset_pulse_state
        try:
            if self.reset_pulse_state:
                self.reset_button.configure(highlightbackground="#FF3030", fg="#FFCC33")
            else:
                self.reset_button.configure(highlightbackground="#FFCC33", fg="#FF7A7A")
        except Exception:
            return
        self.reset_pulse_after = self.root.after(850, self.start_reset_button_pulse)

    def reset_all_to_defaults(self):
        if not messagebox.askyesno("☢ RETRO NUKE RESET", "Alle Einstellungen wirklich auf Standard zurücksetzen?\n\nDas geladene Bild bleibt erhalten."):
            return
        keep_image = self.vars["image_path"].get()
        for key, value in DEFAULT_SETTINGS.items():
            if key in self.vars:
                self.vars[key].set(value)
        self.vars["image_path"].set(keep_image)
        self.renderer.reroll_palette()
        self.apply_gui_skin()
        self.status.set("Alle Einstellungen auf Standard zurückgesetzt.")
        self.schedule_preview()

    def on_close(self):
        for job in (self.preview_after, self.ui_blink_after, self.sprite_after, self.retro_after, self.reset_pulse_after):
            if job:
                try:
                    self.root.after_cancel(job)
                except Exception:
                    pass
        self.preview_server.shutdown()
        self.root.destroy()


def main():
    root = tk.Tk()
    app = RetroAsciiApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()


if __name__ == "__main__":
    main()
