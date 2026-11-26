from __future__ import annotations

import argparse
import json
import math
from pathlib import Path


def build_story(topic, characters, duration, scene_seconds, language, style):
    total_scenes = math.ceil(duration / scene_seconds)
    characters = [c.strip() for c in characters.split(",") if c.strip()]
    if not characters:
        characters = ["Main Character"]

    stages = [
        ("HOOK", "Introduce a surprising event that grabs attention."),
        ("INTRO", "Introduce the characters and the setting."),
        ("DISCOVERY", "Characters discover something unexpected."),
        ("PROBLEM", "A funny, exciting or emotional problem appears."),
        ("ATTEMPT", "Characters try to solve the problem together."),
        ("TWIST", "Add a surprising but child-friendly twist."),
        ("CLIMAX", "Show the biggest action or emotional moment."),
        ("RESOLUTION", "Solve the problem with teamwork."),
        ("ENDING", "End with a memorable visual and a sequel possibility."),
    ]

    scenes = []
    for i in range(total_scenes):
        stage, direction = stages[i % len(stages)]
        character = characters[i % len(characters)]
        next_character = characters[(i + 1) % len(characters)]

        scene = {
            "scene": i + 1,
            "stage": stage,
            "duration_seconds": min(
                scene_seconds, duration - (i * scene_seconds)
            ),
            "characters": characters,
            "action": direction,
            "story_context": topic,
            "visual_prompt": (
                f"{style}. Story: {topic}. "
                f"Scene {i+1}: {direction} "
                f"Featuring {', '.join(characters)}. "
                "Keep character designs consistent, expressive faces, "
                "cinematic composition, smooth animation, "
                "family-friendly content, no text, no watermark."
            ),
            "dialogue": (
                f"{character}: What is happening? "
                f"{next_character}: Let's figure it out together!"
            ),
            "narration": (
                f"Scene {i+1}. {direction} "
                f"The characters continue their adventure."
            ),
        }
        scenes.append(scene)

    return {
        "title": topic,
        "language": language,
        "style": style,
        "duration_seconds": duration,
        "scene_count": total_scenes,
        "characters": characters,
        "scenes": scenes,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--topic", required=True)
    parser.add_argument("--characters", default="Yeti")
    parser.add_argument("--duration", type=int, default=30)
    parser.add_argument("--scene-seconds", type=int, default=5)
    parser.add_argument("--language", default="English")
    parser.add_argument("--style", default="Cute 3D animation")
    parser.add_argument("--output", default="output/story")
    args = parser.parse_args()

    if not 30 <= args.duration <= 1800:
        raise ValueError("Duration must be between 30 and 1800 seconds.")
    if not 3 <= args.scene_seconds <= 8:
        raise ValueError("Scene duration must be 3-8 seconds.")

    result = build_story(
        args.topic,
        args.characters,
        args.duration,
        args.scene_seconds,
        args.language,
        args.style,
    )

    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)

    with open(out / "story.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    with open(out / "narration.txt", "w", encoding="utf-8") as f:
        for scene in result["scenes"]:
            f.write(scene["narration"] + "\n")

    with open(out / "dialogue.txt", "w", encoding="utf-8") as f:
        for scene in result["scenes"]:
            f.write(scene["dialogue"] + "\n")

    with open(out / "scene_prompts.txt", "w", encoding="utf-8") as f:
        for scene in result["scenes"]:
            f.write(
                f"\nSCENE {scene['scene']}\n"
                f"{scene['visual_prompt']}\n"
            )

    print(f"Story created: {result['scene_count']} scenes")
    print(f"Output: {out}")


if __name__ == "__main__":
    main()
