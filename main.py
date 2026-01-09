from backend.prep2 import Preprocessor
from backend.pred import LipPredictor
from av_hubert.avhubert.preparation.align_mouth import write_video_ffmpeg
from pathlib import Path
from uuid import uuid4 as uuid
from io import BytesIO
from hashlib import sha256


def our_sentences(base: Path):
    preps = base/"preprocessed"
    preps.mkdir(exist_ok=True, parents=True)
    hypos = []
    for f in base.rglob("*"):
        if f.is_dir() or f.suffix in [".csv", ".txt"]: continue
        output = (preps/f.stem).with_suffix(".mp4").resolve()
        prep = Preprocessor()
        print(output)
        if not output.exists(): #Remove for production?
            crops = prep.process_video(str(f), str(output))
            pred=LipPredictor("data/misc/self_large_vox_433h.pt")
            hypo=pred.predict([str(output)], "av_hubert/avhubert")
            with (base/"hypos.txt").open("at") as hyp:
                hyp.write(f'{f.stem},"{hypo}"\n')


if __name__ == "__main__":
    our_sentences(Path("sentences-good"))