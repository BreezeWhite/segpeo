import argparse
import os
import glob
from pathlib import Path
from PIL import Image

import cv2
import numpy as np
import torch
import torch.nn as nn
from torchvision.utils import save_image

import utils
import inference
from model.model import HumanSegment, HumanMatting


# --------------- Arguments ---------------
parser = argparse.ArgumentParser(description='Test Images')
parser.add_argument(
    '-i',
    '--image-path',
    type=str,
    required=True,
    help='Could be a file path or a directory that contains images',
)
parser.add_argument('--result-dir', type=str, default='./results')
parser.add_argument('--gt-dir', type=str, default=None)
parser.add_argument('--pretrained-weight', type=str, required=True)

args = parser.parse_args()

if not os.path.exists(args.pretrained_weight):
    print('Cannot find the pretrained model: {0}'.format(args.pretrained_weight))
    exit(1)

# --------------- Main ---------------
# Load Model
model = HumanMatting(backbone='resnet50')
model = nn.DataParallel(model).cuda().eval()
model.load_state_dict(torch.load(args.pretrained_weight))
print('Load checkpoint successfully ...')


# Load Images
img_path = Path(args.image_path)
if img_path.is_file():
    image_list = [img_path]
elif img_path.is_dir():
    image_list = sorted([
        ff
        for ff in img_path.iterdir()
        if ff.suffix.lower() in ('.jpg', '.png')
    ])
else:
    print('Unknown file type of path:', img_path)
    exit(1)

print(f'Found {len(image_list)} images.')

# Process 
for i, image_path in enumerate(image_list):
    image_name = os.path.basename(image_path)
    print(f'Process: {i+1} / {len(image_list)}')

    with Image.open(image_path) as img:
        img = img.convert('RGB')

    # inference
    pred_alpha, pred_mask = inference.single_inference(model, img)

    # save results
    output_dir = Path(args.result_dir)
    if not output_dir.exists():
        output_dir.mkdir()

    out_name = os.path.splitext(image_name)[0] + '.png'
    save_path = output_dir / out_name
    Image.fromarray(((pred_alpha * 255).astype('uint8')), mode='L').save(save_path)
