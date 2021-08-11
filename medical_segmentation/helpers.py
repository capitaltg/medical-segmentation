import os
import math
import numpy as np
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


def contour_to_pixels(contour_coord, ds):
    x0 = contour_coord[len(contour_coord) - 3]
    y0 = contour_coord[len(contour_coord) - 2]
    coord = []
    for i in range(0, len(contour_coord), 3):
        # get the (x,y) coordinate, ignore Z
        x = contour_coord[i]
        y = contour_coord[i + 1]
        # compute the length from x,y to x0,y0
        # we do this to fill in the pixels from the contour points
        l = math.sqrt((x - x0)**2 + (y - y0)**2)
        # round up length * 2, and add 1 to ensure all points in between
        # are filled in
        l = math.ceil(l * 2) + 1
        # add interpolated points
        for j in range(1, l + 1):
            coord.append([(x - x0) * j / l + x0, (y - y0) * j / l + y0])
        # set the comparison points for next loop
        x0 = x
        y0 = y

    x_spacing, y_spacing = float(ds.PixelSpacing[0]), float(ds.PixelSpacing[1])
    origin_x, origin_y, _origin_z = ds.ImagePositionPatient

    pixels = [(np.rint((y - origin_y) / y_spacing), np.rint((x - origin_x) / x_spacing)) for x, y in coord]
    pixels = [(int(x), int(y)) for x, y in list(set(pixels))]
    return pixels


def fetch_contour_sop_instance_uid(metadata, uid, base_path):
    structures = {item.ROINumber: item.ROIName for item in metadata.StructureSetROISequence}
    roi_seq = metadata.ROIContourSequence
    left_lung_roi = find_roi_name(base_path)                  
    for roi in roi_seq:
        if structures[roi.ReferencedROINumber] == left_lung_roi:
            print('ROI Name:', structures[roi.ReferencedROINumber], roi.ReferencedROINumber)
            contour_seq = roi.ContourSequence
            contour_list = []
            for c in contour_seq:
                if c.ContourImageSequence[0].ReferencedSOPInstanceUID == uid:
                    contour_list.append(c)
                    print("OK!")
            if len(contour_list) >= 1:
                return contour_list

def find_roi_name(dataset):
    if 'IPSI' in dataset:     
        return 'LUNG_IPSI'
    elif 'CNTR' in dataset:   
        return 'LUNG_CNTR'
    elif 'LUNG1' in dataset:  
        return 'Lung-Left'
    elif 'LCTSC' in dataset:  
        return 'Lung_L'
    
    except ValueError:
        raise ValueError("unknown dataset")


def save_image_array(img_arr, target_path):
    img = Image.fromarray(img_arr.astype(np.uint8))
    img.save(target_path)
    return img


def normalize_intensity(img):
    img[img < HOUNSFIELD_MIN] = HOUNSFIELD_MIN
    img[img > HOUNSFIELD_MAX] = HOUNSFIELD_MAX
    return (img - HOUNSFIELD_MIN) / HOUNSFIELD_RANGE


def save_images_to_files(plt, subdir, imgarr, contour_mask, dicom_file, output_dir = 'val-output'):
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
