import os.path as op
import numpy as np
import nibabel as nib
import dipy.data as dpd
import json
from dipy.data import fetcher
from dipy.io.gradients import read_bvals_bvecs
from dipy.core.gradients import gradient_table

import AFQ.utils.streamlines as aus
import AFQ.data as afd
import AFQ.tractography as aft
import AFQ.registration as reg
import AFQ.dti as dti
import AFQ.segmentation as seg
import os

def main():
	with open('config.json') as config_json:
	    config = json.load(config_json)

	#Paths to data
	data_file = str(config['data_file'])
	data_bval = str(config['data_bval'])
	data_bvec = str(config['data_bvec'])

	img = nib.load(data_file)
	
	"""
	print("Calculating DTI...")
	if not op.exists('./dti_FA.nii.gz'):
	    dti_params = dti.fit_dti(data_file, data_bval, data_bvec, out_dir='.')
	else:
	    dti_params = {'FA': './dti_FA.nii.gz',
			  'params': './dti_params.nii.gz'}
	"""
	#tg = nib.streamlines.load('track.trk').tractogram
	
	tg = nib.streamlines.load(config['tck_data']).tractogram
	streamlines = tg.apply_affine(np.linalg.inv(img.affine)).streamlines

	# Use only a small portion of the streamlines, for expedience:
	#streamlines = streamlines[::100]

	templates = afd.read_templates()
	bundle_names = ["CST", "ILF"]

	bundles = {}
	for name in bundle_names:
	    for hemi in ['_R', '_L']:
		bundles[name + hemi] = {'ROIs': [templates[name + '_roi1' + hemi],
			                         templates[name + '_roi1' + hemi]],
			                'rules': [True, True]}


	print("Registering to template...")
	if not op.exists('mapping.nii.gz'):
        	gtab = dpg.gradient_table(hardi_fbval, hardi_fbvec)
    	    	mapping = reg.syn_register_dwi(hardi_fdata, gtab)
            	reg.write_mapping(mapping, './mapping.nii.gz')
	else:
    	    	mapping = reg.read_mapping('./mapping.nii.gz', img, MNI_T2_img)
	
	"""
	MNI_T2_img = dpd.read_mni_template()
	bvals, bvecs = read_bvals_bvecs(data_bval, data_bvec)
	gtab = gradient_table(bvals, bvecs, b0_threshold=100)
	mapping = reg.syn_register_dwi(data_file, gtab)
	reg.write_mapping(mapping, './mapping.nii.gz')
	"""

	print("Segmenting fiber groups...")
	fiber_groups = seg.segment(data_file,
			           data_bval,
			           data_bvec,
			           streamlines,
			           bundles,
			           reg_template=MNI_T2_img,
			           mapping=mapping,
			           as_generator=False,
				   affine = img.affine)
	
	path = os.getcwd() + '/tract1/'
        if not os.path.exists(path):
        	os.makedirs(path)
	
	for fg in fiber_groups:
	    	streamlines = fiber_groups[fg]
		fname = fg + ".tck"
		trg = nib.streamlines.Tractogram(streamlines, affine_to_rasmm=img.affine)
    		nib.streamlines.save(trg,path+fname)


main()
