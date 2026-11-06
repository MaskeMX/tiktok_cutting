import sys, json
from faster_whisper import WhisperModel
m = WhisperModel("medium", device="cpu", compute_type="int8")
import numpy as np
audio = np.fromfile(sys.argv[1], dtype=np.int16).astype(np.float32)/32768
segs, _ = m.transcribe(audio, language="de", word_timestamps=True, vad_filter=False)
out=[]
for s in segs:
    out.append({"start":round(s.start,2),"end":round(s.end,2),"text":s.text.strip(),
                "words":[{"w":w.word.strip(),"s":round(w.start,2),"e":round(w.end,2)} for w in s.words]})
    print(f"{s.start:6.2f}-{s.end:6.2f} {s.text.strip()}")
json.dump(out, open(sys.argv[2],"w"), ensure_ascii=False, indent=1)
