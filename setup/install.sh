#!/usr/bin/env bash
# Installiert alles für den Videoschnitt (Cloud-Container, nur CPU).
set -e
command -v ffmpeg >/dev/null || (apt-get update -qq && apt-get install -y -qq ffmpeg)
pip3 install -q --index-url https://download.pytorch.org/whl/cpu torch
pip3 install -q openai-whisper faster-whisper fonttools brotli
mkdir -p /usr/local/share/fonts/montserrat
for w in 700:Bold 800:ExtraBold 900:Black; do
  n=${w%%:*}; s=${w##*:}
  curl -sSfL -o /tmp/m.woff2 "https://cdn.jsdelivr.net/npm/@fontsource/montserrat@5.0.8/files/montserrat-latin-$n-normal.woff2"
  python3 -c "from fontTools.ttLib import TTFont; t=TTFont('/tmp/m.woff2'); t.flavor=None; t.save('/usr/local/share/fonts/montserrat/Montserrat-$s.ttf')"
done
fc-cache -f
echo "Setup fertig."
