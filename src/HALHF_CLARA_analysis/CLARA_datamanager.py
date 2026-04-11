import glob as _glob
import pathlib as _pathlib
import h5py as _h5py
import shutil as _shutil

from .CLARA_dataset import CLARADataset

class CLARADatamanager :

    def __init__(self, path):
        self.path = path

    def check_and_partition_files(self, output_dir = "./"):
        # glob MultiSourceDAQ*
        files = _glob.glob(self.path + 'MultiSourceDAQ*')

        # make output dir
        output_path = _pathlib.Path(output_dir).absolute()
        print(output_path)
        output_path.mkdir(exist_ok=True)


        # loop over files
        for f in files :
            file_path = _pathlib.Path(f)

            print(f, file_path.stem)
            date = file_path.stem.split("_")[1]
            time = file_path.stem.split("_")[2]

            # Create output path for scan/run
            file_merged_path = output_path/_pathlib.Path(str(date)+"_"+str(time))
            file_merged_path.mkdir(exist_ok=True)

            # load data set
            dataset = CLARADataset(f, image_dir = str(self.path))

            # Copy over main data file
            _shutil.copy2(file_path, file_merged_path / file_path.name)

            # is there a data set
            try :
                dataset.file['Dataset'].keys()
            except :
                continue

            # loop over keys in hdf file and move files
            for step_key in dataset.file['Dataset'].keys() :
                for data_key in dataset.file['Dataset'][step_key].keys() :
                    # print(step_key, data_key)
                    d = dataset.file['Dataset'][step_key][data_key]
                    if data_key == "Scan Parameters" :
                        continue

                    print(step_key, data_key)
                    if isinstance(d[()],bytes):
                        # ok should be a file so move it
                        cam_scope_file = _pathlib.Path(self.path)/_pathlib.Path(d[()].decode())
                        cam_scope_files = _glob.glob(str(cam_scope_file)+"*")

                        for cam_scope_file in cam_scope_files :
                            cam_scope_file_path = _pathlib.Path(cam_scope_file)
                            try :
                                _shutil.copy2(cam_scope_file_path, file_merged_path / cam_scope_file_path.name)
                            except PermissionError :
                                pass







