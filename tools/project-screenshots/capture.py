"""Render reproducible terminal captures from actual demo and test output."""
from __future__ import annotations

import json
import shlex
import subprocess
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
SCALE = 2
WIDTH = 1320
BACKGROUND = "#080f1c"
SURFACE = "#111c2d"
TEXT = "#e4edf9"
MUTED = "#97aac4"
ACCENT = "#79c6f7"
SUCCESS = "#86dfb1"
WARNING = "#f3cf8b"
PROJECTS = (
    ("secure-transfer-engine", "Secure Transfer Engine", "Java 17 · durable transfers and owner authorization",
     ["bash", "run.sh", "demo"], ["bash", "run.sh", "test"]),
    ("webhook-security-gateway", "Webhook Security Gateway", "Python · signed admission and transactional delivery",
     ["python3", "demo.py"], ["python3", "-m", "unittest", "discover", "-s", "tests", "-q"]),
    ("restore-drill", "Restore Drill", "Python · authenticated snapshots and recovery verification",
     ["python3", "demo.py"], ["python3", "-m", "unittest", "discover", "-s", "tests", "-q"]),
)


def font(size, *, mono=False, bold=False):
    family = "DejaVuSansMono" if mono else "DejaVuSans"
    suffix = "-Bold" if bold else ""
    return ImageFont.truetype(f"{family}{suffix}.ttf", size * SCALE)


def run(command, directory):
    result = subprocess.run(command, cwd=directory, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT, text=True, check=True, timeout=60)
    return result.stdout.rstrip()


def wrapped(output):
    lines = []
    for line in output.splitlines():
        lines.extend(textwrap.wrap(line, width=90, replace_whitespace=False,
                                   drop_whitespace=False, break_on_hyphens=False) or [""])
    return lines


def output_color(line):
    if line.startswith("PASS "):
        return SUCCESS
    if "rejected" in line.lower() or line.endswith("False"):
        return WARNING
    if line.startswith("PASS ") or line == "OK" or "passed" in line or line == "accepted" or line.endswith("True"):
        return SUCCESS
    return TEXT


def capture(slug, title, subtitle, demo_command, test_command):
    directory = ROOT / "PROJECTS" / "advanced" / slug
    demo_output = run(demo_command, directory)
    test_output = run(test_command, directory)
    demo_lines, test_lines = wrapped(demo_output), wrapped(test_output)
    line_height = 29
    height = 430 + line_height * (len(demo_lines) + len(test_lines))
    image = Image.new("RGB", (WIDTH * SCALE, height * SCALE), BACKGROUND)
    draw = ImageDraw.Draw(image)

    def text(x, y, value, size=21, color=TEXT, mono=False, bold=False):
        draw.text((x * SCALE, y * SCALE), value, font=font(size, mono=mono, bold=bold), fill=color)

    def rule(y):
        draw.line((64 * SCALE, y * SCALE, (WIDTH - 64) * SCALE, y * SCALE), fill="#24344a", width=SCALE)

    draw.rounded_rectangle((32 * SCALE, 32 * SCALE, (WIDTH - 32) * SCALE, (height - 32) * SCALE),
                           radius=18 * SCALE, fill=SURFACE)
    text(64, 58, "CLI EXECUTION", size=15, color=ACCENT, bold=True)
    text(64, 89, title, size=34, bold=True)
    text(64, 139, subtitle, size=19, color=MUTED)
    rule(184)
    y = 209
    text(64, y, "$ " + shlex.join(demo_command), color=ACCENT, mono=True)
    y += 43
    for line in demo_lines:
        text(64, y, line, color=output_color(line), mono=True)
        y += line_height
    y += 17
    rule(y)
    y += 25
    text(64, y, "$ " + shlex.join(test_command), color=ACCENT, mono=True)
    y += 43
    for line in test_lines:
        text(64, y, line, color=output_color(line), mono=True)
        y += line_height

    output = directory / "docs" / "assets"
    output.mkdir(parents=True, exist_ok=True)
    temporary_image = output / "execution.png.tmp"
    image.save(temporary_image, format="PNG", optimize=True)
    temporary_image.replace(output / "execution.png")
    transcript = {"demo": {"command": demo_command, "output": demo_output, "exit_code": 0},
                  "tests": {"command": test_command, "output": test_output, "exit_code": 0}}
    (output / "execution.json").write_text(json.dumps(transcript, indent=2) + "\n")
    print(f"{slug}: {image.width}x{image.height}, {(output / 'execution.png').stat().st_size} bytes")


if __name__ == "__main__":
    for project in PROJECTS:
        capture(*project)
