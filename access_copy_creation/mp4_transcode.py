#!/usr/bin/env python3

"""
mp4_transcode.py

Script to manage MP4 transcoding jobs for access copy creation.
Monitors a designated folder for new files and launches FFmpeg transcoding
jobs to produce H.264/AAC MP4 access copies.

Usage:
    python mp4_transcode.py <watch_folder> <output_folder>

Dependencies:
    - FFmpeg must be installed and available on PATH
    - Python 3.6+
"""

import os
import sys
import logging
import subprocess
import argparse
from pathlib import Path
from datetime import datetime

# Configure logging
LOG_DIR = os.environ.get("LOG_DIR", "/var/log/bfi_scripts")
LOG_FILE = os.path.join(LOG_DIR, "mp4_transcode.log")

os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)

# Supported input file extensions
SUPPORTED_EXTENSIONS = {".mxf", ".mov", ".avi", ".mkv", ".mp4", ".dv", ".ts"}

# FFmpeg transcoding parameters for access copies
FFMPEG_CMD = [
    "ffmpeg",
    "-hide_banner",
    "-loglevel", "error",
    "-i", "{input}",
    "-c:v", "libx264",
    "-crf", "23",
    "-preset", "medium",
    "-pix_fmt", "yuv420p",
    "-c:a", "aac",
    "-b:a", "192k",
    "-movflags", "+faststart",
    "{output}",
]


def get_output_path(input_path: Path, output_folder: Path) -> Path:
    """Generate output MP4 path based on input filename."""
    stem = input_path.stem
    return output_folder / f"{stem}_access.mp4"


def transcode_file(input_path: Path, output_path: Path) -> bool:
    """
    Run FFmpeg transcoding on a single file.

    Args:
        input_path: Path to the source media file.
        output_path: Path for the output MP4 file.

    Returns:
        True if transcoding succeeded, False otherwise.
    """
    cmd = [
        part.replace("{input}", str(input_path)).replace("{output}", str(output_path))
        for part in FFMPEG_CMD
    ]

    logger.info("Starting transcode: %s -> %s", input_path.name, output_path.name)

    try:
        result = subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True,
        )
        logger.info("Transcode complete: %s", output_path.name)
        if result.stderr:
            logger.warning("FFmpeg warnings for %s: %s", input_path.name, result.stderr)
        return True
    except subprocess.CalledProcessError as err:
        logger.error(
            "Transcode failed for %s: %s", input_path.name, err.stderr
        )
        # Remove partial output if it exists
        if output_path.exists():
            output_path.unlink()
        return False


def process_folder(watch_folder: Path, output_folder: Path) -> None:
    """
    Scan watch_folder for supported media files and transcode each.

    Args:
        watch_folder: Directory to scan for input files.
        output_folder: Directory to write transcoded MP4 files.
    """
    output_folder.mkdir(parents=True, exist_ok=True)

    files = [
        f for f in watch_folder.iterdir()
        if f.is_file() and f.suffix.lower() in SUPPORTED_EXTENSIONS
    ]

    if not files:
        logger.info("No supported files found in %s", watch_folder)
        return

    logger.info("Found %d file(s) to process in %s", len(files), watch_folder)

    success_count = 0
    fail_count = 0

    for input_file in sorted(files):
        output_file = get_output_path(input_file, output_folder)

        if output_file.exists():
            logger.info("Skipping %s — output already exists", input_file.name)
            continue

        if transcode_file(input_file, output_file):
            success_count += 1
        else:
            fail_count += 1

    logger.info(
        "Processing complete. Success: %d, Failed: %d",
        success_count,
        fail_count,
    )


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Transcode media files to H.264 MP4 access copies."
    )
    parser.add_argument(
        "watch_folder",
        help="Folder containing source media files to transcode.",
    )
    parser.add_argument(
        "output_folder",
        help="Destination folder for transcoded MP4 access copies.",
    )
    return parser.parse_args()


def main() -> None:
    """Main entry point."""
    args = parse_args()

    watch_folder = Path(args.watch_folder)
    output_folder = Path(args.output_folder)

    if not watch_folder.is_dir():
        logger.error("Watch folder does not exist or is not a directory: %s", watch_folder)
        sys.exit(1)

    logger.info(
        "mp4_transcode.py started at %s",
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    )
    logger.info("Watch folder: %s", watch_folder)
    logger.info("Output folder: %s", output_folder)

    process_folder(watch_folder, output_folder)


if __name__ == "__main__":
    main()
