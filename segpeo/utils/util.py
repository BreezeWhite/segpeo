import urllib
from pathlib import Path

import cv2
import torch
import numpy as np


KERNELS = [None] + [cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (size, size)) for size in range(1,30)]
DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'


def get_unknown_tensor_from_pred(pred, rand_width=30, train_mode=True):
    ### pred: N, 1 ,H, W 
    N, C, H, W = pred.shape

    pred = pred.data.cpu().numpy()
    uncertain_area = np.ones_like(pred, dtype=np.uint8)
    uncertain_area[pred<1.0/255.0] = 0
    uncertain_area[pred>1-1.0/255.0] = 0

    for n in range(N):
        uncertain_area_ = uncertain_area[n,0,:,:] # H, W
        if train_mode:
            width = np.random.randint(1, rand_width)
        else:
            width = rand_width // 2
        uncertain_area_ = cv2.dilate(uncertain_area_, KERNELS[width])
        uncertain_area[n,0,:,:] = uncertain_area_

    weight = np.zeros_like(uncertain_area)
    weight[uncertain_area == 1] = 1
    weight = torch.from_numpy(weight).to(DEVICE)

    return weight


def download_checkpoint(store_path: Path) -> Path:
    store_path = Path(store_path)
    if not store_path.parent.exists():
        store_path.parent.mkdir()

    url = 'https://github.com/BreezeWhite/segpeo/releases/download/checkpoints/SGHM-ResNet50.pth'
    resp = urllib.request.urlopen(url)
    length = int(resp.getheader('Content-Length', -1))

    chunk_size = 2 ** 9
    total = 0
    with open(store_path, 'wb') as out:
        while True:
            print(f'Downloading ckpt: {total*100/length:.1f}% {total}/{length}', end='\r')
            data = resp.read(chunk_size)
            if not data:
                break
            total += out.write(data)
        print(f'Downloading ckpt: 100% {length}/{length}'+' '*20)

    return store_path
