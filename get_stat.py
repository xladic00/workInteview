#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import os
import argparse
from decimal import Decimal
# povolene jsou pouze zakladni knihovny (os, sys) a knihovny numpy, matplotlib a argparse

from download import DataDownloader


def plot_stat(data_source = DataDownloader().get_dict(), fig_location=None, show_figure=False):

    accidents = np.array([])
    for region in data_source:
        template_to_fill = np.zeros(6)
        (unique, counts) = np.unique(region["p24"][1:-1], return_counts=True)
        unique = unique.astype(float)
        template_to_fill[unique.astype(int)] = counts
        if accidents.size == 0:
                accidents = template_to_fill.T
        else:
                accidents = np.column_stack((accidents, template_to_fill))

    rows = ["Žádná úprava", "Přerušovaná žlutá", "Semafor mimo provoz", "Dopravními značkami", "Přenosné dopravní značky", "Nevyznačena"]
    cols = ["PHA", "STC", "JHC", "PLK", "ULK", "HKK", "JHM", "MSK", "OLK", "ZLK", "VYS", "PAK", "LBK", "KVK"]

    accidents = np.ma.masked_where(accidents == 0, accidents) # Mask 0 value data
    fig, axes = plt.subplots(ncols=1, nrows=2, figsize=(4, 8)) # Create figure with 2 subplots
    ax1, ax2 = axes

        # Subplot 1
    # Create colorbar
    im1 = ax1.matshow(accidents, norm=matplotlib.colors.LogNorm(), cmap='viridis')
    cbar1 = fig.colorbar(im1, ax=ax1)
    cbar1.ax.set_ylabel('Počet nehod', rotation=90, va="top")
    cbar1.minorticks_on()

    # Set ticks and labels
    ax1.set_xticks(np.arange(len(cols)))
    ax1.set_yticks(np.arange(len(rows)))
    ax1.xaxis.set_ticks_position('bottom')
    ax1.set_xticklabels(cols)
    ax1.set_yticklabels(rows)
    ax1.set_title("Absolutně")
    plt.setp(ax1.get_xticklabels(), ha="center",
            rotation_mode="anchor")

        # Subplot 2
    accidents_percentage = np.true_divide(accidents, accidents.sum(axis=1, keepdims=True)) * 100 # Adjust data to percentage
    im2 = ax2.matshow(accidents_percentage, cmap='plasma')
    cbar2 = fig.colorbar(im2, ax=ax2) # cbar_kw={}
    cbar2.ax.set_ylabel('Podíl nehod pro danou příčinu [%]', rotation=90, va="top")

    # We want to show all ticks...
    ax2.set_xticks(np.arange(len(cols)))
    ax2.set_yticks(np.arange(len(rows)))
    ax2.xaxis.set_ticks_position('bottom')
    ax2.set_xticklabels(cols)
    ax2.set_yticklabels(rows)
    ax2.set_title("Relativně vůči příčině")
    plt.setp(ax2.get_xticklabels(), ha="center",
            rotation_mode="anchor")


    plt.show()
    return fig

def show_figure(fig):
    #https://stackoverflow.com/questions/31729948/matplotlib-how-to-show-a-figure-that-has-been-closed
    # create a dummy figure and use its
    # manager to display "fig"

    dummy = plt.figure()
    new_manager = dummy.canvas.manager
    new_manager.canvas.figure = fig
    fig.set_canvas(new_manager.canvas)

# TODO pri spusteni zpracovat argumenty
fig = plot_stat()
show_figure(fig)