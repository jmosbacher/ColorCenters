import numpy as np
import math
import os
from oct2py import octave as oc




def wl_to_rgb(wl):
    select = np.select
    # power=np.power
    # transpose=np.transpose
    arange = np.arange

    def factor(wl):
        return select(
            [ wl > 700.,
              wl < 420.,
              True ],
            [ .3+.7*(780.-wl)/(780.-700.),
              .3+.7*(wl-380.)/(420.-380.),
              1.0 ] )

    def raw_r(wl):
        return select(
            [ wl >= 580.,
              wl >= 510.,
              wl >= 440.,
              wl >= 380.,
              True ],
            [ 1.0,
              (wl-510.)/(580.-510.),
              0.0,
              (wl-440.)/(380.-440.),
              0.0 ] )

    def raw_g(wl):
        return select(
            [ wl >= 645.,
              wl >= 580.,
              wl >= 490.,
              wl >= 440.,
              True ],
            [ 0.0,
              (wl-645.)/(580.-645.),
              1.0,
              (wl-440.)/(490.-440.),
              0.0 ] )

    def raw_b(wl):
        return select(
            [ wl >= 510.,
              wl >= 490.,
              wl >= 380.,
              True ],
            [ 0.0,
              (wl-510.)/(490.-510.),
              1.0,
              0.0 ] )

    gamma = 0.80
    def correct_r(wl):
        return math.pow(factor(wl)*raw_r(wl),gamma)
    def correct_g(wl):
        return math.pow(factor(wl)*raw_g(wl),gamma)
    def correct_b(wl):
        return math.pow(factor(wl)*raw_b(wl),gamma)


    return (correct_r(wl),correct_g(wl),correct_b(wl))


def color_map(wl):
    # ['r', 'g', 'b', 'y', 'g', 'k', 'm', 'c', 'k']
    col = 'b'
    if wl >485:
        col = 'c'
    if wl > 500:
        col = 'g'
    if wl > 565:
        col ='y'
    if wl > 590:
        col = 'm'
    if wl > 625:
        col = 'r'
    return col

def merge_experiments(spectrum1,spectrum2):
    """

    :param spectrum1:
    :param spectrum2:
    :return:
    """

    spectrum1.em_wl = (min(spectrum1.em_wl[0],spectrum2.em_wl[0]),max(spectrum1.em_wl[1],spectrum2.em_wl[1]))
    spectrum1.signal = np.append(spectrum1.signal, spectrum2.signal,axis=0)
    if len(spectrum1.signal):
        spectrum1.has_sig = True
        spectrum1.bg = np.append(spectrum1.bg, spectrum2.bg,axis=0)
    if len(spectrum1.bg):
        spectrum1.has_bg = True
    return spectrum1


def merge_crystals(col1,col2):
    """

    :param col1:
    :param col2:
    :return:
    """
    col1.measurements.extend(col2.experiments)
    return col1


def read_sif_file(path):
    """
    Wrapper for the matlab sif reader
    sifread.m must be same directory as this .py file
    :param path: path to file
    :return: data, background, ref
    """
    localdir = os.path.dirname(os.path.abspath(__file__))
    oc.addpath(localdir)
    return oc.sifread(path)

def read_ascii_file(path, file_del):
    data = []
    with open(path, 'r') as f:
        for line in f:
            if line in ['\n', '\r\n']:
                break
            s = line.split(file_del)
            data.append([eval(s[0]), eval(s[1])])
    if len(data):
        return data
    return None

def organize_data(in_data,tags=('sig','bg','ref')):
    '''
    :param data: Dictionary {file name: data array}
    :param data: text tags to organize by
    :return: Dictionarey {Name: {signal:array, bg:array, ref:array}
    '''

    out = {}

    for name, data in in_data.items():
        for tag in tags:
            if tag in name:
                if name.replace(tag,'') in out.keys():
                    out[name.replace('_' + tag,'')][tag] = data
                else:
                    out[name.replace('_' + tag, '')] = {tag:data}
    return out


