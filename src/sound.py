import os
from pathlib import Path

import librosa  # Librosa for audio
import librosa.display  # and the display module for visualization
import librosa.util
import matplotlib.pyplot as plt
import numpy as np


class Sound:
    """
    Basic class to deal with sounds.
    """

    class SpectrogramNotComputed(Exception):
        pass

    def __init__(
            self,
            path: Path = None,
            sampling_rate: int = None,
            process: bool = True,
    ):
        self.path = path
        self.folder, self.filename = path.parent, path.name
        self.filebase, self.ext = os.path.splitext(self.filename)
        self.y, self.sampling_rate = librosa.load(self.path, sr=sampling_rate)
        self.spectrogram = None

        if process:
            self.spectrogram = self.compute_spectrogram()

    def compute_spectrogram(self, n_mels: int = 256):
        """
        Args:
            n_mels: vertical resolution of the spectrogram
        Returns:
            Melspectrogram on a log scale
        """
        return librosa.power_to_db(
            librosa.feature.melspectrogram(
                self.y, sr=self.sampling_rate, n_mels=n_mels
            ),
            ref=np.max,
        )  # convert to log scale (dB). Use the peak power (max) as ref

    def plot_spectrogram(self, ax=None):
        if self.spectrogram is None:
            raise Sound.SpectrogramNotComputed(
                'please call compute_spectrogram() to compute the '
                'sound spectrogram before trying to plot it'
            )
        ax = plt.gca() if ax is None else ax
        librosa.display.specshow(
            self.spectrogram,
            sr=self.sampling_rate,
            x_axis='time',
            y_axis='mel',
            ax=ax,
        )
        ax.set_title('mel power spectrogram')

    def to_samples(
            self,
            sample_length: float = 4,
            mode: str = 'duplicate',
            output_folder: str = None,
            suffix: str = 'sample',
    ):
        """
        Take the sound in self.y and split in into samples of size sample_size.

        Args:
            mode(str, optional):
                'duplicate' (default)
                    Add a  part from the previous sample to make the last
                    one of equal size
                'drop'
                    Drop last sample.
                'keep'
                    Keep last sample from an (unknown size)


            sample_length: length of each sample in seconds.
            output_folder: Folder where samples are saved.
            suffix: String add at the end of the files.
        """

        if output_folder is None:
            output_folder = self.folder
        step_size = int(sample_length * self.sampling_rate)
        i = 0
        n = len(self.y)

        def save(i, suffix, y):
            librosa.output.write_wav(
                Path(output_folder / f'{self.filebase}_{i}_{suffix}.wav'),
                y,
                sr=self.sampling_rate,
                norm=False,
            )

        if n < step_size:  # sound is smaller than required sample size
            # print(' short', np.pad(self.y, (0, step_size - n)).shape)
            save(0, suffix, np.pad(self.y, (0, step_size - n)))
        else:
            for i in range(n // step_size):
                save(0, suffix, self.y[i * step_size: (i + 1) * step_size])
            if (n % step_size != 0):  # handling of last sample
                i = n // step_size
                if mode == 'drop':
                    pass
                elif mode == 'duplicate':
                    save(0, suffix, self.y[n - step_size: n])
                elif mode == 'keep':
                    save(0, suffix, self.y[i * step_size: n])


if __name__ == '__main__':
    folder = Path('../data/urban/processed_1D/talk')
    for file in folder.glob('*.wav'):
        print(file)
        s1 = Sound(file, process=False, sampling_rate=None)
        # s1.plot_spectrogram()
        # plt.show()
        print(s1.y.shape)
        print(s1.sampling_rate)
        # s1.to_samples(sample_length=4, mode='duplicate')
