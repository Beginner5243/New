
#!/usr/bin/env python3
"""CuteVerse preview video builder: story JSON -> scene-card MP4."""

import argparse
import json
import subprocess
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


WIDTH, HEIGHT = 720, 1280
BG = (20, 25, 45)
WHITE = (245, 245, 250)
BLUE = (80, 170, 255)
MUTED = (175, 190, 215)


def load_font(size):
    paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
    ]
    for path in paths:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def draw_wrapped(draw, text, font, x, y, max_width, color, gap=12):
    words = str(text).split()
    lines, current = [], ""

    for word in words:
        candidate = f"{current} {word}".strip()
        if draw.textbbox((0, 0), candidate, font=font)[2] <= max_width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word

    if current:
        lines.append(current)

    for line in lines:
        draw.text((x, y), line, font=font, fill=color)
        y += font.size + gap

    return y


def create_card(scene, index, total, topic, out_path):
    img = Image.new("RGB", (WIDTH, HEIGHT), BG)
    draw = ImageDraw.Draw(img)

    # Decorative gradient-like bands
    draw.rounded_rectangle(
        (28, 28, WIDTH - 28, HEIGHT - 28),
        radius=30, outline=BLUE, width=3
    )
    draw.rounded_rectangle(
        (50, 65, WIDTH - 50, 170),
        radius=24, fill=(34, 48, 78)
    )

    title_font = load_font(38)
    heading_font = load_font(28)
    body_font = load_font(32)
    small_font = load_font(23)

    draw.text((75, 95), "CUTEVERSE", font=title_font, fill=BLUE)
    draw.text(
        (75, 195),
        f"SCENE {index + 1:02d} / {total:02d}",
        font=heading_font, fill=WHITE
    )

    draw_wrapped(
        draw, topic, heading_font, 75, 250, WIDTH - 150, MUTED
    )

    character_list = scene.get("characters", [])
    if isinstance(character_list, list):
        characters = ", ".join(map(str, character_list))
    else:
        characters = str(character_list)

    y = 390
    y = draw_wrapped(
        draw, "CHARACTERS: " + characters,
        small_font, 75, y, WIDTH - 150, BLUE
    )

    y += 35
    action = scene.get("action", "")
    y = draw_wrapped(
        draw, action or scene.get("visual_prompt", "Adventure scene"),
        body_font, 75, y, WIDTH - 150, WHITE, gap=16
    )

    y += 40
    narration = scene.get("narration", "")
    draw.rounded_rectangle(
        (55, HEIGHT - 340, WIDTH - 55, HEIGHT - 85),
        radius=24, fill=(34, 48, 78)
    )
    draw.text(
        (80, HEIGHT - 305), "NARRATION",
        font=heading_font, fill=BLUE
    )
    draw_wrapped(
        draw, narration, body_font,
        80, HEIGHT - 245, WIDTH - 160, WHITE, gap=10
    )

    draw.text(
        (75, HEIGHT - 55),
        "Preview storyboard — AI animation not connected yet",
        font=small_font, fill=MUTED
    )

    img.save(out_path)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--story", required=True)
    parser.add_argument("--output", default="output/preview.mp4")
    args = parser.parse_args()

    story_path = Path(args.story)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    data = json.loads(story_path.read_text(encoding="utf-8"))
    scenes = data.get("scenes", [])

    if not scenes:
        raise SystemExit("story.json contains no scenes.")

    work = output_path.parent / "preview_frames"
    work.mkdir(parents=True, exist_ok=True)

    durations = []
    frame_files = []

    for i, scene in enumerate(scenes):
        duration = max(
            1, int(scene.get("duration_seconds", 5))
        )
        durations.append(duration)

        frame = work / f"scene_{i:04d}.png"
        create_card(
            scene, i, len(scenes),
            data.get("topic", "CuteVerse adventure"),
            frame
        )
        frame_files.append(frame)

    # FFmpeg concat manifest
    manifest = work / "concat.txt"
    with manifest.open("w", encoding="utf-8") as f:
        for frame, duration in zip(frame_files, durations):
            safe_path = str(frame.resolve()).replace("'", "'\\''")
            f.write(f"file '{safe_path}'\n")
            f.write(f"duration {duration}\n")
        f.write(f"file '{frame_files[-1].resolve()}'\n")

    command = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0",
        "-i", str(manifest),
        "-vf", "fps=24,format=yuv420p",
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-movflags", "+faststart",
        str(output_path),
    ]

    subprocess.run(command, check=True)

    print("Preview video created:", output_path)
    print("Scenes:", len(scenes))
    print("Duration:", sum(durations), "seconds")


if __name__ == "__main__":
    main()
