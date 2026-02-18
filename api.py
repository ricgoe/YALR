import backend.patches #NEEDED: Custom patches for AV-HuBERT and fairseq

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from backend.prep import Preprocessor
from backend.pred import LipPredictor
from pathlib import Path
from hashlib import sha256
import subprocess



app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], #TODO ENV
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
model_path = Path("data/misc/self_large_vox_433h.pt")
if not model_path.exists():
    print("By using this Model, you agree to the terms of this License https://raw.githubusercontent.com/facebookresearch/av_hubert/refs/heads/main/LICENSE")
    input("Press Enter to agree>> ")
    result = subprocess.run(["curl","-L","-o",str(model_path),
        "https://dl.fbaipublicfiles.com/avhubert/model/lrs3_vox/vsr/self_large_vox_433h.pt"
    ], check=True)
    if result.returncode != 0 or not model_path.exists():
        print(f"Failed to download model. Navigate to https://facebookresearch.github.io/av_hubert/ and download 'AV-HuBERT Large + Self-Training LRS3 + VoxCeleb2 (En) LRS3-433h'.\nPlace at {str(model_path)}")
        exit()

# class LipReading(BaseModel):
#     lipreading: str
@app.exception_handler(Exception)
async def all_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "error": exc.__class__.__name__,
            "message": str(exc),
        },
    )

@app.post("/upload-video")
async def upload_video(request: Request):
    data = await request.body()
    base = Path("data")
    video = sha256(data).hexdigest()
    print(video)
    input = (base/video).with_suffix(".webm").resolve()
    preps = base/"preprocessed"
    preps.mkdir(exist_ok=True, parents=True)
    output = (preps/video).with_suffix(".mp4").resolve()
    with input.open("wb") as f:
        f.write(data)
    #TODO PREDICT
    # prep = Preprocessor(mean_face_path="data/misc/20words_mean_face.npy")
    prep = Preprocessor()
    if not output.exists(): #Remove for production?
        crops = prep.process_video(str(input), str(output))
    pred=LipPredictor(str(model_path))
    hypo=pred.predict([str(output)], "av_hubert/avhubert")
    return {"message": hypo}
    # return { "message": "Deine Fette Mutter"}


# @app.post("/submit-lipreading")
# async def send_lipreading(lr: LipReading):
#     return {"message": f"Submitted LR: {lr.text}"}
