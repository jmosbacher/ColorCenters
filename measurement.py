import os
from traits.api import *
from traitsui.api import *
from traitsui.extras.checkbox_column import CheckboxColumn
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.collections import PolyCollection, LineCollection
from matplotlib.colors import colorConverter
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import matplotlib.cm as cmx
from auxilary_functions import wl_to_rgb
import numpy as np
import random
import pandas as pd
try:
    import cPickle as pickle
except:
    import pickle


class BaseMeasurement(HasTraits):
    __kind__ = 'Base'
    main = Any()
    name = Str('Name')
    date = Date()
    summary = Property(Str)

    notes = Str('')
    notebook = Int(1)
    page = Int()

    is_selected = Bool(False)

    def __init__(self, main):
        HasTraits.__init__(self)
        self.main = main

    def _anytrait_changed(self):
        self.main.dirty = True

    def _get_summary(self):
        raise NotImplemented


class SpectrumMeasurement(BaseMeasurement):
    __kind__ = 'Spectrum'

    #####       User Input      #####
    duration = Int(0)

    ex_pol = Int()  # Excitation Polarization
    em_pol = Int()  # Emission Polarization
    ex_wl = Float()  # Excitation Wavelength
    em_wl = Tuple((0.0, 0.0), cols=2, labels=['Min', 'Max'])  # Emission Wavelength
    e_per_count = Int(1)  # electrons per ADC count

    #####       Extracted Data      #####
    signal = Array()
    bg = Array()
    ref = Array()

    #####       Flags      #####
    has_sig = Bool(False)
    has_bg = Bool(False)
    has_ref = Bool(False)
    color = Tuple(0.0, 0.0, 0.0)  # Enum(['r', 'g', 'b', 'y', 'g', 'k','m','c','k'])

    #####       Calculated Data      #####


    #####       UI      #####


    #####       GUI layout      #####
    view = View(
        VGroup(

            HGroup(
                Item(name='ex_pol', label='Excitation POL'),
                Item(name='ex_wl', label='Excitation WL'),
                show_border=True, label='Excitation'),

            HGroup(
                Item(name='em_pol', label='Emission POL'),
                Item(name='em_wl', label='Emission WL'),
                Item(name='e_per_count', label='e/count'),
                Item(name='color', label='Plot Color'),
                show_border=True, label='Emission'),

        ),

    )

    #####       Methods      #####


    def _get_summary(self):
        report = 'Excitation: %d nm'%self.ex_wl + ' | Emission Range: %d:%d nm'%self.em_wl
        return report

    def _signal_default(self):
        return np.array([])

    def _signal_changed(self):
        if len(self.signal) > 1:
            self.em_wl = (round(min(self.signal[:, 0])), round(max(self.signal[:, 0])))

    def _bg_default(self):
        return np.array([])

    def create_series(self):
        """

        :return:
        """
        sig = self.bin_data()
        return pd.Series(sig[:, 1], index=sig[:, 0], name=self.ex_wl)

    def bin_data(self):
        """

        :return:
        """
        rounded = {}
        for data in self.signal:
            wl = round(data[0])
            if wl not in rounded.keys():
                rounded[wl] = []
            rounded[wl].append(data[1])

        averaged = []
        for wl in rounded.keys():
            averaged.append([wl, np.mean(rounded[wl])])
        # print sorted(averaged)

        return np.array(sorted(averaged))

    def plot_data(self):
        ser = self.create_series()
        ax = ser.plot(color=self.color, label=str(self.ex_wl), legend=True)
        ax.set_xlabel('Emission Wavelength')
        ax.set_ylabel('Counts')
        # plt.show()



class AnealingMeasurement(BaseMeasurement):
    __kind__ = 'Anealing'
    temperature = Int(0)
    heating_time = Int(0)
    view = View(
        VGroup(

            HGroup(
                Item(name='temperature', label='Temperature'),
                Item(name='heating_time', label='Heating time'),
                show_border=True, label='Anealing Details'),

        ),

)

class MeasurementTableEditor(TableEditor):

    columns = [
               CheckboxColumn(name='is_selected', label='', width=0.05, horizontal_alignment='center', ),
               ObjectColumn(name='name', label='Name', horizontal_alignment='left', width=0.25),
               ObjectColumn(name='date', label='Date', horizontal_alignment='left', width=0.25),
               ObjectColumn(name='__kind__', label='Type', width=0.25, horizontal_alignment='center'),
               ObjectColumn(name='summary', label='Details', width=0.3, horizontal_alignment='center',),

               ]

    auto_size = True
    sortable = False
    editable = False