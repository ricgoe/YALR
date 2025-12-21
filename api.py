from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from backend.prep import Preprocessor
from backend.pred import LipPredictor
from av_hubert.avhubert.preparation.align_mouth import write_video_ffmpeg
from pathlib import Path
from uuid import uuid4 as uuid
from io import BytesIO
from hashlib import sha256


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
    video = sha256(data).hexdigest()
    input = (base/video).with_suffix(".webm").resolve()
    output = (base/"preprocessed"/video).with_suffix(".mp4").resolve()
    with input.open("wb") as f:
        f.write(data)
    #TODO PREDICT
    prep = Preprocessor(
        mean_face_path="data/misc/20words_mean_face.npy"
    )
    if not output.exists(): #Remove for production?
        crops = prep.get_mouth_crops(str(input))
        write_video_ffmpeg(crops, str(output), "/home/richard/.local/bin/ffmpeg")
    pred=LipPredictor("data/misc/large_vox_433h.pt")
    hypo=pred.predict(str(output), "av_hubert/avhubert")
    return {"message": hypo}


# @app.post("/submit-lipreading")
# async def send_lipreading(lr: LipReading):
#     return {"message": f"Submitted LR: {lr.text}"}
