from PIL import Image
from collections import deque
import os

ROOT = os.path.dirname(os.path.abspath(__file__))
FILES = [
    "screen-home.jpg",
    "screen-apprendre.jpg",
    "screen-defis.jpg",
    "screen-lab.jpg",
    "screen-profil.png",
]


def remove_black_bg(path: str, out_path: str, threshold: int = 30) -> None:
    im = Image.open(path).convert("RGBA")
    pixels = im.load()
    w, h = im.size

    def is_bg(p):
        r, g, b, _a = p
        return r <= threshold and g <= threshold and b <= threshold

    visited = [[False] * h for _ in range(w)]
    q = deque()

    for x in range(w):
        q.append((x, 0))
        q.append((x, h - 1))
    for y in range(h):
        q.append((0, y))
        q.append((w - 1, y))

    while q:
        x, y = q.popleft()
        if x < 0 or y < 0 or x >= w or y >= h or visited[x][y]:
            continue
        visited[x][y] = True
        if not is_bg(pixels[x, y]):
            continue
        pixels[x, y] = (0, 0, 0, 0)
        q.extend(((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)))

    # Soften jagged edges: fade near-black pixels that touch transparency
    to_fade = []
    for x in range(w):
        for y in range(h):
            r, g, b, a = pixels[x, y]
            if a == 0:
                continue
            if r > 55 or g > 55 or b > 55:
                continue
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h and pixels[nx, ny][3] == 0:
                    # Only fade if this dark pixel is likely exterior fringe,
                    # not the solid phone bezel (which is deeper inside).
                    # Count transparent neighbors in 3x3
                    t = 0
                    for ox in range(-1, 2):
                        for oy in range(-1, 2):
                            px, py = x + ox, y + oy
                            if 0 <= px < w and 0 <= py < h and pixels[px, py][3] == 0:
                                t += 1
                    if t >= 3:
                        to_fade.append((x, y))
                    break

    for x, y in to_fade:
        r, g, b, _a = pixels[x, y]
        pixels[x, y] = (r, g, b, 0)

    # Crop to non-transparent bounds with small padding
    bbox = im.getbbox()
    if bbox:
        pad = 8
        left = max(0, bbox[0] - pad)
        top = max(0, bbox[1] - pad)
        right = min(w, bbox[2] + pad)
        bottom = min(h, bbox[3] + pad)
        im = im.crop((left, top, right, bottom))

    im.save(out_path, "PNG")
    print(f"OK {os.path.basename(path)} -> {os.path.basename(out_path)} {im.size}")


def main():
    for name in FILES:
        src = os.path.join(ROOT, name)
        out = os.path.join(ROOT, os.path.splitext(name)[0] + ".png")
        remove_black_bg(src, out)


if __name__ == "__main__":
    main()
