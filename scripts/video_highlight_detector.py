#!/usr/bin/env python3
"""
Video Highlight Detector
Automatically finds exciting sections in video files based on audio peaks and scene changes.
"""

import subprocess
import json
import os
from dataclasses import dataclass
from typing import List, Tuple
import argparse


@dataclass
class Highlight:
    """Represents a detected highlight moment."""
    timestamp: float
    score: float
    duration: float = 10.0  # default clip duration
    source_file: str = ""


def run_ffmpeg_command(cmd: List[str]) -> str:
    """Run ffmpeg/ffprobe command and return output."""
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stderr + result.stdout


def analyze_audio_levels(video_path: str, threshold_db: float = -20.0) -> List[Tuple[float, float]]:
    """
    Analyze audio levels in video and return timestamps above threshold.
    Returns: List of (timestamp, db_level) tuples
    """
    temp_file = "/tmp/audio_levels.txt"

    cmd = [
        "ffmpeg", "-i", video_path,
        "-af", f"astats=metadata=1:reset=1,ametadata=print:key=lavfi.astats.Overall.RMS_level:file={temp_file}",
        "-f", "null", "-"
    ]

    subprocess.run(cmd, capture_output=True, text=True)

    # Parse the output file
    timestamps = []
    levels = []

    if os.path.exists(temp_file):
        with open(temp_file, 'r') as f:
            for line in f:
                if 'pts_time' in line:
                    ts = line.split('pts_time:')[1].strip()
                    timestamps.append(float(ts))
                elif 'RMS_level' in line:
                    db = float(line.split('=')[1].strip())
                    levels.append(db)

        os.remove(temp_file)

    # Pair up and filter
    results = []
    for ts, db in zip(timestamps, levels):
        if db > threshold_db:
            results.append((ts, db))

    return results


def detect_scene_changes(video_path: str) -> List[float]:
    """
    Detect scene changes using FFmpeg's scene detection.
    Returns list of timestamps where scene changes occur.
    """
    temp_file = "/tmp/scene_changes.txt"

    # Use mpdecate for scene detection
    cmd = [
        "ffmpeg", "-i", video_path,
        "-filter:v", "mpdecimate,showinfo",
        "-f", "null", "-"
    ]

    output = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

    # Parse scene changes from output
    scene_changes = []
    for line in output.stderr.split('\n'):
        if 'pts_time:' in line and 'Scene' in line:
            try:
                ts = line.split('pts_time:')[1].split()[0]
                scene_changes.append(float(ts))
            except (IndexError, ValueError):
                continue

    return scene_changes


def cluster_highlights(highlights: List[Tuple[float, float]], min_gap: float = 3.0) -> List[Highlight]:
    """
    Cluster nearby highlights into single segments.
    """
    if not highlights:
        return []

    # Sort by timestamp
    sorted_highlights = sorted(highlights, key=lambda x: x[0])

    clusters = []
    current_cluster = [sorted_highlights[0]]

    for ts, db in sorted_highlights[1:]:
        if ts - current_cluster[-1][0] < min_gap:
            current_cluster.append((ts, db))
        else:
            # Calculate average and max for this cluster
            avg_ts = sum(h[0] for h in current_cluster) / len(current_cluster)
            max_db = max(h[1] for h in current_cluster)
            score = max_db  # Use max dB as score
            clusters.append(Highlight(timestamp=avg_ts, score=score))
            current_cluster = [(ts, db)]

    # Add last cluster
    if current_cluster:
        avg_ts = sum(h[0] for h in current_cluster) / len(current_cluster)
        max_db = max(h[1] for h in current_cluster)
        clusters.append(Highlight(timestamp=avg_ts, score=max_db))

    return clusters


def generate_clip_commands(highlights: List[Highlight], output_dir: str = ".") -> List[str]:
    """Generate ffmpeg commands to extract highlight clips."""
    commands = []

    for i, hl in enumerate(highlights):
        start = max(0, hl.timestamp - 2)  # Start 2 seconds before
        duration = hl.duration

        output_file = os.path.join(output_dir, f"highlight_{i+1:02d}.mp4")

        cmd = (
            f"ffmpeg -y -i {hl.source_file} "
            f"-ss {start:.1f} -t {duration:.1f} "
            f"-c:v libx264 -c:a aac -preset fast "
            f"-movflags +faststart {output_file}"
        )

        commands.append((cmd, hl))

    return commands


def concat_highlights(clip_files: List[str], output_file: str) -> str:
    """Generate ffmpeg command to concatenate all highlight clips."""
    # Create concat file
    concat_file = "/tmp/concat_list.txt"
    with open(concat_file, 'w') as f:
        for clip in clip_files:
            f.write(f"file '{clip}'\n")

    cmd = (
        f"ffmpeg -y -f concat -safe 0 -i {concat_file} "
        f"-c:v libx264 -c:a aac -preset fast "
        f"-movflags +faststart {output_file}"
    )

    return cmd


def main():
    parser = argparse.ArgumentParser(description="Detect and extract video highlights")
    parser.add_argument("videos", nargs="+", help="Video files to analyze")
    parser.add_argument("-t", "--threshold", type=float, default=-20.0,
                        help="Audio threshold in dB (default: -20)")
    parser.add_argument("-o", "--output-dir", default="highlights",
                        help="Output directory for clips")
    parser.add_argument("-d", "--duration", type=float, default=10.0,
                        help="Duration of each highlight clip in seconds")
    parser.add_argument("--no-clip", action="store_true",
                        help="Only analyze, don't generate clips")
    parser.add_argument("--concat", action="store_true",
                        help="Concatenate all clips into single video")

    args = parser.parse_args()

    print(f"🎬 Video Highlight Detector")
    print(f"{'='*50}")

    # Create output directory
    if not args.no_clip:
        os.makedirs(args.output_dir, exist_ok=True)

    all_highlights = []

    for video_path in args.videos:
        if not os.path.exists(video_path):
            print(f"❌ File not found: {video_path}")
            continue

        print(f"\n📹 Analyzing: {os.path.basename(video_path)}")

        # Analyze audio levels
        print(f"   🔊 Detecting audio peaks (threshold: {args.threshold} dB)...")
        audio_peaks = analyze_audio_levels(video_path, args.threshold)

        print(f"   Found {len(audio_peaks)} loud moments above threshold")

        # Cluster into highlights
        highlights = cluster_highlights(audio_peaks, min_gap=3.0)

        # Set duration and source
        for hl in highlights:
            hl.duration = args.duration
            hl.source_file = video_path

        all_highlights.extend(highlights)

        # Sort by score
        all_highlights.sort(key=lambda h: h.score, reverse=True)

    # Print results
    print(f"\n{'='*50}")
    print(f"📊 DETECTED HIGHLIGHTS (sorted by score)")
    print(f"{'='*50}")

    for i, hl in enumerate(all_highlights[:20], 1):
        source = os.path.basename(hl.source_file)
        print(f"  {i:2d}. [{source}] {hl.timestamp:6.1f}s | Score: {hl.score:+.1f} dB")

    # Generate clip commands
    if not args.no_clip:
        print(f"\n🎬 Generating clip commands...")

        clip_commands = generate_clip_commands(all_highlights[:10], args.output_dir)

        print(f"\n{'='*50}")
        print(f"📝 FFmpeg Commands (top 10 highlights)")
        print(f"{'='*50}")

        for cmd, hl in clip_commands:
            print(f"\n# {os.path.basename(hl.source_file)} @ {hl.timestamp:.1f}s")
            print(cmd)

        # Optionally concatenate
        if args.concat and clip_commands:
            output_video = os.path.join(args.output_dir, "highlights_reel.mp4")
            concat_cmd = concat_highlights(
                [f"{args.output_dir}/highlight_{i+1:02d}.mp4" for i in range(len(clip_commands))],
                output_video
            )
            print(f"\n{'='*50}")
            print(f"🔗 Concatenation Command")
            print(f"{'='*50}")
            print(concat_cmd)

    print(f"\n✅ Analysis complete!")


if __name__ == "__main__":
    main()