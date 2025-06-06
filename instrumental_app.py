import subprocess
import tempfile
from pathlib import Path

import streamlit as st

# Simple YouTube downloader using yt-dlp

def download_youtube_audio(url: str, out_dir: Path) -> Path:
    output = out_dir / "audio.%(ext)s"
    cmd = [
        "yt-dlp",
        "-x",
        "--audio-format",
        "wav",
        url,
        "-o",
        str(output),
    ]
    subprocess.run(cmd, check=True)
    return out_dir / "audio.wav"


def remove_vocals(input_path: Path, output_path: Path) -> None:
    """Remove center vocals using simple channel subtraction."""
    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        str(input_path),
        "-af",
        "pan=stereo|c0=c0-c1|c1=c1-c0",
        str(output_path),
    ]
    subprocess.run(cmd, check=True)


st.title("YouTube Vocal Remover")
url = st.text_input("YouTube URL")
start = st.button("Create Instrumental")

if start and url:
    with st.spinner("Processing…"):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_dir = Path(tmp)
            wav_path = download_youtube_audio(url, tmp_dir)
            instr_path = tmp_dir / "instrumental.wav"
            remove_vocals(wav_path, instr_path)
            audio_bytes = instr_path.read_bytes()
            st.audio(audio_bytes, format="audio/wav")
            st.download_button("Download Instrumental", audio_bytes, "instrumental.wav")

