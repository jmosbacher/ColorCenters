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

from measurement import BaseMeasurement,SpectrumMeasurement, MeasurementTableEditor
from auxilary_functions import merge_experiments
from data_importing import AutoSpectrumImportTool


class Crystal(HasTraits):
    """

    """
    main = Any()
    name = Str('New Crystal')
    sn = Str('SN')
    desc = Str('Description')
    notes =Str('Notes...')


    measurements = List(BaseMeasurement)
    selected = Instance(BaseMeasurement)

    #####       Data      #####


    #####       Flags      #####
    is_selected = Bool(False)
    has_measurements = Property()

    #####       Info      #####
    ex_wl_range = Property(Tuple)
    em_wl_range = Property(Tuple)
    measurement_cnt = Property(Int)

    #####       UI      #####
    add_type = Enum(['Spectrum', 'Raman', 'Anealing'])
    add_meas = Button('Add')
    edit = Button('Open')
    remove = Button('Remove Selected')
    select_all = Button('Select All')
    unselect_all = Button('Un-select All')
    plot_selected = Button('Plot')
    merge = Button('Merge')
    import_meas = Button('Import Measurements')


    #####       GUI View     #####
    view = View(

        VGroup(

            Group(
                Item(name='selected',style='custom', show_label=False),


            ),
            Group(
                Item(name='measurements', show_label=False, editor=MeasurementTableEditor(selected='selected')),
                show_border=True, label='Datasets'),
            HGroup(
                    Item(name='select_all', show_label=False),
                    Item(name='unselect_all', show_label=False),
                    Item(name='remove', show_label=False,enabled_when='selected'),
                   Item(name='merge', show_label=False),
                    Item(name='plot_selected', show_label=False, enabled_when='selected'),
                  ),

            show_border=True, label='Spectrum'),
        title='Crystal Editor',
        buttons=['OK'],
        kind='nonmodal',
        scrollable=True,
        resizable=True,
        height=800,
        width=1000,

    )

    #####       Initialization Methods      #####
    def __init__(self, main):
        HasTraits.__init__(self)
        self.main = main

    def _anytrait_changed(self):
        self.main.dirty = True

    def _get_has_measurements(self):
        if self.measurements is None:
            return False
        if len(self.measurements):
            return True
        else:
            return False
        
    def import_meas_fired(self):
        tool = AutoSpectrumImportTool(self.main,self.measurements)
        tool.edit_traits()

    def _selected_default(self):
        return SpectrumMeasurement(self.main)

    #####       Private Methods      #####

    def _get_ex_wl_range(self):
        wls = [10000,0]
        for exp in self.measurements:
            if exp.__kind__ == 'Spectrum':
                wls[0] = round(min(exp.ex_wl,wls[0]))
                wls[1] = round(max(exp.ex_wl,wls[1]))
        return tuple(wls)

    def _get_em_wl_range(self):
        wls = [10000,0]
        for exp in self.measurements:
            if exp.__kind__ == 'Spectrum':
                wls[0] = round(min(exp.em_wl[0],wls[0]))
                wls[1] = round(max(exp.em_wl[1],wls[1]))
        return tuple(wls)

    def _get_measurement_cnt(self):
        return len(self.measurements)

    def _edit_fired(self):
        self.selected.edit_traits()

    def _remove_fired(self):
        self.measurements.remove(self.selected)

    def _plot_selected_fired(self):
        for exp in self.measurements:
            if exp.is_selected:
                exp.plot_data()

    def _select_all_fired(self):
        for exp in self.measurements:
            exp.is_selected = True

    def _unselect_all_fired(self):
        for exp in self.measurements:
            exp.is_selected = False

    def _merge_fired(self):
        for_merge = []

        for exp in self.measurements:
            if exp.is_selected:
                for_merge.append(exp)
        main = for_merge[0]
        rest = for_merge[1:]
        for exp in rest:
            main = merge_experiments(main, exp)
            self.measurements.remove(exp)
        main.is_selected = False


    #####      Public Methods      #####
    def add_new(self):
        new = SpectrumMeasurement(self.main)
        self.measurements.append(new)
        self.selected = new
        return new

    def save_to_file(self,path):
        #localdir = os.path.dirname(os.path.abspath(__file__))
        #path = os.path.join(localdir,'saved.spctrm')
        path = self.save_load_path
        with open(path,'wb') as f:
            pickle.dump(self.measurements, f)

    def load_from_file(self):
        #localdir = os.path.dirname(os.path.abspath(__file__))
        #path = os.path.join(localdir,'saved.spctrm')
        path = self.save_load_path
        with open(path, 'rb') as f:
            self.measurements = pickle.load(f)

    def make_dataframe(self):
        data = {}
        for exp in self.measurements:
            data[exp.ex_wl] = exp.create_series()
        return pd.DataFrame(data)

    def save_pandas(self,path):
        df = self.make_dataframe()
        result = df.to_csv(path)
        return result

    def plot_1d(self,kind):

        for exp in self.measurements:
            if exp.__kind__ == kind:
                exp.plot_data()

        """
        df = self.make_dataframe()
        ax = df.plot()
        ax.set_xlabel('Emission Wavelength')
        ax.set_ylabel('Counts')
        plt.show()
        """


    def plot_2d(self,kind):
        jet = plt.get_cmap('jet')
        fig = plt.figure()
        ax = fig.add_subplot(111)
        for data in self.measurements:
            if data.__kind__ == kind:
                sig = data.bin_data()
                xs = sig[:,0]
                ys = np.array([data.ex_wl]*len(sig[:,0]))
                cNorm = colors.Normalize(vmin=min(sig[:,1]), vmax=max(sig[:,1]))
                scalarMap = cmx.ScalarMappable(norm=cNorm, cmap=jet)
                cs = scalarMap.to_rgba(sig[:,1])
                ax.scatter(xs,ys,color=cs)
        ax.set_xlabel('Emission Wavelength')
        ax.set_ylabel('Excitation Wavelength')
        plt.show()

    def plot_3d(self,alpha,kind):
        """

        :return:
        """
        fig = plt.figure()
        ax = fig.gca(projection='3d')

        def cc(arg):
            return colorConverter.to_rgba(arg, alpha=0.6)
        #col_options = [cc('r'), cc('g'), cc('b'), cc('y')]

        verts = []
        colors = []
        zs = []
        wl_range = [3000,0]
        cnt_range = [0,10]
        for data in self.measurements:
            if data.__kind__ == kind:
                sig = data.bin_data()
                #print sig
                if len(sig):
                    zs.append(data.ex_wl)
                    if min(sig[:,1])<0:
                        sig[:,1] = sig[:,1] + abs(min(sig[:,1]))
                    sig[-1, 1] = sig[0, 1] = 0
                    verts.append(sig)
                    colors.append(data.color)
                wl_range = [min(wl_range[0],min(sig[:,0])),max(wl_range[1],max(sig[:,0]))]
                cnt_range = [min(cnt_range[0], min(sig[:, 1])), max(cnt_range[1], max(sig[:, 1]))]
        poly = PolyCollection(verts,closed=False, facecolors=colors) #

        poly.set_alpha(alpha)
        ax.add_collection3d(poly, zs=zs, zdir='y')
        ax.set_xlabel('Emission')
        ax.set_xlim3d(wl_range)
        ax.set_ylabel('Excitation')
        ax.set_ylim3d(min(zs)-10, max(zs)+10)
        ax.set_zlabel('Counts')
        ax.set_zlim3d(cnt_range)
        plt.show()



class CrystalTableEditor(TableEditor):

    columns = [
                CheckboxColumn(name='is_selected', label='', width=0.08, horizontal_alignment='center', ),
                ObjectColumn(name = 'name',label = 'Name',width = 0.25,horizontal_alignment = 'left',editable=True),

                ObjectColumn(name='sn', label='SN', width=0.25, horizontal_alignment='left', editable=True),

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
    editable = True

if __name__ == '__main__':
    app = Crystal()
    app.configure_traits()