import SimpleITK as sitk
from pydicom import dcmread
import numpy as np

def load_dicom(slice_list, split, patient_id):
    metadata = dcmread(os.path.join(split, patient_id, "metadata", '1-1.dcm'))
    slices = []
    mask_arrays = []
    num_with_rois = 0
    for s in slice_list:
        new_slice = pydicom.dcmread(s)
        slices.append(new_slice)

    try:
        # seriesDesc = slices[0].SeriesDescription
        slices.sort(key=lambda x: float(x.ImagePositionPatient[2]))
        try:
            slice_thickness = np.abs(slices[0].ImagePositionPatient[2] - slices[1].ImagePositionPatient[2])
        except:
            slice_thickness = np.abs(slices[0].SliceLocation - slices[1].SliceLocation)
    except Exception as e:
        print (e)
        #print 'No position found for image', slice_list[0]
        return []
    for s in slices:
        s.SliceThickness = slice_thickness

    for new_slice in slices:
      sop_uid = new_slice.SOPInstanceUID
      contour_list = fetch_contour_sop_instance_uid(metadata, sop_uid)
      if len(contour_list) == 0:
          logging.info("Image file SOPInstanceUID %s has no ROI data, using empty mask...", sop_uid)
          contour_mask = np.zeros((512, 512), np.uint8)
      else:
          num_with_rois += 1
          contour_pixels = []
          for c in contour_list:
              contour_coord = c.ContourData
              contour_pixels.extend(contour_to_pixels(contour_coord, new_slice))
          contour_mask = build_mask(contour_pixels)
      mask_arrays.append(contour_mask)

    img_spacing = [float(slices[0].PixelSpacing[0]),
    float(slices[0].PixelSpacing[1]), slice_thickness]
    img_direction = [int(i) for i in slices[0].ImageOrientationPatient] + [0, 0, 1]
    img_origin = slices[0].ImagePositionPatient

    mask = np.stack([m for m in mask_arrays])
    mask = mask.astype(np.int16)

    return slices, img_spacing, img_direction, img_origin, mask


def getPixelArray(slices):
    image = np.stack([s.pixel_array for s in slices])

    # Convert to int16 (from sometimes int16),
    # should be possible as values should always be low enough (<32k)
    image = image.astype(np.int16)

    # Set outside-of-scan pixels to 0
    # The intercept is usually -1024, so air is approximately 0
    image[image == -2000] = 0

    # Convert to Hounsfield units (HU)
    for slice_number in range(len(slices)):
        intercept = slices[slice_number].RescaleIntercept
        slope = slices[slice_number].RescaleSlope
        if slope != 1:
            image[slice_number] = slope * image[slice_number].astype(np.float64)
            image[slice_number] = image[slice_number].astype(np.int16)
        image[slice_number] += np.int16(intercept)
    return np.array(image, dtype=np.int16)


def run_core(dicom_dir, split, patient_id):
    logging.info('Processing patient ', dicom_dir)
    dicomFiles = sorted(glob.glob(dicom_dir + '/*.dcm'))
    dicomFiles = sorted(dicomFiles)
    slices, img_spacing, img_direction, img_origin, mask = load_dicom(dicomFiles, split, patient_id)

    if 0.0 in img_spacing:
        logging.debug('ERROR - Zero spacing found for patient,', seriesID, img_spacing)
        return ''

    imgCube = getPixelArray(slices)

    # Build the SITK nrrd image
    imgSitk = sitk.GetImageFromArray(imgCube)
    imgSitk.SetSpacing(img_spacing)
    imgSitk.SetDirection(img_direction)
    imgSitk.SetOrigin(img_origin)

    maskSitk = sitk.GetImageFromArray(mask)
    maskSitk.SetSpacing(img_spacing)
    maskSitk.SetDirection(img_direction)
    maskSitk.SetOrigin(img_origin)

    return imgSitk, maskSitk


def dcm_to_nrrd(split, dataset, patient_id, data_type, input_dir, output_dir, save=True):
    """
    Converts a stack of slices into a single .nrrd file and saves it.
    Args:
        dataset (str): Name of dataset.
        patient_id (str): Unique patient id.
        data_type (str): Type of data (e.g., ct, pet, mri..)
        input_dir (str): Path to folder containing slices.
        output_dir (str): Path to folder where nrrd will be saved.
        save (bool): If True, the nrrd file is saved
    Returns:
        The sitk image object.
    Raises:
        Exception if an error occurs.
    """
    path = os.path.join(output_dir, patient_id)
    try:
      os.mkdir(path)
    except:
      "folder already created"
    nrrd_name = "image.nrrd"
    mask_name = "mask.nrrd" 
    nrrd_file_path = os.path.join(output_dir, patient_id, nrrd_name)
    nrrd_mask_path = os.path.join(output_dir, patient_id, mask_name)
    sitk_object, mask_object = run_core(input_dir, split, patient_id)
    if save:
        nrrdWriter = sitk.ImageFileWriter()
        nrrdWriter.SetFileName(nrrd_file_path)
        nrrdWriter.SetUseCompression(True)
        nrrdWriter.Execute(sitk_object)

        nrrdWriter = sitk.ImageFileWriter()
        nrrdWriter.SetFileName(nrrd_mask_path)
        nrrdWriter.SetUseCompression(True)
        nrrdWriter.Execute(mask_object)
        
    logging.info("dataset:{} patient_id:{} done!".format(dataset, patient_id))
    return sitk_object, mask_object
    # except Exception as e:
    #     print ("dataset:{} patient_id:{} error:{}".format(dataset, patient_id, e))
