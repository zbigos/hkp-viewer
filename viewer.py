
import cv2
import numpy as np

def getquad(bytestream, voidptr):
    bts = [bytestream[k+voidptr] for k in [0, 1, 2, 3]]
    btv = [int(k[0]) for k in bts]
    return bts, sum(btv[i]*256**(3-i) for i in [0, 1, 2, 3])

### reading the file ###
bytestream = []
f = open("Wzor.hkp", "rb")
try:
    byte = f.read(1)
    while byte != b'':
        byte = f.read(1)
        bytestream.append(byte)
finally:
    f.close()

print(f"read {len(bytestream)} bytes")

bskip = 0
for q in range(len(bytestream)):
    hook = True
    for li, l in enumerate([b'A', b'u', b't', b'o']):
        if bytestream[q+li] != l:
            hook = False
    if hook:
        break
    
    bskip += 1

print(f"skipping {bskip} bytes")
for bi, b in enumerate(bytestream[bskip:bskip+100]):
    print(bi, b)

_, imw = getquad(bytestream, bskip + 10)
_, imh = getquad(bytestream, bskip + 14)
outmat = np.zeros((imh, imw, 3), np.uint8)

qdiff = [[0, 0, 0], [255, 0, 0], [0, 255, 0], [0, 0, 255], [255, 255, 0], [0, 255, 255], [255, 0, 255]]

print(f"image width {imw}")
print(f"image height {imh}")
print(f"total image size {imw*imh} pixels")
for i in range(imw*imh):
    #print(getquad(bytestream, bskip + 18 + i * 4))
    try:
        outmat[i//imw][i % imw] = qdiff[getquad(bytestream, bskip + 18 + i * 4)[1]]
    except Exception as e:
        print(e, getquad(bytestream, bskip + 18 + i * 4)[1])
cv2.imshow("d", outmat)
while True:
    cv2.waitKey(10)