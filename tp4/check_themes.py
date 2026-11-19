"""Checks that every theme has its own player, monsters, bullets, background and sounds.

Run from the project folder:   python3 check_themes.py
A missing file is not a crash: the game draws the old shape for it. But a theme
should have its own complete set, so this tells you what is still missing."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import settings as cfg

ROOT = os.path.join(HERE, cfg.ASSETS_DIR)
REQUIRED = {
    "player": ["player.png"],
    "monsters": [n + ".png" for n in ("normal", "fast", "flying", "strong", "immobile")],
    "bullets": [n + ".png" for n in ("bullet", "fire", "laser", "enemy_shot")],
    "backgrounds": ["background.png"],
    "sounds": ["shoot.wav", "game_over.wav"],
}


def missing_files(theme):
    return [os.path.join(folder, name)
            for folder, names in REQUIRED.items() for name in names
            if not os.path.exists(os.path.join(ROOT, theme, folder, name))]


def main():
    if not os.path.isdir(ROOT):
        print("No themes folder found:", ROOT)
        return 1
    themes = sorted(d for d in os.listdir(ROOT) if os.path.isdir(os.path.join(ROOT, d)))
    problems = 0
    for theme in themes:
        missing = missing_files(theme)
        if missing:
            problems += 1
            print("%-12s MISSING %d file(s)" % (theme, len(missing)))
            for path in missing:
                print("               -", path)
        else:
            print("%-12s complete (player, monsters, bullets, background, sounds)" % theme)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
