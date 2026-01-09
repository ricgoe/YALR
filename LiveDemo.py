import cv2
import numpy as np
from pathlib import Path
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision


class LiveDemo:
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

    def __init__(self, cam_index=0, model_path="face_landmarker.task", crop_size=(96, 96), ema_alpha=0.85):
        self.crop_size = crop_size
        self.alpha = ema_alpha
        self.prev_landmarks = None
        self.cam_index = cam_index
        self.last_lm = np.zeros((478, 2), dtype=np.float32)
        self.window= np.ones((500, 700, 3), dtype=np.uint8) * 255

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

    def run(self):
        cap = cv2.VideoCapture(self.cam_index)
        if not cap.isOpened():
            raise RuntimeError(f"Could not open camera index {self.cam_index}")
        try:
            while True:
                ok, frame = cap.read()
                if not ok or frame is None:
                    continue
                # cv2.imshow("LiveDemo", frame)
                lm = self.detect_landmarks(frame[...,::-1])
                lm = self.last_lm if lm is None else self.smooth(lm)
                crop = self.align_and_crop(frame, lm)
                self.last_lm = lm
                cv2.imshow("LiveDemo Crop", crop)
                cv2.imshow("LiveDemo Frame", cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE))
                if cv2.waitKey(1) & 0xFF in [ord("q"), 27]:
                    break
        finally:
            cap.release()
            cv2.destroyAllWindows()

if __name__ == "__main__":
    demo = LiveDemo(crop_size=(300,300))
    # a=demo.detect_landmarks(cv2.imread("test.jpg")[...,::-1])
    # print(a.shape, a.dtype)
    demo.run()