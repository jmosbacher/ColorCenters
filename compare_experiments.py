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


class ExperimentComparison(BaseExperiment):

    exp1 = Instance(BaseExperiment)
    exp2 = Instance(BaseExperiment)
    subtraction = Instance(BaseExperiment)
    has_sub = Property(Bool)

    def plot_1d(self,kind,title=''):
        f, axs = plt.subplots(3, sharex=True)
        axs[0].set_title(self.exp1.crystal_name+' '+self.exp1.name)
        for meas in self.exp1.measurements:
            meas.plot_data(ax=axs[0],legend=False)

        axs[1].set_title(self.exp2.crystal_name + ' ' + self.exp2.name)
        for meas in self.exp2.measurements:
            meas.plot_data(ax=axs[1],legend=False)

        axs[2].set_title('Subtraction')
        for meas in self.subtraction.measurements:
            meas.plot_data(ax=axs[2],legend=False)

        plt.suptitle(title, fontsize=16)
        plt.show()

    def plot_2d(self, kind, title=''):
        jet = plt.get_cmap('jet')
        fig = plt.figure()
        ax = fig.add_subplot(111)
        for data in self.subtraction.measurements:
            if data.__kind__ == kind:
                sig = data.bin_data()
                xs = sig[:, 0]
                ys = np.array([data.ex_wl] * len(sig[:, 0]))
                cNorm = colors.Normalize(vmin=min(sig[:, 1]), vmax=max(sig[:, 1]))
                scalarMap = cmx.ScalarMappable(norm=cNorm, cmap=jet)
                cs = scalarMap.to_rgba(sig[:, 1])
                ax.scatter(xs, ys, color=cs)

        plt.title(title)
        ax.set_xlabel('Emission Wavelength')
        ax.set_ylabel('Excitation Wavelength')
        plt.show()

    def plot_3d(self, alpha, kind, title=''):
        """

        :return:
        """
        fig = plt.figure()
        ax = fig.gca(projection='3d')

        def cc(arg):
            return colorConverter.to_rgba(arg, alpha=0.6)

        # col_options = [cc('r'), cc('g'), cc('b'), cc('y')]

        verts = []
        colors = []
        zs = []
        wl_range = [3000, 0]
        cnt_range = [0, 10]
        for data in self.subtraction.measurements:
            if data.__kind__ == kind:
                sig = data.bin_data()
                # print sig
                if len(sig):
                    zs.append(data.ex_wl)
                    if min(sig[:, 1]) != 0:
                        sig[:, 1] = sig[:, 1] - min(sig[:, 1])
                    sig[-1, 1] = sig[0, 1] = 0
                    verts.append(sig)
                    colors.append(data.color)
                wl_range = [min(wl_range[0], min(sig[:, 0])), max(wl_range[1], max(sig[:, 0]))]
                cnt_range = [min(cnt_range[0], min(sig[:, 1])), max(cnt_range[1], max(sig[:, 1]))]
        poly = PolyCollection(verts, closed=False, facecolors=colors)  #

        poly.set_alpha(alpha)
        ax.add_collection3d(poly, zs=zs, zdir='y')
        ax.set_xlabel('Emission')
        ax.set_xlim3d(wl_range)
        ax.set_ylabel('Excitation')
        ax.set_ylim3d(min(zs) - 10, max(zs) + 10)
        ax.set_zlabel('Counts')
        ax.set_zlim3d(cnt_range)
        plt.title(title)
        plt.show()

    def compare_experiments(self):
        new_exp = SpectrumExperiment(main=self.exp1.main)
        self.name = self.exp1.name + ' vs ' + self.exp2.name
        self.crystal_name = self.exp1.crystal_name + ' vs ' + self.exp2.crystal_name
        for first in self.exp1.measurements:
            for second in self.exp2.measurements:
                if first.ex_wl == second.ex_wl:
                    if first.has_sig and second.has_sig:
                        new_meas = SpectrumMeasurement(main=self.exp1.main)
                        new_meas.ex_wl = first.ex_wl
                        new_meas.name = first.name
                        big_signal = first.bin_data()
                        small_signal = second.bin_data()
                        signal = []
                        for wl_b, cnts_b in big_signal:
                            for wl_s, cnts_s in small_signal:
                                if wl_b == wl_s:
                                    signal.append([wl_b, cnts_b - cnts_s])
                        new_meas.signal = np.array(signal)
                        new_exp.measurements.append(new_meas)
        self.subtraction = new_exp


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
                #CheckboxColumn(name='is_selected', label='', width=0.08, horizontal_alignment='center', ),
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

                #ObjectColumn(name='desc', label='Description', width=0.08,
                             #horizontal_alignment='center', editable=False),
              ]

    auto_size = True
    sortable = False
    editable = False

class AllExperimentList(HasTraits):
    project = Any()
    experiments = List()
    comparisons = DelegatesTo('project') #List()
    selected_comp = Instance(BaseExperiment)
    selected_exp1 = Instance(BaseExperiment)
    selected_exp2 = Instance(BaseExperiment)

    compare = Button('Compare')
    remove_exp = Button('Remove Experiment')
    remove_comp = Button('Remove Comparison')
    plot_1d = Button('Plot 1D')
    plot_2d = Button('Plot 2D')
    plot_3d = Button('Plot 3D')
    plot_title = Str('')
    plot_1d_1st = Button('Plot')
    plot_1d_2nd = Button('Plot')

    #####       Visualization     #####
    plot_sel = Enum('Comparison',['First','Second', 'Subtraction','Comparison'])

    kind = Enum('Spectrum',['Spectrum', 'Raman'])
    alpha = Float(0.6)


    view = View(

        VSplit(

            VGroup(


            HGroup(
                Group(Item(name='experiments', show_label=False, editor=ExperimentListTableEditor(selected='selected_exp1')),
                      Item(name='plot_1d_1st', show_label=False,),
                      show_border=True,label='First'),
                Group(Item(name='experiments', show_label=False, editor=ExperimentListTableEditor(selected='selected_exp2')),
                      Item(name='plot_1d_2nd', show_label=False, ),
                      show_border=True, label='Second'),
            ),
            HGroup(
                    Item(name='compare', show_label=False, ),
                    #Item(name='remove_exp', show_label=False, ),
                ),
            ),
        VGroup(
            HGroup(
                # Item(name='kind', show_label=False, enabled_when='selected'),
                Item(name='plot_sel', label='Plot', enabled_when='selected'),
                Item(name='plot_title', label='Title', enabled_when='selected'),
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
        #self.comparisons = project.comparisons
        self.compile_experiment_list()
        HasTraits.__init__(self)

    def _plot_1d_fired(self):
        selection = {'First':self.selected_comp.exp1,
        'Second': self.selected_comp.exp2,
        'Subtraction': self.selected_comp.subtraction ,
        'Comparison': self.selected_comp,
        }

        selection[self.plot_sel].plot_1d(self.kind,title=self.plot_title)

    def _plot_1d_1st_fired(self):
        self.selected_exp1.plot_1d(self.kind)

    def _plot_1d_2nd_fired(self):
        self.selected_exp2.plot_1d(self.kind)

    def _plot_2d_fired(self):
        selection = {'First': self.selected_comp.exp1,
                     'Second': self.selected_comp.exp2,
                     'Subtraction': self.selected_comp.subtraction,
                     'Comparison': self.selected_comp,
                     }

        selection[self.plot_sel].plot_2d(self.kind,title=self.plot_title)

    def _plot_3d_fired(self):
        selection = {'First': self.selected_comp.exp1,
                     'Second': self.selected_comp.exp2,
                     'Subtraction': self.selected_comp.subtraction,
                     'Comparison': self.selected_comp,
                     }

        selection[self.plot_sel].plot_3d(self.alpha,self.kind,title=self.plot_title)


    def compile_experiment_list(self):
        for crystal in self.project.crystals:
            for exp in crystal.experiments:
                exp.crystal_name = crystal.name + '_' + crystal.sn
                self.experiments.append(exp)

    def _compare_fired(self):

        comp = ExperimentComparison(exp1=self.selected_exp1,exp2=self.selected_exp2)
        comp.compare_experiments()
        self.comparisons.append(comp)

    def _remove_exp_fired(self):
        self.comparisons.remove(self.selected_exp)

    def _remove_comp_fired(self):
        self.comparisons.remove(self.selected_comp)

