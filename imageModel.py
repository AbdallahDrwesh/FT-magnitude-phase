import cv2
import numpy as np
from modesEnum import Modes
import logging
logger = logging.getLogger()
class ImageModel:

    def __init__(self, img_data=0, url=None):
        logger.debug('Creating object of  ImageModel')
        if url is not None:
            self.img_data = cv2.imread(url, cv2.IMREAD_GRAYSCALE)
        else:
            self.img_data = img_data
        self.img_fft = np.fft.fft2(self.img_data)
        self.magnitude = np.abs(self.img_fft)
        self.phase = np.angle(self.img_fft)
        self.real = self.img_fft.real
        self.imaginary = self.img_fft.imag

        self.attrs = [np.abs(np.fft.fftshift(self.img_fft)), self.phase, self.img_fft.real, self.img_fft.imag]

    def mix(self, imageToBeMixed: 'ImageModel', magnitudeOrRealRatio: float, phaesOrImaginaryRatio: float, mode: 'Modes') -> np.ndarray:
        """
        a function that takes ImageModel object mag ratio, phase ration
        """
        #  here I add another if conditions and modes according to the GUI
        if imageToBeMixed is not None:  # Two images
            if mode == Modes.magnitudeAndPhase:
                mag = magnitudeOrRealRatio * self.magnitude + (1 - magnitudeOrRealRatio) * imageToBeMixed.magnitude
                phase = phaesOrImaginaryRatio * self.phase + (1 - phaesOrImaginaryRatio) * imageToBeMixed.phase
                exp = np.exp(1j * phase)
                mix = mag * exp
            elif mode == Modes.uniform_mag:
                mag = 1
                phase = phaesOrImaginaryRatio * self.phase + (1 - phaesOrImaginaryRatio) * imageToBeMixed.phase
                exp = np.exp(1j * phase)
                mix = mag * exp
            elif mode == Modes.uniform_phase:
                mag = magnitudeOrRealRatio * self.magnitude + (1 - magnitudeOrRealRatio) * imageToBeMixed.magnitude
                phase = 0
                exp = np.exp(1j * phase)
                mix = mag * exp
            elif mode == Modes.uniform_mag_phase:
                mag = 1
                phase = 0
                exp = np.exp(1j * phase)
                mix = mag * exp * np.ones(self.img_data.shape)
            else:
                real = magnitudeOrRealRatio * self.real + (1 - magnitudeOrRealRatio) * imageToBeMixed.real
                imag = 1j * (phaesOrImaginaryRatio * self.imaginary + (1 - phaesOrImaginaryRatio) * imageToBeMixed.imaginary)
                mix = real + imag
        else:
            if mode == Modes.magnitudeAndPhase:
                mag = magnitudeOrRealRatio * self.magnitude
                phase = phaesOrImaginaryRatio * self.phase
                exp = np.exp(1j * phase)
                mix = mag * exp
            elif mode == Modes.uniform_mag:
                mag = magnitudeOrRealRatio
                phase = phaesOrImaginaryRatio * self.phase
                exp = np.exp(1j * phase)
                mix = mag * exp
            elif mode == Modes.uniform_phase:
                mag = magnitudeOrRealRatio * self.magnitude
                phase = 0
                exp = np.exp(1j * phase)
                mix = mag * exp
            elif mode == Modes.uniform_mag_phase:
                mag = magnitudeOrRealRatio
                phase = 0
                exp = np.exp(1j * phase)
                mix = mag * exp * np.ones(self.img_data.shape)
            else:
                real = magnitudeOrRealRatio * self.real
                imag = 1j * (phaesOrImaginaryRatio * self.imaginary)
                mix = real + imag

        return np.fft.ifft2(mix).real

