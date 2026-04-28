import glob as _glob
import pathlib as _pathlib
import h5py as _h5py
import shutil as _shutil
import numpy as _np

from .CLARA_dataset import CLARADataset

class CLARA_datamanager :

    def __init__(self, path):
        self.path = path

    def check_and_partition_files(self, output_dir = "./"):
        # glob MultiSourceDAQ*
        files = _glob.glob(self.path + 'MultiSourceDAQ*')

        # make output dir
        output_path = _pathlib.Path(output_dir).absolute()
        print(output_path)
        output_path.mkdir(exist_ok=True)


        summary_info = {}
        summary_info['filename'] = []
        summary_info['check_comment'] = []
        summary_info['check_dataset'] = []
        summary_info['check_setting'] = []
        summary_info['check_snapshots'] = [] 
        summary_info['comment'] = []
        summary_info['check_scan'] = []
        summary_info['scan_parameter'] = []

        # loop over files
        for f in files :

            file_path = _pathlib.Path(f)

            print("Processing", f, file_path.stem)
            date = file_path.stem.split("_")[1]
            time = file_path.stem.split("_")[2]

            # Create output path for scan/run
            file_merged_path = output_path/_pathlib.Path(str(date)+"_"+str(time))
            file_merged_path.mkdir(exist_ok=True)

            # load data set
            dataset = CLARADataset(f, image_dir = str(self.path))

            # check if Comment, Dataset, Setttings, Snapshots is present in the file    
            check_comment = self._checkkey(dataset.file, "Comment")
            check_dataset = self._checkkey(dataset.file, "Dataset")
            check_settings = self._checkkey(dataset.file, "Settings")
            check_snapshots = self._checkkey(dataset.file, "Snapshots")

            print(f"Check primary keys> Comment: {check_comment} Dataset: {check_dataset} Settings: {check_settings} Snapshots: {check_snapshots}")

            # get comment 
            comment = dataset.file['Comment'][()].decode()
            print(f"Comment: {comment}")

            # get scan parameters  
            check_scan = False 
            scan_parameter = "None" 
            scan_points = [0] 
        
            scan_parameters = dataset.file['Settings/Scan Parameters']
            if len(scan_parameters.keys()) > 0 :
                check_scan = True
                scan_parameter = list(scan_parameters.keys())[0]
                scan_points = scan_parameters[scan_parameter].attrs['pointarray']
                check_scan = True

            # get number of pulses per scan  point 
            scan_pulses_per_point = dataset.file['Settings/Collection Size'][()]

            # parameters of scan
            scan_range_min = _np.array(scan_points).min()
            scan_range_max = _np.array(scan_points).max()
            scan_range_size = len(scan_points)


            print(scan_parameter, scan_range_min, scan_range_max, scan_range_size, scan_pulses_per_point)

            # Copy over main data file
            _shutil.copy2(file_path, file_merged_path / file_path.name)


            # dict of all the PVs which are pointers to another file
            files_dict = {}
       
            # Go to next file if dataset not present
            if not check_dataset :
                continue 

            # loop over keys in hdf file and move files
            for step_key in dataset.file['Dataset'].keys() :
                for data_key in dataset.file['Dataset'][step_key].keys() :
                    d = dataset.file['Dataset'][step_key][data_key]
                    if data_key == "Scan Parameters" :
                        continue

                    if isinstance(d[()],bytes):
                        # gather up file names
                        if data_key not in files_dict :
                            files_dict[data_key] = []
                        
                        files_dict[data_key].append(d[()].decode())
                        
                        # ok should be a file so move it
                        cam_scope_file = _pathlib.Path(self.path)/_pathlib.Path(d[()].decode())
                        cam_scope_files = _glob.glob(str(cam_scope_file)+"*")

                        for cam_scope_file in cam_scope_files :
                            cam_scope_file_path = _pathlib.Path(cam_scope_file)
                            try :
                                _shutil.copy2(cam_scope_file_path, file_merged_path / cam_scope_file_path.name)
                            except PermissionError :
                                pass

            print(files_dict)
 

            print()

    def _checkkey(self, file, key) :
        try: 
            file[key]
            return True
        except :
            return False 

