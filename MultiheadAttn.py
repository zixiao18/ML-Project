#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr  5 11:59:54 2022

@author: wangcatherine
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
import math


# QK'/sqrt(d_k)
def a_norm(Q, K):
    m = torch.matmul(Q, K.transpose(2, 1).float())
    m /= torch.sqrt(torch.tensor(Q.shape[-1]).float())

    return torch.softmax(m, -1)


def attention(Q, K, V):
    # Attention(Q, K, V) = norm(QK)V
    a = a_norm(Q, K)  # (batch_size, dim_attn, seq_length)

    return torch.matmul(a, V)  # (batch_size, seq_length, seq_length)


class AttentionBlock(torch.nn.Module):
    def __init__(self, dim_val, dim_attn):
        super(AttentionBlock, self).__init__()
        self.value = Value(dim_val, dim_val)
        self.key = Key(dim_val, dim_attn)
        self.query = Query(dim_val, dim_attn)

    def forward(self, x, kv=None):
        if kv is None:
            # Attention with x connected to Q,K and V (For encoder)
            return attention(self.query(x), self.key(x), self.value(x))

        # Attention with x as Q, external vector kv as K an V (For decoder)
        return attention(self.query(x), self.key(kv), self.value(kv))


class MultiHeadAttentionBlock(torch.nn.Module):
    def __init__(self, dim_val, dim_attn, n_heads):
        super(MultiHeadAttentionBlock, self).__init__()
        self.heads = []
        for _ in range(n_heads):
            self.heads.append(AttentionBlock(dim_val, dim_attn))
        print(self.heads)
        self.heads = nn.ModuleList(self.heads)

        self.fc = nn.Linear(n_heads * dim_val, dim_val, bias=False)

    def forward(self, x, kv=None):
        a = []
        for h in self.heads:
            a.append(h(x, kv=kv))
        # combine heads, each head size = input data size
        a = torch.stack(a, dim=-1)
        a = a.flatten(start_dim=2)  # flatten all head outputs

        x = self.fc(a)

        return x


class Value(torch.nn.Module):
    def __init__(self, dim_input, dim_val):
        super(Value, self).__init__()
        self.dim_val = dim_val

        self.fc1 = nn.Linear(dim_input, dim_val, bias=False)
        # self.fc2 = nn.Linear(5, dim_val)

    def forward(self, x):
        x = self.fc1(x)
        # x = self.fc2(x)

        return x


class Key(torch.nn.Module):
    def __init__(self, dim_input, dim_attn):
        super(Key, self).__init__()
        self.dim_attn = dim_attn

        self.fc1 = nn.Linear(dim_input, dim_attn, bias=False)
        # self.fc2 = nn.Linear(5, dim_attn)

    def forward(self, x):
        x = self.fc1(x)
        # x = self.fc2(x)

        return x


class Query(torch.nn.Module):
    def __init__(self, dim_input, dim_attn):
        super(Query, self).__init__()
        self.dim_attn = dim_attn

        self.fc1 = nn.Linear(dim_input, dim_attn, bias=False)
        # self.fc2 = nn.Linear(5, dim_attn)

    def forward(self, x):
        x = self.fc1(x)
        # print(x.shape)
        # x = self.fc2(x)

        return x


# testing
if __name__ == "__main__":
    attn = MultiHeadAttentionBlock(4, 2, 2)

    print(attn(torch.randn(2, 5, 4)).shape)
