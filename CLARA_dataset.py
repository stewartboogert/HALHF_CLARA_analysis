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

    def load_images_for_step(self , camera , step_no = 0 , ):

        im_file_names = self.file['Dataset']['step_' + f'{step_no}'.zfill(3)][camera][()]
        if im_file_names.decode('utf-8') == 'FAIL':
            return [np.nan]
        
        else:
            im_file = h5py.File(self.image_dir + im_file_names.decode('utf-8') + '_mask.hdf', 'r')
            ims = [im_file[key][()] for key in im_file.keys()]

            return ims
    
    def load_scopes_for_step(self , scope , step_no = 0 , channel = 'Channel1'):
        
        scope_file_names = self.file['Dataset/step_' + f'{step_no}'.zfill(3) + f'/{scope}'][()]
    
        scope_file = h5py.File(self.scope_dir + scope_file_names.decode('utf-8'), 'r')

        scope_data = scope_file[channel]['Segments'][()]

        return list(scope_data)

    def load_data_for_step(self , cameras = [] , scopes = [] , step_no = 0):
        
        data = pd.DataFrame()

        # load images
        for camera in cameras:
            ims = self.load_images_for_step(camera , step_no = step_no)
            data[camera] = ims

        # load scopes
        for scope in scopes:
            scope_data = self.load_scopes_for_step(scope , step_no=step_no)
            data[scope] = scope_data

        step_values = []
        for scan_parameter in self.scan_parameters:
            step_values.append(self.file['Dataset/' + 'step_' + f'{step_no}'.zfill(3) + f'/Scan Parameters/{scan_parameter}'][()])

        if len(self.scan_parameters) != 0:
            data[self.scan_parameters[0]] = step_values[0]

        return data
    
    def load_data(self , cameras = [] , scopes = []):

        datas = []
        for step_no in range(len(self.file['Dataset'].keys())):
            datas.append(self.load_data_for_step(cameras , scopes , step_no))

        datas = pd.concat(datas)
        datas = datas.reset_index(drop=True)
        return datas