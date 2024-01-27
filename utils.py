import math, IPython, base64, html
import numpy as np
import cv2 as cv
import urllib.request

# Utility function to show an image
def show(*images, enlarge_small_images = True, max_per_row = -1, font_size = 0):
  if len(images) == 2 and type(images[1])==str:
      images = [(images[0], images[1])]

  def convert_for_display(img):
      if img.dtype!=np.uint8:
          a, b = img.min(), img.max()
          if a==b:
              offset, mult, d = 0, 0, 1
          elif a<0:
              offset, mult, d = 128, 127, max(abs(a), abs(b))
          else:
              offset, mult, d = 0, 255, b
          img = np.clip(offset + mult*(img.astype(float))/d, 0, 255).astype(np.uint8)
      return img

  def convert(imgOrTuple):
      try:
          img, title = imgOrTuple
          if type(title)!=str:
              img, title = imgOrTuple, ''
      except ValueError:
          img, title = imgOrTuple, ''        
      if type(img)==str:
          data = img
      else:
          img = convert_for_display(img)
          if enlarge_small_images:
              REF_SCALE = 100
              h, w = img.shape[:2]
              if h<REF_SCALE or w<REF_SCALE:
                  scale = max(1, min(REF_SCALE//h, REF_SCALE//w))
                  img = cv.resize(img,(w*scale,h*scale), interpolation=cv.INTER_NEAREST)
          data = 'data:image/png;base64,' + base64.b64encode(cv.imencode('.png', img)[1]).decode('utf8')
      return data, title
    
  if max_per_row == -1:
      max_per_row = len(images)

  rows = [images[x:x+max_per_row] for x in range(0, len(images), max_per_row)]
  font = f"font-size: {font_size}px;" if font_size else ""

  html_content = ""
  for r in rows:
      l = [convert(t) for t in r]
      html_content += "".join(["<table><tr>"] 
              + [f"<td style='text-align:center;{font}'>{html.escape(t)}</td>" for _,t in l]    
              + ["</tr><tr>"] 
              + [f"<td style='text-align:center;'><img src='{d}'></td>" for d,_ in l]
              + ["</tr></table>"])
  IPython.display.display(IPython.display.HTML(html_content))

# Utility function to load an image from an URL
def load_from_url(url):
  resp = urllib.request.urlopen(url)
  image = np.asarray(bytearray(resp.read()), dtype=np.uint8)
  return cv.imdecode(image, cv.IMREAD_GRAYSCALE)

# Utility function to draw orientations over an image
def draw_orientations(fingerprint, orientations, strengths, mask, scale = 3, step = 8, border = 0):
    if strengths is None:
        strengths = np.ones_like(orientations)
    h, w = fingerprint.shape
    sf = cv.resize(fingerprint, (w*scale, h*scale), interpolation = cv.INTER_NEAREST)
    res = cv.cvtColor(sf, cv.COLOR_GRAY2BGR)
    d = (scale // 2) + 1
    sd = (step+1)//2
    c = np.round(np.cos(orientations) * strengths * d * sd).astype(int)
    s = np.round(-np.sin(orientations) * strengths * d * sd).astype(int) # minus for the direction of the y axis
    thickness = 1 + scale // 5
    for y in range(border, h-border, step):
        for x in range(border, w-border, step):
            if mask is None or mask[y, x] != 0:
                ox, oy = c[y, x], s[y, x]
                cv.line(res, (d+x*scale-ox,d+y*scale-oy), (d+x*scale+ox,d+y*scale+oy), (255,0,0), thickness, cv.LINE_AA)
    return res

# Utility function to generate gabor filter kernels

_sigma_conv = (3.0/2.0)/((6*math.log(10))**0.5)
# sigma is adjusted according to the ridge period, so that the filter does not contain more than three effective peaks 
def _gabor_sigma(ridge_period):
    return _sigma_conv * ridge_period

def _gabor_size(ridge_period):
    p = int(round(ridge_period * 2 + 1))
    if p % 2 == 0:
        p += 1
    return (p, p)

def gabor_kernel(period, orientation):
    f = cv.getGaborKernel(_gabor_size(period), _gabor_sigma(period), np.pi/2 - orientation, period, gamma = 1, psi = 0)
    f /= f.sum()
    f -= f.mean()
    return f
