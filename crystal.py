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
import numpy as np
import random
import pandas as pd
import matplotlib
matplotlib.style.use('ggplot')
import pandas as pd
try:
    import cPickle as pickle
except:
    import pickle

from experiment import BaseExperiment,SpectrumExperiment, ExperimentTableEditor
from measurement import SpectrumMeasurement
from auxilary_functions import merge_spectrums
from data_importing import AutoSpectrumImportTool


class Crystal(HasTraits):
    """

    """
    main = Any()
    name = Str('New Crystal')
    sn = Str('SN')
    desc = Str('Description')
    notes =Str('Notes...')


    experiments = List(BaseExperiment)
    selected = Instance(BaseExperiment)

    #####       Data      #####


    #####       Flags      #####
    is_selected = Bool(False)
    has_experiments = Property()

    #####       Info      #####
    ex_wl_range = Property(Tuple)
    em_wl_range = Property(Tuple)
    experiment_cnt = Property(Int)

    #####       UI      #####
    add_type = Enum(['Spectrum', 'Raman', 'Anealing'])
    add_exp = Button('Add Experiment')
    edit = Button('Open')
    remove = Button('Remove Selected')
    select_all = Button('Select All')
    unselect_all = Button('Un-select All')
    plot_selected = Button('Plot')
    merge = Button('Merge')
    #import_exp = Button('Import Experiment')
    comp_sel = Button('Compare selected')
    plot_1d = Button('Plot 1D')
    plot_2d = Button('Plot 2D')
    plot_3d = Button('Plot 3D')

    #####       Visualization     #####
    kind = Enum('Spectrum',['Spectrum', 'Raman'])
    alpha = Float(0.6)

    #####       GUI View     #####
    view = View(
        VSplit(
            VGroup(

                HGroup(
                    Item(name='select_all', show_label=False),
                    Item(name='unselect_all', show_label=False),
                    Item(name='remove', show_label=False, enabled_when='selected'),
                    Item(name='merge', show_label=False),

                    Item(name='comp_sel', show_label=False, enabled_when='selected'),
                    # Item(name='add_type', show_label=False),
                    Item(name='add_exp', show_label=False),

                show_border=True, label='Experiments'),
                Item(name='experiments', show_label=False, editor=ExperimentTableEditor(selected='selected')),
                HGroup(
                    #Item(name='kind', show_label=False, enabled_when='selected'),
                    Item(name='alpha', label='Transparency', enabled_when='selected'),
                    Item(name='plot_1d', show_label=False, enabled_when='selected'),
                    Item(name='plot_2d', show_label=False, enabled_when='selected'),
                    Item(name='plot_3d', show_label=False, enabled_when='selected'),
                    show_border=True, label='Visualization'),
            ),

        VGroup(

            Group(
                Item(name='selected', style='custom', show_label=False),

            ),

                show_border=True, label='Selected'),

        ),

        title='Crystal Editor',
        buttons=['OK'],
        kind='nonmodal',
        scrollable=True,
        resizable=True,
        height=800,
        width=1280,

    )

    #####       Initialization Methods      #####
    def __init__(self, **kargs):
        HasTraits.__init__(self)
        self.main = kargs.get('main', None)

    def _anytrait_changed(self):
        if self.main is None:
            return
        self.main.dirty = True

    def _get_has_experiments(self):
        if self.experiments is None:
            return False
        if len(self.experiments):
            return True
        else:
            return False

    def _plot_1d_fired(self, ):
        self.selected.plot_1d(self.kind)

    def _plot_2d_fired(self):
        self.selected.plot_2d(self.kind)

    def _plot_3d_fired(self):
        self.selected.plot_3d(self.alpha, self.kind)

    def _add_exp_fired(self):
        self.experiments.append(SpectrumExperiment(main=self.main))

    def _comp_sel_fired(self):
        sel = []
        for meas in self.experiments:
            if meas.is_selected:
                sel.append(meas)
        if len(sel)!=2:
            return
        new_exp = SpectrumExperiment(main=self.main)
        new_exp.name = sel[0].name +' vs '+sel[1].name
        for first in sel[0].measurements:
            for second in sel[1].measurements:
                if first.ex_wl==second.ex_wl:
                    if first.has_signal and second.has_signal:
                        big = first
                        small = second
                        if np.average(second.signal[0,:])>np.average(first.signal[0,:]):
                            big = second
                            small = first
                        new_meas = SpectrumMeasurement(main=self.main)
                        new_meas.ex_wl = first.ex_wl
                        new_meas.name = first.name
                        big_signal = big.bin_data()
                        small_signal = small.bin_data()
                        signal = []
                        for wl_b, cnts_b in big_signal:
                            for wl_s, cnts_s in small_signal:
                                if wl_b==wl_s:
                                    signal.append([wl_b,cnts_b-cnts_s])
                        new_meas.signal = np.array(signal)
                        new_exp.measurements.append(new_meas)
        self.experiments.append(new_exp)


    def import_data(self):
        tool = AutoSpectrumImportTool(self.selected)
        tool.edit_traits()

    def _selected_default(self):
        return SpectrumExperiment(main=self.main)

    #####       Private Methods      #####

    def _get_ex_wl_range(self):
        wls = [10000,0]
        for exp in self.experiments:
            if exp.__kind__ == 'Spectrum':
                wls[0] = round(min(exp.ex_wl,wls[0]))
                wls[1] = round(max(exp.ex_wl,wls[1]))
        return tuple(wls)

    def _get_em_wl_range(self):
        wls = [10000,0]
        for exp in self.experiments:
            if exp.__kind__ == 'Spectrum':
                wls[0] = round(min(exp.em_wl[0],wls[0]))
                wls[1] = round(max(exp.em_wl[1],wls[1]))
        return tuple(wls)

    def _get_experiment_cnt(self):
        return len(self.experiments)

    def _edit_fired(self):
        self.selected.edit_traits()

    def _remove_fired(self):
        self.experiments.remove(self.selected)

    def _plot_selected_fired(self):
        for exp in self.experiments:
            if exp.is_selected:
                exp.plot_data()

    def _select_all_fired(self):
        for exp in self.experiments:
            exp.is_selected = True

    def _unselect_all_fired(self):
        for exp in self.experiments:
            exp.is_selected = False

    def _merge_fired(self):
        for_merge = []

        for exp in self.experiments:
            if exp.is_selected:
                for_merge.append(exp)
        main = for_merge[0]
        rest = for_merge[1:]
        for exp in rest:
            main = merge_spectrums(main, exp)
            self.experiments.remove(exp)
        main.is_selected = False


    #####      Public Methods      #####
    def add_new(self):
        new = SpectrumExperiment(main=self.main)
        self.experiments.append(new)
        self.selected = new
        return new

    def save_to_file(self,path):
        #localdir = os.path.dirname(os.path.abspath(__file__))
        #path = os.path.join(localdir,'saved.spctrm')
        path = self.save_load_path
        with open(path,'wb') as f:
            pickle.dump(self.experiments, f)

    def load_from_file(self):
        #localdir = os.path.dirname(os.path.abspath(__file__))
        #path = os.path.join(localdir,'saved.spctrm')
        path = self.save_load_path
        with open(path, 'rb') as f:
            self.experiments = pickle.load(f)

    def make_dataframe(self):
        data = {}
        for exp in self.experiments:
            data[exp.ex_wl] = exp.create_series()
        return pd.DataFrame(data)

    def save_pandas(self,path):
        df = self.make_dataframe()
        result = df.to_csv(path)
        return result





class CrystalTableEditor(TableEditor):

    columns = [
                CheckboxColumn(name='is_selected', label='', width=0.08, horizontal_alignment='center', ),
                ObjectColumn(name = 'name',label = 'Name',width = 0.25,horizontal_alignment = 'left',editable=True),

                ObjectColumn(name='sn', label='SN', width=0.25, horizontal_alignment='left', editable=True),

                #ObjectColumn(name = 'ex_wl_range',label = 'Excitation WLs',horizontal_alignment = 'center',
                             #width = 0.13,editable=False),

                #ObjectColumn(name = 'em_wl_range',label = 'Emission WLs',width = 0.13,
                             #horizontal_alignment = 'center',editable=False),
                #ObjectColumn(name = 'em_pol',label = 'Emission POL',width = 0.08,horizontal_alignment = 'center'),

                ObjectColumn(name='experiment_cnt', label='Experiments', width=0.08,
                             horizontal_alignment='center',editable=False),

                ObjectColumn(name='desc', label='Description', width=0.08,
                             horizontal_alignment='center', editable=False),
              ]

    auto_size = True
    sortable = False
    editable = True

if __name__ == '__main__':
    app = Crystal()
    app.configure_traits()