import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.utils.data import Dataset


class ClassificationNetwork(nn.Module):
    data_nature = None
    def __init__(self, nb_labels):
        super(ClassificationNetwork, self).__init__()
        self.nb_label = nb_labels


    def forward(self, x):
        raise NotImplementedError


class NetConv1D(ClassificationNetwork):
    data_nature = '1D'
    def __init__(self, nb_labels):
        super(NetConv1D, self).__init__(nb_labels)
        self.conv1 = nn.Conv1d(1, 128, 80, 4)
        self.bn1 = nn.BatchNorm1d(128)
        self.pool1 = nn.MaxPool1d(4)
        self.conv2 = nn.Conv1d(128, 128, 3)
        self.bn2 = nn.BatchNorm1d(128)
        self.pool2 = nn.MaxPool1d(4)
        self.conv3 = nn.Conv1d(128, 256, 3)
        self.bn3 = nn.BatchNorm1d(256)
        self.pool3 = nn.MaxPool1d(4)
        self.conv4 = nn.Conv1d(256, 512, 3)
        self.bn4 = nn.BatchNorm1d(512)
        self.pool4 = nn.MaxPool1d(4)
        self.conv5 = nn.Conv1d(512, 1024, 3)
        self.bn5 = nn.BatchNorm1d(1024)
        self.pool5 = nn.MaxPool1d(6)
        self.avgPool = nn.AvgPool1d(
            30
        )  # input should be 512x30 so this outputs a 512x1
        self.fc1 = nn.Linear(1024, nb_labels)

    def forward(self, x):
        x = self.conv1(x)
        x = F.relu(self.bn1(x))
        x = self.pool1(x)
        x = self.conv2(x)
        x = F.relu(self.bn2(x))
        x = self.pool2(x)
        x = self.conv3(x)
        x = F.relu(self.bn3(x))
        x = self.pool3(x)
        x = self.conv4(x)
        x = F.relu(self.bn4(x))
        x = self.pool4(x)
        x = self.conv5(x)
        x = F.relu(self.bn5(x))
        x = self.pool5(x)
        x = self.avgPool(x)
        x = x.view(x.shape[0], -1)  # from shape (bs,channel,len)  to (bs,len)
        x = self.fc1(x)
        return F.log_softmax(x, dim=1)
