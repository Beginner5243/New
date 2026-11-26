
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from datetime import datetime, timezone

ACTIONS = [
    "introduces the adventure and looks around curiously",
    "discovers a mysterious object nearby",
    "hears a strange sound and reacts with surprise",
    "approaches the new discovery carefully",
    "tries a funny solution to the problem",
    "meets a new friend who offers help",
    "the friends work together on a clever idea",
    "something unexpected changes their plan",
    "they overcome the obstacle through teamwork",
    "celebrate their success and end with a funny moment",
]

EN_LINES = [
    "Today, a new adventure begins.",
    "Something unusual catches our hero's attention.",
    "What could that strange sound be?",
    "Let's take a closer look.",
    "That was not the plan, but it is funny!",
    "A new friend arrives to help.",
    "Together, they come up with an idea.",
    "Wait! Something unexpected happens.",
    "Teamwork saves the day.",
    "And that is how this adventure ends—with a smile.",
]

HI_LINES = [
    "आज एक नया रोमांच शुरू होता है।",
    "हमारे हीरो को कुछ अनोखा दिखाई देता है।",
    "यह अजीब आवाज़ कहाँ से आई?",
    "चलो, पास जाकर देखते हैं।",
    "अरे! यह तो योजना में नहीं था, लेकिन मज़ेदार है!",
    "मदद करने के लिए एक नया दोस्त आता है।",
    "दोनों मिलकर एक नया उपाय सोचते हैं।",
    "रुको! कुछ अनपेक्षित हो गया!",
    "मिलकर काम करने से समस्या हल हो जाती है।",
    "और यह रोमांच मुस्कान के साथ समाप्त होता है।",
]

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--duration", type=int, required=True)
    p.add_argument("--scene-seconds", type=int, default=5)
    p.add_argument("--aspect", choices=["vertical", "horizontal", "square"], default="vertical")
    p.add_argument("--language", choices=["English", "Hindi"], default="English")
    p.add_argument("--mode", choices=["full_motion", "hybrid", "story_mode"], default="hybrid")
    p.add_argument("--characters", default="Yeti")
    p.add_argument("--topic", default="A funny friendship adventure")
    p.add_argument("--style", default="Cute high-quality 3D cartoon")
    p.add_argument("--output", default="output")
    args = p.parse_args()

    if not 30 <= args.duration <= 1800:
        raise SystemExit("Duration must be between 30 and 1800 seconds.")
    if not 3 <= args.scene_seconds <= 8:
        raise SystemExit("Scene duration must be 3 to 8 seconds.")

    count = math.ceil(args.duration / args.scene_seconds)
    characters = [x.strip() for x in args.characters.split(",") if x.strip()]
    if not characters:
        characters = ["Original cartoon character"]

    lines = HI_LINES if args.language == "Hindi" else EN_LINES
    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)

    scenes = []
    for i in range(count):
        start = i * args.scene_seconds
        end = min(args.duration, start + args.scene_seconds)
        action = ACTIONS[i % len(ACTIONS)]
        narration = lines[i % len(lines)]
        cast = characters[i % len(characters)]

        prompt = (
            f"{args.style}. Characters: {', '.join(characters)}. "
            f"Topic: {args.topic}. Scene {i+1}/{count}: {cast} {action}. "
            "Keep character appearance, face, colors and proportions consistent. "
            "Clear readable action, cinematic composition, no text, no watermark."
        )

        scenes.append({
            "scene": i + 1,
            "start_seconds": start,
            "end_seconds": end,
            "duration_seconds": end - start,
            "characters": characters,
            "action": action,
            "visual_prompt": prompt,
            "narration": narration,
            "mode": args.mode
        })

    plan = {
        "project": "CuteVerse",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "requested_duration_seconds": args.duration,
        "planned_duration_seconds": args.duration,
        "scene_seconds_target": args.scene_seconds,
        "scene_count": count,
        "aspect_ratio": args.aspect,
        "language": args.language,
        "production_mode": args.mode,
        "characters": characters,
        "topic": args.topic,
        "style": args.style,
        "scenes": scenes
    }

    (out / "scene_plan.json").write_text(
        json.dumps(plan, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )
    (out / "narration.txt").write_text(
        "\n".join(s["narration"] for s in scenes),
        encoding="utf-8"
    )
    (out / "scene_prompts.txt").write_text(
        "\n\n".join(
            f"SCENE {s['scene']} ({s['start_seconds']}–{s['end_seconds']} sec)\n"
            f"{s['visual_prompt']}\nNARRATION: {s['narration']}"
            for s in scenes
        ),
        encoding="utf-8"
    )

    print(f"Planned {count} scenes for {args.duration} seconds.")
    print(f"Output files saved in: {out}")

if __name__ == "__main__":
    main()
  
