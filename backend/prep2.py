import sys; sys.argv.extend(["",""])
import cv2
import numpy as np
import skvideo.io
from tqdm import tqdm
from pathlib import Path
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision


class Preprocessor:
    """
    MediaPipe-based mouth cropper with temporal smoothing.
    """

    MOUTH_IDXS = [
        61, 146, 91, 181, 84, 17, 314, 405, 321, 375, 291,
        78, 95, 88, 178, 87, 14, 317, 402, 318, 324, 308
    ]
    STABLE_IDXS = [1, 133, 362]
    TARGET = np.float32([
        [48, 52],   # nose
        [34, 40],   # left eye
        [62, 40],   # right eye
    ])

    def __init__(self, model_path="data/misc/face_landmarker.task", crop_size=(96, 96), ema_alpha=0.85):
        self.crop_size = crop_size
        self.alpha = ema_alpha
        self.prev_landmarks = None

        base = python.BaseOptions(model_asset_path=model_path)
        opts = vision.FaceLandmarkerOptions(
            base_options=base,
            num_faces=1,
            output_face_blendshapes=False,
            output_facial_transformation_matrixes=False,
        )
        self.detector = vision.FaceLandmarker.create_from_options(opts)

    def detect_landmarks(self, frame):
        h, w, _ = frame.shape
        mp_img = mp.Image(mp.ImageFormat.SRGB, frame)
        res = self.detector.detect(mp_img)

        if not res.face_landmarks:
            return None

        lm = res.face_landmarks[0]
        pts = np.array([[p.x * w, p.y * h] for p in lm], dtype=np.float32)
        return pts

    def smooth(self, lm):
        if self.prev_landmarks is None:
            self.prev_landmarks = lm
            return lm
        smoothed = self.alpha * self.prev_landmarks + (1 - self.alpha) * lm
        self.prev_landmarks = smoothed
        return smoothed

    def align_and_crop(self, frame, lm):
        # Affine alignment
        src = lm[self.STABLE_IDXS].astype(np.float32)
        M = cv2.getAffineTransform(src, self.TARGET)
        aligned = cv2.warpAffine(frame, M, self.crop_size)

        # Transform landmarks
        lm_h = np.hstack([lm, np.ones((lm.shape[0], 1), dtype=np.float32)])
        lm_a = (M @ lm_h.T).T

        mouth = lm_a[self.MOUTH_IDXS]
        x, y, w, h = cv2.boundingRect(mouth.astype(np.int32))

        pad = 8
        x0 = max(x - pad, 0)
        y0 = max(y - pad, 0)
        x1 = min(x + w + pad, aligned.shape[1])
        y1 = min(y + h + pad, aligned.shape[0])

        crop = aligned[y0:y1, x0:x1]
        crop = cv2.resize(crop, self.crop_size)

        return crop

    def align_and_crop2(self, frame, lm):
        """
        Option 2: rotate by eye line only, then crop mouth.
        No affine / no similarity transform.
        """
        LEFT_EYE = 133
        RIGHT_EYE = 362

        left = lm[LEFT_EYE]
        right = lm[RIGHT_EYE]
        dx = right[0] - left[0]
        dy = right[1] - left[1]
        angle = np.degrees(np.arctan2(dy, dx))
        center = tuple(((left + right) / 2).astype(float))
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(
            frame,
            M,
            (frame.shape[1], frame.shape[0]),
            flags=cv2.INTER_LINEAR,
            borderMode=cv2.BORDER_REPLICATE,
        )
        lm_h = np.hstack([lm, np.ones((lm.shape[0], 1))])
        lm_r = (M @ lm_h.T).T

        mouth = lm_r[self.MOUTH_IDXS].astype(np.int32)
        x, y, w, h = cv2.boundingRect(mouth)

        pad_x = int(0.4 * w)
        pad_y = int(0.6 * h)

        x0 = max(x - pad_x, 0)
        y0 = max(y - pad_y, 0)
        x1 = min(x + w + pad_x, rotated.shape[1])
        y1 = min(y + h + pad_y, rotated.shape[0])

        crop = rotated[y0:y1, x0:x1]

        if crop.size == 0:
            return cv2.resize(frame, self.crop_size)

        crop = cv2.resize(crop, self.crop_size)
        return crop

    def process_video(self, input_path: Path, output_path: Path):
        meta = skvideo.io.ffprobe(str(input_path))
        num, den = map(int, meta["video"]["@avg_frame_rate"].split("/"))
        if den==0:
            fps = 30
        else:
            fps = int(num / den)
        frames = skvideo.io.vread(str(input_path), inputdict={'-r' : str(fps)})
        # skvideo.io.vwrite("test.mp4", frames)
        mouth_crops = []
        # print(len(frames))
        for frame in tqdm(frames, desc="Processing"):
            lm = self.detect_landmarks(frame)
            if lm is None:
                if mouth_crops:
                    mouth_crops.append(mouth_crops[-1])
                continue

            lm = self.smooth(lm)
            crop = self.align_and_crop(frame, lm)
            mouth_crops.append(crop)
        # print(len(mouth_crops))
        skvideo.io.vwrite(str(output_path), np.stack(mouth_crops)) # maybe just use from av_hubert.avhubert.preparation.align_mouth import write_video_ffmpeg
        return np.stack(mouth_crops)
