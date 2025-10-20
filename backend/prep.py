import sys; sys.argv.extend(["",""])
import dlib, cv2
import numpy as np
import skvideo
import skvideo.io
from tqdm import tqdm
from av_hubert.avhubert.preparation.align_mouth import landmarks_interpolate, crop_patch, write_video_ffmpeg
from pathlib import Path


class Preprocessor:
    
    def __init__(self, predictor_path: Path, mean_face_path: Path,  std_size: tuple[int] = (256, 256)):
        self.STD_SIZE = std_size
        self.detector = dlib.get_frontal_face_detector()
        self.predictor = dlib.shape_predictor(str(predictor_path))
        self.mean_face_landmarks = np.load(mean_face_path)
        self.stablePoints = [33, 36, 39, 42, 45] # tip of nose + inner and outer corner of both eyes
        
    def detect_landmark(self, image):
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        rects = self.detector(gray, 1)
        coords = None
        for (_, rect) in enumerate(rects):
            shape = self.predictor(gray, rect)
            coords = np.zeros((68, 2), dtype=np.int32)
            for i in range(0, 68):
                coords[i] = (shape.part(i).x, shape.part(i).y)
        return coords
    
    def get_mouth_crops(self, video_path: Path):
        frames = skvideo.io.vread(video_path)
        landmarks = []
        for frame in tqdm(frames):
            landmark = self.detect_landmark(frame)
            landmarks.append(landmark)
        preprocessed_landmarks = landmarks_interpolate(landmarks)
        crops = crop_patch(video_path, preprocessed_landmarks, self.mean_face_landmarks, self.stablePoints, self.STD_SIZE, 
                        window_margin=12, start_idx=48, stop_idx=68, crop_height=96, crop_width=96)
        return crops
    
        
        
if __name__ == "__main__":
    pre = Preprocessor(
        predictor_path="data/misc/shape_predictor_68_face_landmarks.dat", 
        mean_face_path="data/misc/20words_mean_face.npy"
    )
    crops = pre.get_mouth_crops("data/clip.mp4")
    write_video_ffmpeg(crops, "./data/clip-cropped.mp4", "/home/richard/.local/bin/ffmpeg")

