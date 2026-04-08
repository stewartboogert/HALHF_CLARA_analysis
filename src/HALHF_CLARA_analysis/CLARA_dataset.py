import pandas as pd
import h5py
import numpy as np

class CLARADataset:

    def __init__(self , filepath , image_dir = r'\\claraserv3.dl.ac.uk\CameraImages\2026\4\1\\' , scope_dir =r'\\fed.cclrc.ac.uk\Org\NLab\ASTeC\Projects\VELA\Work\2026\04\01\\' ):

        self.filepath = filepath

        self.file = h5py.File(self.filepath , 'r')
        self.image_dir = image_dir
        self.scope_dir = scope_dir

        self.scan_parameters = list(self.file['Settings/Scan Parameters'].keys())
        self.snapshot_data_list = list(self.file['Settings/Snapshot Datalist'].keys())
        self.data_list = list(self.file['Settings/Data Collection List'].keys())
        

    def load_images_for_step(self , camera , step_no = 0 , use_full_images = False):

        im_file_names = self.file['Dataset']['step_' + f'{step_no}'.zfill(3)][camera][()]
        if im_file_names.decode('utf-8') == 'FAIL':
            return [np.nan]
        
        else:
            if use_full_images:
                im_file = h5py.File(self.image_dir + im_file_names.decode('utf-8') + '_full.hdf', 'r')
            else:
                im_file = h5py.File(self.image_dir + im_file_names.decode('utf-8') + '_mask.hdf', 'r')
 
            ims = [im_file[key][()] for key in im_file.keys()]

            return ims
    
    def load_scopes_for_step(self , scope , step_no = 0 , channel = 'Channel1'):
        
        scope_file_names = self.file['Dataset/step_' + f'{step_no}'.zfill(3) + f'/{scope}'][()]
    
        scope_file = h5py.File(self.scope_dir + scope_file_names.decode('utf-8'), 'r')

        scope_data = scope_file[channel]['Segments'][()]

        return list(scope_data)
    
    def load_scalars_for_step(self , scalar , step_no = 0):
        return self.file['Dataset/step_' + f'{step_no}'.zfill(3) + f'/{scalar}'][()]

    def load_data_for_step(self , cameras = [] , scopes = [] , scalars = [] , step_no = 0):
        
        data = pd.DataFrame()

        # load images
        for camera in cameras:
            ims = self.load_images_for_step(camera , step_no = step_no)
            data[camera] = ims

        # load scopes
        for scope in scopes:
            scope_data = self.load_scopes_for_step(scope , step_no=step_no)
            data[scope] = scope_data

        # load scalars
        for scalar in scalars:
            scalar_data = self.load_scalars_for_step(scalar , step_no=step_no)
            data[scalar] = scalar_data

        step_values = []
        for scan_parameter in self.scan_parameters:
            step_values.append(self.file['Dataset/' + 'step_' + f'{step_no}'.zfill(3) + f'/Scan Parameters/{scan_parameter}'][()])

        if len(self.scan_parameters) != 0:
            data[self.scan_parameters[0]] = step_values[0]

        return data
    
    def load_data(self , cameras = [] , scopes = [] , scalars = []):

        datas = []
        for step_no in range(len(self.file['Dataset'].keys())):
            datas.append(self.load_data_for_step(cameras , scopes , scalars , step_no))

        datas = pd.concat(datas)
        datas = datas.reset_index(drop=True)
        return datas
    
    def load_snapshot_data(self , where = 'START'):
        snapshot_data = {}
        for name in self.snapshot_data_list:
            if 'QUAD' in name:
                snapshot_data[name + '_READI'] = [self.file[f'Snapshots/{where}/{name}'][name]['READI'][()]]
            else:
                snapshot_data[name] = [self.file[f'Snapshots/{where}/{name}'][()]]

        return pd.DataFrame(snapshot_data)
    
    def load_snapshot_data_all_steps(self):
        snapshot_data = []
        for step_no in range(len(self.file['Dataset'].keys())):
            snapshot_data.append(self.load_snapshot_data('STEP_' + f'{step_no}'.zfill(3)))

        return pd.concat(snapshot_data)
