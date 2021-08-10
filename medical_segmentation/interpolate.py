import SimpleITK as sitk
import numpy as np


def sitk_interpolation(path_to_nrrd, interpolation_type, new_spacing, mask):
    data = sitk.ReadImage(path_to_nrrd)

    original_spacing = data.GetSpacing()
    original_size = data.GetSize()
    logging.debug('{} {}'.format('original size: ', original_size))
    logging.debug('{} {}'.format('original spacing: ', original_spacing))

    new_size = [int(round((original_size[0]*original_spacing[0])/float(new_spacing[0]))),
                int(round((original_size[1]*original_spacing[1])/float(new_spacing[1]))),
                int(round((original_size[2]*original_spacing[2])/float(new_spacing[2])))]

    logging.debug('{} {}'.format('new size: ', new_size))

    # http://insightsoftwareconsortium.github.io/SimpleITK-Notebooks/Python_html/20_Expand_With_Interpolators.html
    if interpolation_type == 'linear':
        interpolation_type = sitk.sitkLinear
    elif interpolation_type == 'bspline':
        interpolation_type = sitk.sitkBSpline
    elif interpolation_type == 'nearest_neighbor':
        interpolation_type = sitk.sitkNearestNeighbor

    if mask:
      interpolation_type = sitk.sitkNearestNeighbor

    resampleImageFilter = sitk.ResampleImageFilter()
    new_image = resampleImageFilter.Execute(data,
                                            new_size,
                                            sitk.Transform(),
                                            interpolation_type,
                                            data.GetOrigin(),
                                            [float(x) for x in new_spacing],
                                            data.GetDirection(),
                                            0,
                                            data.GetPixelIDValue())
    new_image.SetSpacing(new_spacing)

    new_array = sitk.GetArrayFromImage(new_image)

    if not mask:
      new_array = normalize_intensity(new_array)

    x, y = new_array.shape[1], new_array.shape[2]
    while new_array.shape[0] % 16 != 0:
      new_array = np.vstack([np.zeros((1, x, y)), new_array])
    
    z, y = new_array.shape[0], new_array.shape[2]
    while new_array.shape[1] % 16 != 0:
      new_array = np.concatenate([np.zeros((z, 1, y)), new_array], axis=1)

    z, x = new_array.shape[0], new_array.shape[1]
    while new_array.shape[2] % 16 != 0:
      new_array = np.concatenate([np.zeros((z, x, 1)), new_array], axis=2)


    processedSitk = sitk.GetImageFromArray(new_array)
    processedSitk.SetSpacing(new_spacing)
    processedSitk.SetDirection(new_image.GetDirection())
    processedSitk.SetOrigin(new_image.GetOrigin())

    logging.debug("new dims", new_array.shape)
    return processedSitk

def interpolate(dataset, patient_id, data_type, path_to_nrrd, interpolation_type, new_spacing, return_type, image_type, output_dir = "", mask=False):
    """
    Interpolates a given nrrd file to a given voxel spacing.
    Args:
        dataset (str): Name of dataset.
        patient_id (str): Unique patient id.
        data_type (str): Type of data (e.g., ct, pet, mri, lung(mask), heart(mask)..)
        path_to_nrrd (str): Path to nrrd file.
        interpolation_type (str): Either 'linear' (for images with continuous values), 'bspline' (also for images but will mess up the range of the values), or 'nearest_neighbor' (for masks with discrete values).
        new_spacing (tuple): Tuple containing 3 values for voxel spacing to interpolate to: (x,y,z).
        return_type (str): Either 'sitk_object' or 'numpy_array'.
        output_dir (str): Optional. If provided, nrrd file will be saved there. If not provided, file will not be saved.
    Returns:
        Either a sitk image object or a numpy array derived from it (depending on 'return_type').
    Raises:
        Exception if an error occurs.
    """
    try:
        new_sitk_object = sitk_interpolation(path_to_nrrd, interpolation_type, new_spacing, mask)
        if output_dir != "":
            # write new nrrd
            try:
              os.mkdir(output_dir)
            except:
              logging.debug("directory already exists")
              
            writer = sitk.ImageFileWriter()
            writer.SetFileName(os.path.join(output_dir, "{}.nrrd".format(image_type)))
            writer.SetUseCompression(True)
            writer.Execute(new_sitk_object)

        if return_type == "sitk_object":
            return new_sitk_object
        elif return_type == "numpy_array":
            return sitk.GetArrayFromImage(new_sitk_object)

    except Exception as e:
        logging.debug("Error in {}_{}, {}".format(dataset, patient_id, e))
