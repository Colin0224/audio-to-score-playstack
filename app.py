# app.py – "Audio‑to‑Score PlayStack"
# -------------------------------------------------------------
# A tiny Streamlit app that accepts a YouTube link **or** an audio
# file (MP3/WAV), runs automatic music‑transcription with Spotify's
# Basic Pitch, prints an optional PDF score, and plays the result.
# -------------------------------------------------------------
# ⚙️  Prerequisites (Linux / macOS / Windows WSL)
#   pip install streamlit basic-pitch music21 pyfluidsynth yt-dlp
#   brew / apt: lilypond fluidsynth
#   Download a GM sound‑font, e.g. FluidR3_GM.sf2, and put it next to
#   this script or set SOUNDFONT_PATH env var.
# -------------------------------------------------------------
#   Run:  streamlit run app.py
# -------------------------------------------------------------

import os, subprocess, tempfile, uuid, shutil, mimetypes, base64, io
from pathlib import Path

import streamlit as st
from music21 import converter

# ---------------------------------------------
# Helper functions
# ---------------------------------------------

HERE = Path(__file__).parent
SOUNDFONT = Path(os.getenv("SOUNDFONT_PATH", HERE / "FluidR3_GM.sf2"))


def download_youtube(url: str, out_dir: Path) -> Path:
    """Download YouTube audio as WAV using yt‑dlp."""
    wav_path = out_dir / "audio.wav"
    cmd = [
        "yt-dlp",
        "--verbose",  # Added for detailed error logs
        "--legacy-server-connect",  # Fix for SSL handshake issues
        "--no-check-certificates",  # Skip SSL certificate verification
        "--prefer-insecure",  # Use HTTP instead of HTTPS when possible
        "-x",
        "--audio-format",
        "wav",
        url,
        "-o",
        str(wav_path),
    ]
    process = subprocess.run(cmd, check=False, capture_output=True, text=True)
    if process.returncode != 0:
        # Raise an error that includes stdout and stderr
        raise subprocess.CalledProcessError(
            process.returncode, process.args, output=process.stdout, stderr=process.stderr
        )
    return wav_path


def transcribe_audio_to_midi(audio_path: Path, out_dir: Path) -> Path:
    """Run Basic Pitch → MIDI file using command line tool or Python API."""
    midi_path = out_dir / "transcription.mid"
    
    # Try command line tool first (more reliable)
    try:
        cmd = [
            "basic-pitch",
            str(out_dir),
            str(audio_path)
        ]
        
        st.write("Running basic-pitch command line tool...")
        
        # List files before running
        files_before = list(out_dir.glob("*"))
        
        process = subprocess.run(cmd, check=False, capture_output=True, text=True)
        
        if process.returncode != 0:
            st.warning(f"Command line tool failed: {process.stderr}")
            raise subprocess.CalledProcessError(process.returncode, cmd, process.stdout, process.stderr)
        
        # Look for generated MIDI files with different possible naming patterns
        possible_names = [
            audio_path.stem + "_basic_pitch.mid",
            audio_path.stem + ".mid",
            "audio_basic_pitch.mid",
            "audio.mid"
        ]
        
        for name in possible_names:
            candidate = out_dir / name
            if candidate.exists():
                if candidate != midi_path:
                    candidate.rename(midi_path)
                st.success(f"Found MIDI file: {name}")
                return midi_path
        
        # If not found by name, look for any new MIDI files
        files_after = list(out_dir.glob("*.mid")) + list(out_dir.glob("*.midi"))
        new_files = [f for f in files_after if f not in files_before]
        
        if new_files:
            source_midi = new_files[0]
            if source_midi != midi_path:
                source_midi.rename(midi_path)
            st.success(f"Found MIDI file: {source_midi.name}")
            return midi_path
            
    except Exception as e:
        st.warning(f"Command line approach failed: {e}")
        
    # Fallback: Try Python API
    try:
        st.write("Trying Python API approach...")
        from basic_pitch.inference import predict
        
        # Use the Python API without specifying model path (uses default)
        model_output, midi_data, note_events = predict(
            str(audio_path),
            onset_threshold=0.5,
            frame_threshold=0.3,
            minimum_note_length=127.70,  # in milliseconds
            minimum_frequency=32.7,       # Hz (C1)
            maximum_frequency=2093.0,     # Hz (C7)
            multiple_pitch_bends=False,   # Correct parameter name
            melodia_trick=True
        )
        
        # Save the MIDI data
        midi_data.write(str(midi_path))
        st.success("MIDI generated via Python API!")
        return midi_path
        
    except Exception as e:
        st.error(f"Python API also failed: {e}")
        raise FileNotFoundError("Could not generate MIDI file using either method")


def midi_to_score_pdf(midi_path: Path, out_dir: Path) -> Path | None:
    """Create a nicely engraved PDF score using music21 + LilyPond.
    Returns None if LilyPond not found."""
    try:
        score = converter.parse(midi_path)
        pdf_path = out_dir / "score.pdf"
        score.write("lily.pdf", fp=pdf_path)
        return pdf_path
    except Exception as e:
        st.warning(f"Could not generate PDF score: {e}")
        return None


def render_midi_to_wav(midi_path: Path, out_dir: Path) -> Path | None:
    if not SOUNDFONT.exists():
        st.warning(f"Sound‑font not found at {SOUNDFONT}. Skipping audio rendering.")
        st.info("Download a soundfont like FluidR3_GM.sf2 and place it in the app directory.")
        return None
    wav_path = out_dir / "render.wav"
    cmd = [
        "fluidsynth",
        "-ni",
        str(SOUNDFONT),
        str(midi_path),
        "-F",
        str(wav_path),
        "-r",
        "44100",
    ]
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        return wav_path
    except subprocess.CalledProcessError as e:
        st.warning(f"FluidSynth rendering failed: {e.stderr}")
        return None
    except FileNotFoundError:
        st.warning("FluidSynth not found. Please install it with: brew install fluidsynth")
        return None


# ---------------------------------------------
# Streamlit UI
# ---------------------------------------------

st.set_page_config(page_title="Audio‑to‑Score PlayStack", page_icon="🎶")
st.title("🎶 Audio‑to‑Score PlayStack")
st.caption("From YouTube link or MP3 ➜ MIDI ➜ Score PDF ➜ Playback")

url = st.text_input("YouTube URL (leave blank to upload your own file)")
file = st.file_uploader("…or upload MP3 / WAV", type=["mp3", "wav"])

auto_start = st.button("Transcribe & Play")

if auto_start:
    with st.spinner("Working… this can take up to a minute for long tracks"):
        with tempfile.TemporaryDirectory() as tmp_dir_str:
            tmp_dir = Path(tmp_dir_str)

            # 1) Acquire audio
            if url:
                st.write("📥 Downloading YouTube audio…")
                try:
                    audio_path = download_youtube(url, tmp_dir)
                except subprocess.CalledProcessError as e:
                    error_message = f"yt-dlp failed (exit code {e.returncode}). Is the link valid and yt-dlp installed?\n"
                    # Ensure e.output (stdout) and e.stderr are strings and not None
                    stdout_info = e.output if e.output is not None else ""
                    stderr_info = e.stderr if e.stderr is not None else ""
                    if stdout_info.strip(): # Only add if there's actual content
                        error_message += f"\n--- yt-dlp STDOUT ---\n{stdout_info.strip()}"
                    if stderr_info.strip(): # Only add if there's actual content
                        error_message += f"\n--- yt-dlp STDERR ---\n{stderr_info.strip()}"
                    st.error(error_message)
                    st.stop()
            elif file is not None:
                st.write("📥 Saving uploaded file…")
                suffix = Path(file.name).suffix or ".wav"
                audio_path = tmp_dir / f"upload{suffix}"
                audio_path.write_bytes(file.read())
            else:
                st.error("Please provide a YouTube URL or upload a file.")
                st.stop()

            # 2) Transcription
            st.write("🎧 Transcribing audio → MIDI (Basic Pitch)…")
            try:
                midi_path = transcribe_audio_to_midi(audio_path, tmp_dir)
                st.success("✅ MIDI ready!")
            except Exception as e:
                st.error(f"Transcription failed: {e}")
                st.stop()

            # 3) Score PDF
            st.write("📄 Engraving score… (needs LilyPond)")
            pdf_path = midi_to_score_pdf(midi_path, tmp_dir)
            if pdf_path and pdf_path.exists():
                with open(pdf_path, "rb") as f:
                    st.download_button("📥 Download score (PDF)", f.read(), "score.pdf", mime="application/pdf")

            # 4) Render WAV for browser playback
            st.write("🔊 Rendering audio… (FluidSynth)")
            wav_path = render_midi_to_wav(midi_path, tmp_dir)
            if wav_path and wav_path.exists():
                wav_bytes = wav_path.read_bytes()
                st.audio(wav_bytes, format="audio/wav")
                st.download_button("📥 Download instrumental (WAV)", wav_bytes, "instrumental.wav", mime="audio/wav")
            else:
                st.info("Audio rendering skipped. You can still download the MIDI file below.")

            # 5) Always offer MIDI
            if midi_path.exists():
                with open(midi_path, "rb") as f:
                    st.download_button("📥 Download MIDI", f.read(), "instrumental.mid", mime="audio/midi")

st.sidebar.title("ℹ️  Help")
st.sidebar.markdown(
    """
    **Setup tips**
    1. Install Python dependencies:
       ```
       pip install streamlit basic-pitch music21 pyfluidsynth yt-dlp
       ```
    2. Install system dependencies:
       - macOS: `brew install lilypond fluidsynth`
       - Linux: `apt install lilypond fluidsynth`
    3. Download a soundfont (e.g., [FluidR3_GM.sf2](https://github.com/urish/cinto/blob/master/media/FluidR3%20GM.sf2)) 
       and place it in the same directory as app.py
    
    **Note:** The warnings about scikit-learn and TensorFlow versions are normal and can be ignored.
    
    *If LilyPond / FluidSynth aren't present, the app will still give you a MIDI file.*
    """
)