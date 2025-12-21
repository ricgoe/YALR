from contextlib import suppress

import skvideo.io
from backend.prep2 import Preprocessor
from backend.pred import LipPredictor
# from av_hubert.avhubert.preparation.align_mouth import write_video_ffmpeg


if __name__ == "__main__":
    # pre = Preprocessor()
    # pred =
    # crops = pre.process_video("./data/50b77a2ec778f18fa16caceccabdf7ba5059012921c20e2d4930258be9c65c5e.webm", "./test.mp4")
    # print(crops)
    meta = skvideo.io.ffprobe("data/926858efa7e7d3ba8bcf770b87a50cd303ed9f8262c4488fedce32f7be1e4d73.webm")
    num, den = map(int, meta["video"]["@avg_frame_rate"].split("/"))
    if den != 0:
        fps = num / den
    else:
        print("corruptedd")
        fps = 30
    frames = skvideo.io.vread("data/926858efa7e7d3ba8bcf770b87a50cd303ed9f8262c4488fedce32f7be1e4d73.webm", inputdict={'-r' : str(fps)})
    skvideo.io.vwrite("test.mp4", frames)
    # for i, (x, y) in enumerate(landmark.astype(int)):
        # if i in pre.stablePoints:
            # cv2.circle(frame, (x, y), 1, (255,0,0), -1)
    # cv2.imshow('bla', frame)
    # cv2.waitKey(0)

    # closing all open windows
    # cv2.destroyAllWindows()
    # print(crops)
    # write_video_ffmpeg(crops, "./data/clip-cropped2.mp4", "/usr/bin/ffmpeg")