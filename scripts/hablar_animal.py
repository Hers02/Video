import cv2, numpy as np, wave, sys
img = cv2.imread('mono.jpg').astype(np.float32)
H, W = img.shape[:2]
w = wave.open('voice.wav'); sr = w.getframerate()
a = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32)
fps = 25; hop = sr // fps; n = len(a) // hop
rms = np.array([np.sqrt(np.mean(a[i*hop:(i+1)*hop]**2)) for i in range(n)])
rms = rms / (np.percentile(rms, 95) + 1e-6)
env = np.clip(rms, 0, 1)
sm = np.zeros_like(env)
for i in range(n):  # fast attack, slower release
    p = sm[i-1] if i else 0
    sm[i] = p + (env[i]-p)*(0.7 if env[i] > p else 0.35)
# mouth geometry (in 928x936 image)
cx, top, open_y, chin = 505, 375, 430, 600
rx = 150
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
wx = np.clip(1 - ((xx-cx)/rx)**2, 0, 1)**1.5
ramp = np.clip((yy-top)/(open_y-top), 0, 1)
fall = np.clip(1 - (yy-open_y)/(chin+80-open_y), 0, 1) ** 0.7
fall = np.where(yy < open_y, 1.0, fall)
field = (wx * ramp * fall).astype(np.float32)
out = cv2.VideoWriter('frames.mp4', cv2.VideoWriter_fourcc(*'mp4v'), fps, (720, 720))
for i in range(n):
    A = 38 * sm[i]
    t = i / fps
    mapy = yy - A * field
    fr = cv2.remap(img, xx, mapy, cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)
    # darken newly opened mouth interior a bit
    dark = (wx * ramp * (yy < open_y + A)).astype(np.float32) * (yy > top+10) * min(1, A/20) * 0.35
    fr = fr * (1 - dark[..., None])
    # gentle head bob + slow push-in
    s = 1.0 + 0.03 * t / (n/fps) + 0.006 * sm[i]
    ang = 1.2 * np.sin(t * 2.1) + 1.5 * sm[i]
    M = cv2.getRotationMatrix2D((cx, 380), ang, s)
    fr = cv2.warpAffine(fr, M, (W, H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)
    fr = cv2.resize(fr[0:928, 0:928], (720, 720), interpolation=cv2.INTER_AREA)
    out.write(np.clip(fr, 0, 255).astype(np.uint8))
out.release(); print(n, 'frames')
