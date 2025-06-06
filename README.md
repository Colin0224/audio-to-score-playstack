# 🎶 Audio-to-Score PlayStack

A Streamlit web application that transcribes audio from YouTube videos or uploaded files into musical scores and playable MIDI files using AI-powered music transcription.

## Features

- 📥 **YouTube Audio Download**: Extract audio from YouTube videos using yt-dlp
- 🎧 **AI Music Transcription**: Convert audio to MIDI using Spotify's Basic Pitch model
- 📄 **Score Generation**: Create PDF musical scores using LilyPond
- 🔊 **Audio Playback**: Generate and play instrumental versions using FluidSynth
- 🎤 **Simple Vocal Removal**: `instrumental_app.py` uses ffmpeg to create karaoke tracks
- 💾 **Multiple Download Options**: MIDI files, PDF scores, and WAV audio

## Demo

The app processes:
1. YouTube URL or uploaded audio file (MP3/WAV)
2. Downloads/processes the audio
3. Transcribes to MIDI using Basic Pitch AI
4. Generates a PDF musical score
5. Creates playable audio and downloads

## Prerequisites

### System Dependencies

**macOS:**
```bash
brew install lilypond fluidsynth
```

**Ubuntu/Debian:**
```bash
sudo apt-get install lilypond fluidsynth libsndfile1 ffmpeg
```

FFmpeg is only required for `instrumental_app.py`.
### Python Dependencies

```bash
pip install streamlit basic_pitch music21 pyfluidsynth yt-dlp scipy==1.11.4
```

### SoundFont

Download a General MIDI soundfont (e.g., `FluidR3_GM.sf2`) and place it in the project directory, or set the `SOUNDFONT_PATH` environment variable.

## Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/audio-to-score-playstack.git
   cd audio-to-score-playstack
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install streamlit basic_pitch music21 pyfluidsynth yt-dlp scipy==1.11.4
   ```

4. **Install system dependencies:**
   - **macOS:** `brew install lilypond fluidsynth`
   - **Linux:** `sudo apt-get install lilypond fluidsynth libsndfile1`

5. **Download a SoundFont file** (e.g., FluidR3_GM.sf2) and place it in the project directory

## Usage

1. **Start the application:**
   ```bash
   streamlit run app.py
   ```

2. **Open your browser** and navigate to `http://localhost:8501`

3. **Input audio:**
   - Paste a YouTube URL, OR
   - Upload an MP3/WAV file

4. **Click "Transcribe & Play"** and wait for processing

5. **Download results:**
   - PDF musical score
   - MIDI file
   - Instrumental WAV audio
6. **Or run the simpler vocal remover:**
   ```bash
   streamlit run instrumental_app.py
   ```




### Architecture

- **Frontend**: Streamlit web interface
- **Audio Processing**: yt-dlp for YouTube downloads
- **AI Transcription**: Spotify's Basic Pitch (CoreML backend)
- **Score Rendering**: music21 + LilyPond
- **Audio Synthesis**: FluidSynth + SoundFont

### Compatibility Issues Resolved

This implementation addresses several compatibility issues:
- **SciPy Version**: Uses SciPy 1.11.4 for compatibility with Basic Pitch
- **TensorFlow/CoreML**: Uses CoreML backend to avoid TensorFlow model loading issues
- **SSL Certificates**: YouTube download with certificate bypass options
- **Command-line Interface**: Uses Basic Pitch CLI instead of Python API for stability

## Troubleshooting

### Common Issues

| Problem | Solution |
|---------|----------|
| YouTube download fails | Try different video or update yt-dlp |
| Basic Pitch model error | Ensure SciPy 1.11.4 is installed |
| No audio playback | Check SoundFont file path |
| PDF generation fails | Install Ghostscript |

### Dependencies Not Working?

```bash
# Reinstall with specific versions
pip install "scipy==1.11.4" "basic-pitch[coreml]"

# For M1/M2 Macs, you might need:
brew install gfortran
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is open source and available under the [MIT License](LICENSE).

## Acknowledgments

- [Spotify's Basic Pitch](https://github.com/spotify/basic-pitch) for AI music transcription
- [music21](https://web.mit.edu/music21/) for music notation processing
- [LilyPond](https://lilypond.org/) for musical score engraving
- [FluidSynth](https://www.fluidsynth.org/) for MIDI synthesis
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) for YouTube audio extraction 