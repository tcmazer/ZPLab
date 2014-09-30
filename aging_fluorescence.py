from collections import defaultdict
import numpy
from pathlib import Path
import re
import skimage.io as skio

def process_masks(directory):
    directory = Path(directory)
    control_lums = defaultdict(int)
    control_counts = defaultdict(int)
    exp_lums = defaultdict(int)
    exp_counts = defaultdict(int)
    il_bg_references = {
        'FITC'    : skio.imread('/Volumes/scopearray/aging_fluorescence_9_25_14/references/aging_fluorescence_control_0000_FITC.png').astype(numpy.float64),
        'CFP'     : skio.imread('/Volumes/scopearray/aging_fluorescence_9_25_14/references/aging_fluorescence_control_0000_CFP.png').astype(numpy.float64),
        'TRITC'   : skio.imread('/Volumes/scopearray/aging_fluorescence_9_25_14/references/aging_fluorescence_control_0000_TRITC.png').astype(numpy.float64),
        'DAPI'    : skio.imread('/Volumes/scopearray/aging_fluorescence_9_25_14/references/aging_fluorescence_control_0000_DAPI.png').astype(numpy.float64),
        'YFP'     : skio.imread('/Volumes/scopearray/aging_fluorescence_9_25_14/references/aging_fluorescence_control_0000_YFP.png').astype(numpy.float64),
        'mCherry' : skio.imread('/Volumes/scopearray/aging_fluorescence_9_25_14/references/aging_fluorescence_control_0000_mCherry.png').astype(numpy.float64)
    }
    for mask_fpath in directory.glob('*_Mask*.png'):
        if re.search(r'/\._aging_', str(mask_fpath)) is None:
            mask = (skio.imread(str(mask_fpath)) == 0)
            match = re.match(r'aging_fluorescence_(control|exp)_(\d{4})_Mask-.+\.png', mask_fpath.name)
            image_set = match.group(1)
            image_number = match.group(2)
            for fluo_image_fpath in directory.glob('*{}_{}*.png'.format(image_set, image_number)):
                if re.search(r'/\._aging_', str(fluo_image_fpath)) is None and re.search(r'\d{4}_(Mask-|bf-)[^.]+\.png$', str(fluo_image_fpath)) is None:
                    match = re.search(r'\d{4}_([^.]+)\.png$', str(fluo_image_fpath))
                    image_type = match.group(1)
                    if image_set == 'control':
                        lums = control_lums
                        counts = control_counts
                    else:
                        lums = exp_lums
                        counts = exp_counts
                    lum = (skio.imread(str(fluo_image_fpath)).astype(numpy.float64) / il_bg_references[image_type])[mask]
                    lum = lum[~numpy.isnan(lum)].sum()
                    lums[image_type] += lum
                    counts[image_type] += int(mask.sum())
                    print('{} (number {}, set {}, type {}): {}'.format(fluo_image_fpath, int(image_number), image_set, image_type, lum))
    return control_lums, control_counts, exp_lums, exp_counts

def get_mean_masked_pixel_intensities(control_lums, control_counts, exp_lums, exp_counts):
    mean_control_lums = {}
    mean_exp_lums = {}
    for image_type, lum in control_lums.items():
        mean_control_lums[image_type] = lum / control_counts[image_type]
    for image_type, lum in exp_lums.items():
        mean_exp_lums[image_type] = lum / exp_counts[image_type]
    return mean_control_lums, mean_exp_lums