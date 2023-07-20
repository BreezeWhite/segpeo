import argparse
import os
from pathlib import Path
from PIL import Image

import torch
import torch.nn as nn

import segpeo.inference as inference
from segpeo.model.model import HumanMatting
from segpeo.utils import download_checkpoint


PROJECT_ROOT = Path(__file__).parent.absolute()


class UnknownTypeOfPath(Exception):
    ...


def get_parser():
    parser = argparse.ArgumentParser(description='Test Images')
    parser.add_argument(
        '-i',
        '--image-path',
        type=str,
        required=True,
        help='Could be a file path or a directory that contains images',
    )
    parser.add_argument(
        '-o',
        '--output-dir',
        type=str,
        default=None,
        help='Path to output the result image. Default to the same folder of input image.'
    )
    parser.add_argument(
        '-c',
        '--checkpoint-path',
        type=str,
        default=None,
        help='Optionally provide your own checkpoint to use. Will download and use the default model if not specified.'
    )
    return parser


def main():
    parser = get_parser()
    args = parser.parse_args()

    # Check model weight exists
    if args.checkpoint_path:
        ckpt_path = args.checkpoint_path
    else:
        ckpt_path = PROJECT_ROOT / 'SGHM-ResNet50.pth'
        if not os.path.exists(ckpt_path):
            print(f'Checkpoint not found in {ckpt_path}. Downloading...')
            download_checkpoint(ckpt_path)

    # Load model
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    model = HumanMatting(backbone='resnet50')
    model = nn.DataParallel(model).to(device).eval()
    model.load_state_dict(torch.load(ckpt_path, map_location=device))
    print('Model loaded')

    # Load Images
    img_path = Path(args.image_path)
    if img_path.is_file():
        image_list = [img_path]
    elif img_path.is_dir():
        image_list = sorted([
            ff
            for ff in img_path.iterdir()
            if ff.suffix.lower() in ('.jpg', '.jpeg', '.png')
        ])
    else:
        raise UnknownTypeOfPath(args.image_path)

    # Process 
    for i, image_path in enumerate(image_list):
        image_name = os.path.basename(image_path)
        print(f'Process: {i+1} / {len(image_list)}')

        with Image.open(image_path) as img:
            img = img.convert('RGB')

        # inference
        pred_alpha, pred_mask = inference.single_inference(model, img)

        # save results
        output_dir = Path(args.output_dir) if args.output_dir else image_path.parent
        if not output_dir.exists():
            output_dir.mkdir()

        out_name = os.path.splitext(image_name)[0] + '_mask.png'
        save_path = output_dir / out_name
        Image.fromarray(((pred_alpha * 255).astype('uint8')), mode='L').save(save_path)
        print(f'Image saved to {save_path}')


if __name__ == '__main__':
    main()
