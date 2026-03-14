import cv2
import numpy as np
from PIL import Image

def process_logo():
    in_path = r'C:\Users\Sadheesh\.gemini\antigravity\brain\e649dc5a-9c19-4e31-8e35-1feb3a8d2a4a\media__1773469288605.jpg'
    out_path = r'e:\varun projects\you_can_tech-voting\static\logo.png'
    
    img = Image.open(in_path).convert('RGBA')
    data = np.array(img)
    
    # Calculate brightness
    rgb = data[:,:,:3]
    brightness = np.max(rgb, axis=2)
    
    # Map brightness to alpha. Boost alpha to 255 for anything above a certain threshold if it should be solid
    # Since it's a sleek logo, maybe brightness directly map to alpha gives a nice luminous effect!
    # Let's threshold it a bit: if brightness > 200, make alpha 255.
    alpha = np.clip(brightness * 1.5, 0, 255).astype(np.uint8)
    
    data[:,:,3] = alpha
    
    # Find bounding box of non-transparent pixels
    coords = np.argwhere(alpha > 10)
    if len(coords) > 0:
        y0, x0 = coords.min(axis=0)
        y1, x1 = coords.max(axis=0)
        # Add a little padding
        pad = 20
        y0 = max(0, y0 - pad)
        y1 = min(data.shape[0], y1 + pad)
        x0 = max(0, x0 - pad)
        x1 = min(data.shape[1], x1 + pad)
        data = data[y0:y1, x0:x1]
    
    out_img = Image.fromarray(data)
    out_img.thumbnail((300, 300), Image.Resampling.LANCZOS)
    out_img.save(out_path)
    print("Saved logo to", out_path)

if __name__ == '__main__':
    process_logo()
