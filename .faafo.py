from contextlib import suppress
from backend.prep import Preprocessor
from av_hubert.avhubert.preparation.align_mouth import write_video_ffmpeg


if __name__ == "__main__":
    pre = Preprocessor(mean_face_path="data/misc/20words_mean_face.npy")
    crops = pre.get_mouth_crops("./data/müllero-uncut.mp4")
    # for i, (x, y) in enumerate(landmark.astype(int)):
        # if i in pre.stablePoints:
            # cv2.circle(frame, (x, y), 1, (255,0,0), -1)
    # cv2.imshow('bla', frame)
    # cv2.waitKey(0)

    # closing all open windows
    # cv2.destroyAllWindows()
    # print(crops)
    write_video_ffmpeg(crops, "./data/clip-cropped2.mp4", "/usr/bin/ffmpeg")