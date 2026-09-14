# Depth Anything V2 Small on the graded still -> 16-bit depth PNG (near = bright).
import time, numpy as np, torch
from PIL import Image
from transformers import AutoImageProcessor, AutoModelForDepthEstimation
dev = "mps" if torch.backends.mps.is_available() else "cpu"
t = time.time()
proc = AutoImageProcessor.from_pretrained("depth-anything/Depth-Anything-V2-Small-hf")
model = AutoModelForDepthEstimation.from_pretrained("depth-anything/Depth-Anything-V2-Small-hf").to(dev).eval()
im = Image.open("ev_s11_graded.png").convert("RGB")
with torch.no_grad():
    out = model(**{k: v.to(dev) for k, v in proc(images=im, return_tensors="pt").items()}).predicted_depth
d = torch.nn.functional.interpolate(out[:, None], size=im.size[::-1], mode="bicubic", align_corners=False)[0, 0].cpu().numpy()
d = (d - d.min()) / (d.max() - d.min())
Image.fromarray((d * 65535).astype(np.uint16)).save("ev_depth16.png")
Image.fromarray((d * 255).astype(np.uint8)).save("ev_depth_preview.png")
import resource
print(f"device={dev} time={time.time()-t:.1f}s maxrss={resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1e9:.2f}GB")
