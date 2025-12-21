import sys; sys.argv.extend(["",""])
import cv2
import numpy as np
import skvideo
import skvideo.io
from tqdm import tqdm
#from av_hubert.avhubert.preparation.align_mouth import landmarks_interpolate, crop_patch, write_video_ffmpeg
from pathlib import Path
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from mp2dlib import convert_landmarks_mediapipe_to_dlib


class Preprocessor:
    
    def __init__(self, mean_face_path: np.ndarray, std_size: tuple[int] = (256, 256)):
        self.STD_SIZE = std_size
        self.mp_baseoptions = python.BaseOptions(model_asset_path='data/misc/face_landmarker.task')
        self.mp_options = vision.FaceLandmarkerOptions(base_options=self.mp_baseoptions,
                                       output_face_blendshapes=True,
                                       output_facial_transformation_matrixes=True,
                                       num_faces=1)
        
        self.detector = vision.FaceLandmarker.create_from_options(self.mp_options)
        self.stablePoints = [33, 36, 39, 42, 45] # tip of nose + inner and outer corner of both eyes
        self.mean_face_landmarks = mean_face_path
        
    def detect_landmark(self, frame):
        h, w, _ = frame.shape

        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=frame
        )

        result = self.detector.detect(mp_image)

        if not result.face_landmarks:
            return None

        lm = result.face_landmarks[0]
        lmks_mp = np.array(
            [[p.x * w, p.y * h] for p in lm],
            dtype=np.float32
        )

        lmks_dlib = convert_landmarks_mediapipe_to_dlib(lmks_mp)

        return lmks_dlib.astype(np.int32)
    
    def get_mouth_crops(self, video_path: Path):
        frames = skvideo.io.vread(video_path)
        landmarks = []
        for frame in tqdm(frames):
            landmark = self.detect_landmark(frame)
            print(landmark)
            return frame, landmark
            landmarks.append(landmark)
        # preprocessed_landmarks = landmarks_interpolate(landmarks)
        # crops = crop_patch(video_path, preprocessed_landmarks, self.mean_face_landmarks, self.stablePoints, self.STD_SIZE, 
        #                 window_margin=12, start_idx=48, stop_idx=68, crop_height=96, crop_width=96)
        return crops
    
    
        
if __name__ == "__main__":
    pre = Preprocessor(mean_face_path="data/misc/20words_mean_face.npy")
    frame, landmark = pre.get_mouth_crops("data/VIDEO-2025-10-20-10-16-28.mp4")
    for i, (x, y) in enumerate(landmark.astype(int)):
        if i in pre.stablePoints:
            cv2.circle(frame, (x, y), 1, (255,0,0), -1)
    cv2.imshow('bla', frame)
    cv2.waitKey(0)

    # closing all open windows
    cv2.destroyAllWindows()
    
    #write_video_ffmpeg(crops, "./data/clip-cropped.mp4", "/opt/homebrew/bin/ffmpeg")

