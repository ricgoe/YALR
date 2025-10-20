from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pred import LipPredictor
from prep import Preprocessor
from av_hubert.avhubert.preparation.align_mouth import write_video_ffmpeg
from pathlib import Path
from uuid import uuid4 as uuid
from io import BytesIO


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], #TODO ENV
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# class LipReading(BaseModel):
#     lipreading: str

@app.post("/upload-video")
async def upload_video(request: Request):
    data = await request.body()
    base = Path("data")
    video = Path("jannis-test-4.mp4")
    output = base / "preprocessed" / video
    with open("uploaded_video.mp4", "wb") as f:
        f.write(data)
    #TODO PREDICT
    prep = Preprocessor(
        predictor_path="data/misc/shape_predictor_68_face_landmarks.dat", 
        mean_face_path="data/misc/20words_mean_face.npy"
    )
    if not output.exists():
        crops = prep.get_mouth_crops(str(base / video))
        write_video_ffmpeg(crops, output, "/home/richard/.local/bin/ffmpeg")
    pred=LipPredictor("data/misc/large_vox_433h.pt")
    hypo=pred.predict(str(output.resolve()), "av_hubert/avhubert")
    return {"message": hypo}


# @app.post("/submit-lipreading")
# async def send_lipreading(lr: LipReading):
#     return {"message": f"Submitted LR: {lr.text}"}
    