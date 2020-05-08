from pathlib import Path

import numpy as np
import torch
from torch.utils.data import DataLoader, Dataset
from torchvision import transforms, utils

from sound import Sound


class SoundDataset(Dataset):
    """Sound dataset"""
    DATA_FOLDER = Path(__file__).resolve().parent.parent / 'data'

    class DatasetFolderStructureError(Exception):
        pass

    def __init__(
            self,
            dataset_name,
            transform,
            data_nature='2D',
            sampling_rate=None,
            process_data='Auto',
    ):
        """
        Args:
            dataset_name (string): Directory with all the images.
            transform (callable, optional): Optional transform to be applied
                on a sample.
        """
        self.dataset_name = dataset_name
        self.data_nature = data_nature
        self.sampling_rate = sampling_rate
        self.root_dir = SoundDataset.DATA_FOLDER / dataset_name
        self.raw_dir = self.root_dir / 'raw'
        self.processed_dir = self.root_dir / f'processed'
        if process_data == 'Auto':
            self.process_data = not (self.processed_dir.exists())
        else:
            self.process_data = process_data
        if self.process_data:
            self.make_processing()

        self.files_list = list(self.processed_dir.rglob('*1D.*'))
        self.labels = [
            f.stem for f in self.processed_dir.glob('*/') if f.is_dir()
        ]
        self.nb_labels = len(self.labels)
        self.label_to_num = {label: i for i, label in enumerate(self.labels)}
        self.data_nature = data_nature
        self.transform = transform

    def __len__(self):
        return len(self.files_list)

    def __getitem__(self, idx):
        # if torch.is_tensor(idx):
        #     idx = idx.tolist()
        file = Path(self.files_list[idx])
        label = file.parent.stem  # label is the folder name
        sound = Sound(
            path=file,
            process=False if self.data_nature == '1D' else True,
            sampling_rate=self.sampling_rate,
        )
        spectrogram = np.load(file.parent / f'{file.stem[:-2]}2D.npy')

        sample = {'sound': sound,'spectrogram':spectrogram ,'label':
            self.label_to_num[
            label]}
        sample = self.transform(sample)
        return sample

    def make_processing(self):
        """ Process all the raw data"""
        if not self.root_dir.exists():  # require dataset folder
            raise SoundDataset.DatasetFolderStructureError(
                f'No folder called \'{self.dataset_name}\' found in the '
                f'dataset '
                f'folder{SoundDataset.DATA_FOLDER}'
            )

        if not self.raw_dir.exists():  # require raw data folder
            raise SoundDataset.DatasetFolderStructureError(
                f'To process data, raw data have to be located in \'data'
                f'/{self.dataset_name}/raw/\' '
            )

        self.processed_dir.mkdir(exist_ok=True)

        labels = [f.stem for f in self.raw_dir.glob('*/') if f.is_dir()]
        for label in labels:
            Path(self.processed_dir / label).mkdir(
                exist_ok=True
            )
        # 1D Process
        for file in list(self.raw_dir.rglob('*.wav')):
            sound = Sound(
                file,
                process=False,
                sampling_rate=self.sampling_rate,
            )
            sound.to_samples(
                output_folder=self.processed_dir / file.parent.stem,
                suffix='1D'
            )
        # 2D Process
        for file in list(self.processed_dir.rglob('*1D.wav')):
            sound = Sound(
                file,
                process=True,
                sampling_rate=None,
            )
            np.save(Path(file.parent / f'{file.stem[:-2]}2D.npy'),
                    sound.spectrogram)


class ToTensor(object):
    """Convert ndarrays to Tensors. This class is used as a transform in the
    data loading` """

    class ModeNotRecognised(Exception):
        pass

    def __init__(self, data_nature):
        self.data_nature = data_nature

    def __call__(self, sample):

        sound, label = sample['sound'], sample['label']
        if self.data_nature == '1D':
            return {
                'sound': torch.from_numpy(sound.y).unsqueeze(0),
                'label': label,
            }
        # conv1D expect sample following the shape [bs,nb_channel,lenght]
        elif self.data_nature == '2D':
            return {
                'sound': torch.from_numpy(sound.spectrogram),
                'label': label,
            }
        else:
            raise ToTensor.ModeNotRecognised(
                "Enter a valid value for " "data_nature."
            )
