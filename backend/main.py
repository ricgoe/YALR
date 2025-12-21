from backend.pred import LipPredictor
from backend.prep import Preprocessor
from av_hubert.avhubert.preparation.align_mouth import write_video_ffmpeg
from pathlib import Path


if __name__ == "__main__":
    prep = Preprocessor(
        predictor_path="data/misc/shape_predictor_68_face_landmarks.dat",
        mean_face_path="data/misc/20words_mean_face.npy"
    )
    base = Path("data")
    video = Path("jannis-test-4.mp4")
    output = base / "preprocessed" / video
    if not output.exists():
        crops = prep.get_mouth_crops(str(base / video))
        write_video_ffmpeg(crops, output, "/home/richard/.local/bin/ffmpeg")
    pred=LipPredictor("data/misc/large_vox_433h.pt")
    hypo=pred.predict(str(output.resolve()), "av_hubert/avhubert")
    with (base / "subtitles" / video).with_suffix(".txt").open("wt") as f:
        f.write(hypo)
