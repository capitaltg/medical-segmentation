'''
Reads DICOM medical imaging files and outputs rasterized representations
suitable for ML training purposes
'''

import os
import click
import logging
import matplotlib.pyplot as plt
import numpy as np
from pydicom import dcmread

from helpers import build_mask, normalize_intensity
from helpers import contour_to_pixels, save_images_to_files
from helpers import fetch_contour_sop_instance_uid


def run(base_path, subdir, save_images=False, mode='training'):
    metadata = dcmread(os.path.join(base_path, 'metadata', '1-1.dcm'))
    num_with_rois = 0

    img_dir = os.path.join(base_path, 'images')

    for dicom_file in os.listdir(img_dir):
        print(dicom_file)
        full_dicom_path = os.path.join(img_dir, dicom_file)

        dicom_img = dcmread(full_dicom_path)
        sop_uid = dicom_img.SOPInstanceUID
        imgarr = dicom_img.pixel_array
        contour_obj = fetch_contour_sop_instance_uid(metadata, sop_uid, base_path)

        if not contour_obj:
            logging.info(
                "Image file SOPInstanceUID %s has no ROI data, using empty mask...", sop_uid)
            contour_mask = np.zeros((512, 512), np.uint8)
        else:
            num_with_rois += 1
            contour_pixels = []
            for c in contour_obj:
                contour_coord = c.ContourData
                contour_pixels.extend(contour_to_pixels(contour_coord, dicom_img))
            contour_mask = build_mask(contour_pixels)

        imgarr = normalize_intensity(imgarr)

        if save_images:
            save_images_to_files(plt, subdir, imgarr, contour_mask, dicom_file, f'{mode}-output')

    logging.info("Total images with ROIs %s, %s", num_with_rois, (num_with_rois/130.) * 100)



@click.command()
@click.option('--mode', default='training', help='Training or testing processing mode.')
def process_images(mode):
    base_dir = './lungs'
    img_folder_base = os.path.join(base_dir, f'{mode}')
    subdirs = os.listdir(img_folder_base)
    for target_subdir in [d for d in subdirs if os.path.isdir(os.path.join(img_folder_base, d))]:
        dataset_path = os.path.join(img_folder_base, target_subdir)
        logging.info("Running process on %s ...", dataset_path)
        run(dataset_path, target_subdir, save_images=True, mode=mode)


if __name__ == '__main__':
    process_images()
