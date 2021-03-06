import numpy as np
from src.preprocessors.Preprocessor import Preprocessor
from src.utility.image_utility import normalize_img


class Normalizer(Preprocessor):

    def __init__(self, title='Normalizer', alpha=0, beta=1):
        Preprocessor.__init__(self, title)
        self.alpha = alpha
        self.beta = beta

    def evaluate(self, value):
        if value.shape[2] == 1:
            normalized = normalize_img(value, self.alpha, self.beta)
            return np.array(normalized)[:, :, np.newaxis]
        else:
            normalized = normalize_img(value, self.alpha, self.beta)
            return normalized
