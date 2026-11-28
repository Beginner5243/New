from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from datetime import datetime, timezone

BEATS = [
    ("opening", "Introduce the characters and their world."),
    ("discovery", "Discover something mysterious or surprising."),
    ("curiosity", "Investigate and react with curiosity."),
    ("problem", "A funny or exciting problem appears."),
    ("attempt", "Try the first creative solution."),
    ("complication", "The first attempt creates a new complication."),
    ("teamwork", "Friends cooperate and help each other."),
    ("climax", "Face the biggest challenge of the adventure."),
    ("resolution", "Solve the problem in a satisfying way."),
    ("ending", "Finish with a memorable funny or heartwarming moment."),
]

ACTIONS = [
    "explores the colorful environment",
    "discovers a mysterious object",
    "reacts with surprise and curiosity",
    "tries to understand the new discovery",
    "attempts a funny solution",
    "accidentally creates a new problem",
    "asks a friend for help",
    "works together to solve the challenge",
    "overcomes the main obstacle",
    "celebrates with a funny ending",
]

EN = [
    "Welcome to a brand-new adventure!",
    "Look what we just discovered!",
    "What could this mysterious thing be?",
    "Uh-oh! We have a little problem!",
    "Let's try something clever!",
    "Oops! That didn't go as planned!",
    "Don't worry. Friends can help!",
    "Together, we can do this!",
    "We did it! The adventure is saved!",
    "And that was the funniest adventure ever!",
]

HI = [
    "एक नया रोमांच शुरू होता है!",
    "अरे! यह क्या मिला?",
    "यह रहस्यमयी चीज़ क्या हो सकती है?",
    "ओह! एक छोटी सी मुसीबत आ गई!",
    "चलो, कोई मज़ेदार उपाय सोचते हैं!",
    "अरे! यह तो उल्टा हो गया!",
    "चिंता मत करो, दोस्त मदद करेंगे!",
    "हम मिलकर यह कर सकते हैं!",
    "वाह! हमने समस्या हल कर दी!",
    "और यह सबसे मज़ेदार रोमांच था!",
]

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--topic", required=True)
    p.add_argument("--characters", required=True)
    p.add_argument("--duration", type=int, required=True)
    p.add_argument("--scene-seconds", type=int, default=5)
    p.add_argument("--language", choices=["English", "Hindi"], default="English")
    p.add_argument("--style", default="Cute high-quality 3D cartoon")
    p.add_argument("--output", default="output/story")
    args = p.parse_args()

    if not 30 <= args.duration <= 1800:
        raise SystemExit("Duration must be 30 to 1800 seconds.")
    if not 3 <= args.scene_seconds <= 8:
        raise SystemExit("Scene duration must be 3 to 8 seconds.")

    characters = [
        c.strip() for c in args.characters.split(",") if c.strip()
    ] or ["Cute original hero"]

    total = math.ceil(args.duration / args.scene_seconds)
    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)

    narration_lines = EN if args.language == "English" else HI
    scenes = []

    for i in range(total):
        start = i * args.scene_seconds
        end = min(args.duration, start + args.scene_seconds)
        beat_index = min(9, int(i / max(1, total) * 10))
        beat, beat_description = BEATS[beat_index]
        action = ACTIONS[i % len(ACTIONS)]
        character = characters[i % len(characters)]
        narration = narration_lines[i % len(narration_lines)]

        prompt = (
            f"{args.style}, cinematic animated scene. "
            f"Characters: {', '.join(characters)}. "
            f"Story: {args.topic}. "
            f"Scene {i+1} of {total}. Story beat: {beat}. "
            f"{beat_description} "
            f"Action: {character} {action}. "
            "Maintain identical character design, face, colors, "
            "proportions and outfit across every scene. "
            "Expressive emotions, smooth movement, detailed environment, "
            "beautiful lighting, coherent animation, no text, no watermark."
        )

        scenes.append({
            "scene": i + 1,
            "start_seconds": start,
            "end_seconds": end,
            "duration_seconds": end - start,
            "story_beat": beat,
            "characters": characters,
            "action": action,
            "visual_prompt": prompt,
            "narration": narration,
            "dialogue": [
                {
                    "character": character,
                    "line": narration
                }
            ]
        })

    project = {
        "project": "CuteVerse",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "topic": args.topic,
        "characters": characters,
        "duration_seconds": args.duration,
        "scene_count": total,
        "scene_seconds": args.scene_seconds,
        "language": args.language,
        "style": args.style,
        "scenes": scenes
    }

    (out / "story.json").write_text(
        json.dumps(project, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    (out / "narration.txt").write_text(
        "\n".join(s["narration"] for s in scenes),
        encoding="utf-8"
    )

    (out / "dialogue.txt").write_text(
        "\n".join(
            f"Scene {s['scene']}: "
            + " | ".join(
                f"{d['character']}: {d['line']}"
                for d in s["dialogue"]
            )
            for s in scenes
        ),
        encoding="utf-8"
    )

    (out / "video_prompts.txt").write_text(
        "\n\n".join(
            f"SCENE {s['scene']} "
            f"({s['start_seconds']}–{s['end_seconds']} sec)\n"
            f"{s['visual_prompt']}\n"
            f"NARRATION: {s['narration']}"
            for s in scenes
        ),
        encoding="utf-8"
    )

    print(f"Story created: {total} scenes")
    print(f"Duration: {args.duration} seconds")
    print(f"Files saved in: {out}")

if __name__ == "__main__":
    main()
    
