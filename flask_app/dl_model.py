import torch
import torch.nn as nn
import torch.nn.functional as F
import torchaudio
import torchaudio.transforms as T
from torchvision import datasets, models, transforms


class raga_resnet(nn.Module):
    def __init__(self, device, num_ragas = 2):
        super(raga_resnet, self).__init__()
        model_ft = models.resnet18(pretrained=True)
#         model_ft = models.resnet50(pretrained=False)
        num_ftrs = model_ft.fc.in_features
        model_ft.fc = nn.Linear(num_ftrs, num_ragas)
        self.model = model_ft
        self.device = device
        # output sample rate from pitch shift
        self.sample_rate = 44100
        self.mel_model = torch.nn.Sequential(
                T.MelSpectrogram(sample_rate = self.sample_rate, n_mels = 24, n_fft = 2048),
                T.AmplitudeToDB())

    def forward(self, x):
        d = torch.zeros((x.shape[0], 1, 24, 1292)).to(self.device)
        for i in range(x.shape[0]):
#             print('mel', self.mel_model(x[i,:,:]).shape)
            d[i,:,:,:] = self.mel_model(x[i,:,:])
        x = d.repeat(1,3,1,1)
        x = self.model(x)
        return x
