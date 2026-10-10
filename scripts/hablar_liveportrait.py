"""Hace hablar una foto con LivePortrait (modo humano) a partir de un audio.

La boca se abre según el volumen del audio (retarget_lip), con parpadeos
periódicos (retarget_eye) y un leve movimiento natural de cabeza.
Uso: python hablar_lp.py foto.jpg voz.wav salida.mp4
"""
import sys, wave, subprocess
import numpy as np
import cv2
import torch

from src.config.argument_config import ArgumentConfig
from src.config.inference_config import InferenceConfig
from src.config.crop_config import CropConfig
from src.live_portrait_pipeline import LivePortraitPipeline
from src.utils.camera import get_rotation_matrix
from src.utils.crop import prepare_paste_back, paste_back
from src.utils.retargeting_utils import calc_lip_close_ratio, calc_eye_close_ratio

foto, voz, salida = sys.argv[1:4]
FPS = 25
torch.set_num_threads(4)

inf_cfg = InferenceConfig(flag_force_cpu=True, flag_use_half_precision=False, flag_do_torch_compile=False)
crop_cfg = CropConfig(flag_force_cpu=True, det_thresh=0.05)
pipe = LivePortraitPipeline(inference_cfg=inf_cfg, crop_cfg=crop_cfg)
w = pipe.live_portrait_wrapper

img = cv2.cvtColor(cv2.imread(foto), cv2.COLOR_BGR2RGB)
crop = pipe.cropper.crop_source_image(img, crop_cfg)
if crop is None:
    sys.exit("NO_FACE")
I_s = w.prepare_source(crop['img_crop_256x256'])
lmk = crop['lmk_crop']
info = w.get_kp_info(I_s)
f_s = w.extract_feature_3d(I_s)
x_s = w.transform_keypoint(info)
R_s = get_rotation_matrix(info['pitch'], info['yaw'], info['roll'])
mask = prepare_paste_back(inf_cfg.mask_crop, crop['M_c2o'], dsize=(img.shape[1], img.shape[0]))
lip0 = float(calc_lip_close_ratio(lmk[None])[0][0])
eye0 = float(calc_eye_close_ratio(lmk[None])[0][0])
print(f"cara detectada; lip0={lip0:.3f} eye0={eye0:.3f}", flush=True)

# envolvente del audio -> apertura de boca por cuadro
wf = wave.open(voz)
sr = wf.getframerate()
a = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16).astype(np.float32)
if wf.getnchannels() > 1:
    a = a.reshape(-1, wf.getnchannels()).mean(1)
hop = sr // FPS
n = len(a) // hop
rms = np.array([np.sqrt(np.mean(a[i*hop:(i+1)*hop] ** 2)) for i in range(n)])
env = np.clip(rms / (np.percentile(rms, 95) + 1e-6), 0, 1) ** 0.8
sm = np.zeros(n)
for i in range(n):
    p = sm[i-1] if i else 0
    sm[i] = p + (env[i] - p) * (0.75 if env[i] > p else 0.4)

rng = np.random.default_rng(7)
blinks = set()
t = int(FPS * 0.8)
while t < n:
    blinks.update(range(t, t + 4))
    t += int(FPS * rng.uniform(1.8, 3.2))
blink_curve = {0: 0.6, 1: 0.05, 2: 0.15, 3: 0.6}

frames = []
for i in range(n):
    tt = i / FPS
    # cabeza: balanceo suave + pequeño asentimiento al hablar
    dp = 1.5 * np.sin(tt * 1.7) + 3.0 * sm[i]
    dy = 2.5 * np.sin(tt * 0.9 + 1.0)
    dr = 1.2 * np.sin(tt * 1.3 + 2.0)
    R_d = get_rotation_matrix(info['pitch'] + dp, info['yaw'] + dy, info['roll'] + dr)
    R_new = (R_d @ R_s.permute(0, 2, 1)) @ R_s
    x_d = info['scale'] * (info['kp'] @ R_new + info['exp']) + info['t']
    # boca
    lip_target = lip0 + 0.55 * sm[i]
    lip_delta = w.retarget_lip(x_s, w.calc_combined_lip_ratio([[lip_target]], lmk))
    x_d = x_d + lip_delta
    # parpadeo
    if i in blinks:
        k = min(blink_curve.keys(), key=lambda b: abs(b - (i - min(j for j in blinks if j <= i and j > i - 4))))
        eye_target = eye0 * blink_curve[k]
        x_d = x_d + w.retarget_eye(x_s, w.calc_combined_eye_ratio([[eye_target]], lmk))
    x_d = w.stitching(x_s, x_d)
    out = w.parse_output(w.warp_decode(f_s, x_s, x_d)['out'])[0]
    frames.append(paste_back(out, crop['M_c2o'], img, mask))
    if i % 10 == 0:
        print(f"cuadro {i}/{n}", flush=True)

h, wd = frames[0].shape[:2]
h2, w2 = h - h % 2, wd - wd % 2
proc = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                         "-s", f"{w2}x{h2}", "-r", str(FPS), "-i", "-", "-i", voz,
                         "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "17",
                         "-c:a", "aac", "-b:a", "160k", "-shortest", salida], stdin=subprocess.PIPE)
for f in frames:
    proc.stdin.write(np.ascontiguousarray(f[:h2, :w2]).tobytes())
proc.stdin.close(); proc.wait()
print("LISTO", salida)
