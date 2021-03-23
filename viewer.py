
import cv2
import numpy as np
import random

def getquad(bytestream, voidptr):
    bts = [bytestream[k+voidptr] for k in [0, 1, 2, 3]]
    btv = [int(k[0]) for k in bts]
    return bts, sum(btv[i]*256**(3-i) for i in [0, 1, 2, 3])

def read_threadmap(bytestream, cmap):
    threadstreams = []
    for i in range(25):
        if bytestream[37 + 24*i] != b'\x04':
            break
        threadstreams.append([bytestream[37+j + 24*i] for j in range(24)])
    
    tids = []
    for ts in threadstreams:
        tids.append("".join([chr(ts[i][0]) for i in [1, 2, 3, 4]]))

    print(f"using {len(tids)} different threads")
    print("injecting shuffled threadmapping")
    tidmap = []
    for t in tids:
        if t in cmap.keys():
            print(f"knwn {t}")
            tidmap.append(cmap[t])
        else:
            print(f"unkn {t}")
            tidmap.append([
                0, 0, 255
            ])

    return tidmap

def read_colormap():
    colormap = {}
    with open("colormap.txt", "r") as f:
        data = f.read().split("\n")
        for dl in data:
            try:
                dcut = list(dl.split(","))
                colormap[str(int(dcut[0]))] = [int(dcut[i]) for i in [3, 2, 1]]
            except Exception as e:
                print(f"failed while parsing {dl}")
                print(e)
    return colormap

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

cmap = read_colormap()
threadmapping = read_threadmap(bytestream, cmap)

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

_, imw = getquad(bytestream, bskip + 10)
_, imh = getquad(bytestream, bskip + 14)
outmat = np.zeros((imh, imw, 3), np.uint8)


print(f"image width {imw}")
print(f"image height {imh}")
print(f"total image size {imw*imh} pixels")
for i in range(imw*imh):
    try:
        outmat[i//imw][i % imw] = threadmapping[getquad(bytestream, bskip + 18 + i * 4)[1] - 1]
    except Exception as e:
        print(e, getquad(bytestream, bskip + 18 + i * 4)[1])

width = int(outmat.shape[1] * 800 / 100)
height = int(outmat.shape[0] * 800 / 100)
resized = cv2.resize(outmat, (width, height), interpolation = cv2.INTER_NEAREST)

cv2.imshow("d", resized)
while True:
    cv2.waitKey(10)