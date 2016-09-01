import numpy as np
import math
import os
from experiment import SpectrumExperiment
from measurement import SpectrumMeasurement




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

def merge_spectrums(spectrum1,spectrum2):
    """

    :param spectrum1:
    :param spectrum2:
    :return:
    """

    spectrum1.em_wl = (min(spectrum1.em_wl[0],spectrum2.em_wl[0]),max(spectrum1.em_wl[1],spectrum2.em_wl[1]))
    spectrum1.signal = np.append(spectrum1.signal, spectrum2.signal,axis=0)
    if len(spectrum1.bg):
        spectrum1.bg = np.append(spectrum1.bg, spectrum2.bg,axis=0)
    return spectrum1


def merge_crystals(col1,col2):
    """

    :param col1:
    :param col2:
    :return:
    """
    col1.measurements.extend(col2.experiments)
    return col1


def read_ascii_file(path, file_del):
    data = []
    sup = []
    with open(path, 'r') as f:
        sig = True
        for line in f:
            if line in ['\n', '\r\n']:
                sig = False
                continue
            if sig:
                s = line.split(file_del)
                data.append([eval(s[0]), eval(s[1])])
            else:
                sup.append(line)
    if len(data):
        return data, sup
    return None




def organize_data(in_data,tags=('sig','bgd','ref'), ext='.asc'):
    '''
    :param data: Dictionary {file name: data array}
    :param data: text tags to organize by
    :return: Dictionarey {Name: {signal:array, bg:array, ref:array}
    '''

    out = {}
    for name, data in in_data.items():

        for tag in tags:

            if tag in name:
                if name.replace('_' + tag,'').replace(ext, '') in out.keys():
                    out[name.replace('_' + tag,'').replace(ext, '')][tag] = data
                else:
                    out[name.replace('_' + tag, '').replace(ext, '')] = {tag:data}
    return out


def compare_experiments(exp1,exp2,main=None):
    new_exp = SpectrumExperiment(main=main)
    new_exp.name = exp1.name + ' vs ' + exp2.name
    for first in exp1.measurements:
        for second in exp2.measurements:
            if first.ex_wl == second.ex_wl:
                if first.has_signal and second.has_signal:
                    big = first
                    small = second
                    if np.average(second.signal[0, :]) > np.average(first.signal[0, :]):
                        big = second
                        small = first
                    new_meas = SpectrumMeasurement(main=main)
                    new_meas.ex_wl = first.ex_wl
                    new_meas.name = first.name
                    big_signal = big.bin_data()
                    small_signal = small.bin_data()
                    signal = []
                    for wl_b, cnts_b in big_signal:
                        for wl_s, cnts_s in small_signal:
                            if wl_b == wl_s:
                                signal.append([wl_b, cnts_b - cnts_s])
                    new_meas.signal = np.array(signal)
                    new_exp.measurements.append(new_meas)
    return new_exp