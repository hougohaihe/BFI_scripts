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
# Using crf=20 instead of 23 for slightly better quality on archival material
# Note: bumped preset from 'medium' to 'slow' for better compression efficiency
# at the cost of longer encode times -- worth it for archival sources (personal pref)
FFMPEG_CMD = [
    "ffmpeg",
    "-hide_banner",
    "-loglevel", "error",
    "-i", "{input}",
    "-c:v", "libx264",
    "-crf", "20",
    "-preset", "slow",
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
        watch_folder: Di
