"""Rasterize App Store badge to match Play height. No screenshot recolor."""
from __future__ import annotations

import os
import subprocess
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent


def find_browser() -> str | None:
    candidates = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    ]
    for p in candidates:
        if os.path.exists(p):
            return p
    return None


def rasterize_appstore(height: int = 160) -> Path | None:
    svg = ROOT / "appstore-official.svg"
    out = ROOT / "appstore-badge.png"
    browser = find_browser()
    if not browser or not svg.exists():
        return None
    html_path = ROOT / "_badge_render.html"
    html_path.write_text(
        "<!doctype html><html><head><meta charset='utf-8'>"
        "<style>html,body{margin:0;padding:0;background:transparent;}"
        f"img{{height:{height}px;display:block;}}</style></head>"
        f"<body><img src='{svg.as_uri()}'></body></html>",
        encoding="utf-8",
    )
    width = int(height * 3.35)
    subprocess.run(
        [
            browser,
            "--headless=new",
            "--disable-gpu",
            "--hide-scrollbars",
            "--default-background-color=00000000",
            f"--window-size={width},{height + 20}",
            f"--screenshot={out}",
            html_path.as_uri(),
        ],
        check=False,
        capture_output=True,
    )
    if not out.exists():
        return None
    im = Image.open(out).convert("RGBA")
    bbox = im.getbbox()
    if bbox:
        im = im.crop(bbox)
    nw = int(im.size[0] * height / im.size[1])
    im = im.resize((nw, height), Image.Resampling.LANCZOS)
    im.save(out)
    return out


def normalize_play(height: int = 160) -> Path:
    src = ROOT / "googleplay-official.png"
    out = ROOT / "googleplay-badge.png"
    play = Image.open(src).convert("RGBA")
    nw = int(play.size[0] * height / play.size[1])
    play = play.resize((nw, height), Image.Resampling.LANCZOS)
    play.save(out)
    return out


def match_badge_boxes(apple: Path, play: Path, height: int = 160) -> None:
    a = Image.open(apple).convert("RGBA")
    p = Image.open(play).convert("RGBA")
    tw = max(a.size[0], p.size[0])

    def pad(im: Image.Image) -> Image.Image:
        canvas = Image.new("RGBA", (tw, height), (0, 0, 0, 0))
        canvas.paste(im, ((tw - im.size[0]) // 2, (height - im.size[1]) // 2), im)
        return canvas

    pad(a).save(apple)
    pad(p).save(play)


def main() -> None:
    apple = rasterize_appstore(160)
    play = normalize_play(160)
    if apple and play:
        match_badge_boxes(apple, play, 160)
        print("badges ok")


if __name__ == "__main__":
    main()
