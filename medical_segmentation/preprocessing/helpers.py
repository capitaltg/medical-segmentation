import os
import math
import logging

import numpy as np
import matplotlib.pyplot as plt
from scipy import ndimage
from PIL import Image

HOUNSFIELD_MIN = -1000
HOUNSFIELD_MAX = 2000
HOUNSFIELD_RANGE = HOUNSFIELD_MAX - HOUNSFIELD_MIN


def build_mask(pixels_array):
    mask = np.zeros((512, 512), np.uint8)
    for x, y in pixels_array:
        mask[x][y] = 1
    mask = ndimage.binary_fill_holes(mask).astype(int)
    return mask


def contour_to_pixels(contour_coord, dicom_structure):
    x0 = contour_coord[len(contour_coord) - 3]
    y0 = contour_coord[len(contour_coord) - 2]
    coordinates = []
    for i in range(0, len(contour_coord), 3):
        # get the (x,y) coordinate, ignore Z
        x = contour_coord[i]
        y = contour_coord[i + 1]
        # compute the length from x,y to x0,y0
        # we do this to fill in the pixels from the contour points
        length = math.sqrt((x - x0)**2 + (y - y0)**2)
        # round up length * 2, and add 1 to ensure all points in between
        # are filled in
        length = math.ceil(length * 2) + 1
        # add interpolated points
        for j in range(1, length + 1):
            coordinates.append([(x - x0) * j / length + x0, (y - y0) * j / length + y0])
        # set the comparison points for next loop
        x0 = x
        y0 = y
    return pixels_from_spacing(coordinates, dicom_structure)

def pixels_from_spacing(coordinates, dicom_structure):
    origin_x, origin_y, _origin_z = dicom_structure.ImagePositionPatient
    spacing_x, spacing_y = float(
        dicom_structure.PixelSpacing[0]), float(dicom_structure.PixelSpacing[1]
    )
    pixels = [(np.rint((y - origin_y) / spacing_y),
    np.rint((x - origin_x) / spacing_x)) for x, y in coordinates]
    pixels = [(int(x), int(y)) for x, y in list(set(pixels))]

def fetch_contour_sop_instance_uid(metadata, uid):
    structures = {item.ROINumber: item.ROIName for item in metadata.StructureSetROISequence}
    roi_seq = metadata.ROIContourSequence
    for roi in roi_seq:
        if structures[roi.ReferencedROINumber] == 'Lung_L':
            logging.info('ROI Name %s number %s',
                structures[roi.ReferencedROINumber], roi.ReferencedROINumber)
            for contour in roi.ContourSequence:
                if contour.ContourImageSequence[0].ReferencedSOPInstanceUID == uid:
                    return contour
    return None

def save_image_array(img_arr, target_path):
    img = Image.fromarray(img_arr.astype(np.uint8))
    img.save(target_path)
    return img


def normalize_intensity(img):
    img[img < HOUNSFIELD_MIN] = HOUNSFIELD_MIN
    img[img > HOUNSFIELD_MAX] = HOUNSFIELD_MAX
    return (img - HOUNSFIELD_MIN) / HOUNSFIELD_RANGE


def save_images_to_files(subdir, imgarr, contour_mask, dicom_file, output_dir = 'val-output'):
    masks_dir = os.path.join(output_dir, 'masks', 'lung_l')
    images_dir = os.path.join(output_dir, 'images', 'lung_l')
    plt.axis('off')
    plt.imshow(contour_mask, cmap="gray")
    if not os.path.exists(masks_dir):
        os.makedirs(masks_dir)
    if not os.path.exists(images_dir):
        os.makedirs(images_dir)
    plt.savefig(f"{masks_dir}/{subdir}-{dicom_file}.png",
        bbox_inches='tight', pad_inches = 0)
    plt.clf()
    plt.axis('off')
    plt.imshow(imgarr, cmap="gray")
    plt.savefig(f"{images_dir}/{subdir}-{dicom_file}.png",
        bbox_inches='tight', pad_inches = 0)
    plt.clf()
