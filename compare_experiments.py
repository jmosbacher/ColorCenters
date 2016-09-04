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
from file_selector import string_list_editor
import numpy as np
import random
import pandas as pd
try:
    import cPickle as pickle
except:
    import pickle
from experiment import SpectrumExperiment,BaseExperiment, ExperimentTableEditor
from measurement import SpectrumMeasurement



def compare_experiments(exp1,exp2):
    new_exp = SpectrumExperiment(main=exp1.main)
    new_exp.name = exp1.name + ' vs ' + exp2.name
    new_exp.crystal_name = exp1.crystal_name + ' vs ' + exp2.crystal_name
    for first in exp1.measurements:
        for second in exp2.measurements:
            if first.ex_wl == second.ex_wl:
                if first.has_sig and second.has_sig:
                    big = first
                    small = second
                    if np.average(second.signal[:, 1]) > np.average(first.signal[:, 1]):
                        big = second
                        small = first
                    new_meas = SpectrumMeasurement(main=exp1.main)
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


class ExperimentListTableEditor(TableEditor):

    columns = [
                CheckboxColumn(name='is_selected', label='', width=0.08, horizontal_alignment='center', ),
                ObjectColumn(name='crystal_name', label='Crystal', width=0.25, horizontal_alignment='left', editable=True),
                ObjectColumn(name = 'name',label = 'Name',width = 0.25,horizontal_alignment = 'left',editable=True),

                #ObjectColumn(name='sn', label='SN', width=0.25, horizontal_alignment='left', editable=True),

                ObjectColumn(name = 'ex_wl_range',label = 'Excitation WLs',horizontal_alignment = 'center',
                             width = 0.13,editable=False),

                ObjectColumn(name = 'em_wl_range',label = 'Emission WLs',width = 0.13,
                             horizontal_alignment = 'center',editable=False),
                #ObjectColumn(name = 'em_pol',label = 'Emission POL',width = 0.08,horizontal_alignment = 'center'),

                ObjectColumn(name='measurement_cnt', label='Datasets', width=0.08,
                             horizontal_alignment='center',editable=False),

                ObjectColumn(name='desc', label='Description', width=0.08,
                             horizontal_alignment='center', editable=False),
              ]

    auto_size = True
    sortable = False
    editable = False

class AllExperimentList(HasTraits):
    project = Any()
    experiments = List()
    comparisons = List()
    selected_comp = Instance(BaseExperiment)
    selected_exp = Instance(BaseExperiment)

    compare = Button('Compare')
    remove_exp = Button('Remove Experiment')
    remove_comp = Button('Remove Comparison')
    plot_1d = Button('Plot 1D')
    plot_2d = Button('Plot 2D')
    plot_3d = Button('Plot 3D')

    #####       Visualization     #####
    plot_sel = Enum('Experiment',['Experiment','Comparison'])
    kind = Enum('Spectrum',['Spectrum', 'Raman'])
    alpha = Float(0.6)


    view = View(

        VSplit(

            VGroup(
                HGroup(
                    Item(name='compare', show_label=False, ),
                    Item(name='remove_exp', show_label=False, ),
                ),

            Item(name='experiments', show_label=False, editor=ExperimentListTableEditor(selected='selected_exp')),
            ),
        VGroup(
            HGroup(
                # Item(name='kind', show_label=False, enabled_when='selected'),
                Item(name='plot_sel', label='Plot', enabled_when='selected'),
                Item(name='plot_1d', show_label=False, enabled_when='selected'),
                Item(name='plot_2d', show_label=False, enabled_when='selected'),
                Item(name='alpha', label='Transparency', enabled_when='selected'),
                Item(name='plot_3d', show_label=False, enabled_when='selected'),
                show_border=True, label='Visualization'),
            HGroup(
                Item(name='remove_comp', show_label=False, ),
                spring
            ),
            Item(name='comparisons', show_label=False,editor=ExperimentListTableEditor(selected='selected_comp')),
        ),
        ),
        title = 'Compare experiments',
        scrollable = True,
        resizable = True,
        height = 800,
        width = 1280,



    )

    def __init__(self,project):
        self.project = project
        self.comparisons = project.comparisons
        self.compile_experiment_list()
        HasTraits.__init__(self)

    def _plot_1d_fired(self, ):
        if self.plot_sel=='Experiment':
            self.selected_exp.plot_1d(self.kind)
        elif self.plot_sel=='Comparison':
            self.selected_comp.plot_1d(self.kind)

    def _plot_2d_fired(self):
        if self.plot_sel == 'Experiment':
            self.selected_exp.plot_2d(self.kind)
        elif self.plot_sel == 'Comparison':
            self.selected_comp.plot_2d(self.kind)

    def _plot_3d_fired(self):
        if self.plot_sel == 'Experiment':
            self.selected_exp.plot_3d(self.alpha,self.kind)
        elif self.plot_sel == 'Comparison':
            self.selected_comp.plot_3d(self.alpha, self.kind)

    def compile_experiment_list(self):
        for crystal in self.project.crystals:
            for exp in crystal.experiments:
                exp.crystal_name = crystal.name + '_' + crystal.sn
                self.experiments.append(exp)

    def _compare_fired(self):
        sel = []
        for exp in self.experiments:
            if exp.is_selected:
                sel.append(exp)
        if len(sel)!=2:
            return
        comp = compare_experiments(sel[0],sel[1])
        self.comparisons.append(comp)

    def _remove_exp_fired(self):
        self.comparisons.remove(self.selected_exp)


    def _remove_comp_fired(self):
        self.comparisons.remove(self.selected_comp)


class ExperimentComparison(HasTraits):

    exp1 = Instance(BaseExperiment)
    exp2 = Instance(BaseExperiment)
    subtraction = Instance(BaseExperiment)

    def plot_1d(self):
        pass

    def plot_2d(self):
        pass

    def plot_3d(self):
        pass

    def compare_experiments(self):
        new_exp = SpectrumExperiment(main=self.exp1.main)
        new_exp.name = self.exp1.name + ' vs ' + self.exp2.name
        new_exp.crystal_name = self.exp1.crystal_name + ' vs ' + self.exp2.crystal_name
        for first in self.exp1.measurements:
            for second in self.exp2.measurements:
                if first.ex_wl == second.ex_wl:
                    if first.has_sig and second.has_sig:
                        big = first
                        small = second
                        if np.average(second.signal[:, 1]) > np.average(first.signal[:, 1]):
                            big = second
                            small = first
                        new_meas = SpectrumMeasurement(main=self.exp1.main)
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
