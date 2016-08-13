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

try:
    import cPickle as pickle
except:
    import pickle

from crystal import Crystal, CrystalTableEditor
from auxilary_functions import merge_crystals
from saving import CanSaveMixin
from handlers import ProjectHandler


class Project(CanSaveMixin):
    main = Any()
    name = Str('New Project')
    notes = Str()
    comments = Str('No Comments')

    #####       Data     #####
    crystals = List(Crystal)
    crystal_cnt = Property()
    selected = Instance(Crystal)

    #####       Flags      #####
    is_selected = Bool(False)

    #####       UI     #####
    add_new = Button('New Crystal')
    remove = Button('Remove')
    edit = Button('Open')
    merge = Button('Merge')
    select_all = Button('Select All')
    unselect_all = Button('Un-select All')

    #####       Visualization     #####
    kind = Enum('Spectrum',['Spectrum', 'Raman'])
    alpha = Float(0.6)
    plot_1d = Button('Plot 1D')
    plot_2d = Button('Plot 2D')
    plot_3d = Button('Plot 3D')

    view = View(
        VGroup(
            HGroup(
                Item(name='name', label='Name'),
                Item(name='comments', label='Comments',springy=True),

            ),
            Group(Item(name='notes', show_label=False,springy=True,editor=TextEditor(multi_line=True), style='custom'),
                  show_border=True, label='Notes'),
            Group(

                Item(name='crystals', show_label=False, editor=CrystalTableEditor(selected='selected')),
                show_border=True, label='Crystals'),
            HGroup(
                Item(name='edit', show_label=False, enabled_when='selected'),

                Item(name='add_new', show_label=False),
                Item(name='unselect_all', show_label=False),
                Item(name='remove', show_label=False, enabled_when='selected'),
                Item(name='merge', show_label=False),
                ),
            HGroup(
                Item(name='kind', show_label=False, enabled_when='selected'),
                Item(name='alpha', label='Transparency', enabled_when='selected'),
                Item(name='plot_1d', show_label=False, enabled_when='selected'),
                Item(name='plot_1d', show_label=False, enabled_when='selected'),
                Item(name='plot_1d', show_label=False, enabled_when='selected'),
                show_border=True, label='Visualization'),

            ),


        buttons=['OK'],
        title='Project Editor',
        kind='nonmodal',
        handler = ProjectHandler(),
        scrollable=True,
        resizable=True,
        height=800,
        width=1000,

    )
    def __init__(self, main):
        HasTraits.__init__(self)
        self.main = main

    def _anytrait_changed(self):
        self.main.dirty = True

    def _get_crystal_cnt(self):
        return len(self.crystals)

    def _edit_fired(self):
        self.selected.edit_traits()

    def _select_all_fired(self):
        for crystal in self.crystals:
            crystal.is_selected = True

    def _unselect_all_fired(self):
        for crystal in self.crystals:
            crystal.is_selected = False

    def _merge_fired(self):
        for_merge = []

        for crystal in self.crystals:
            if crystal.is_selected:
                for_merge.append(crystal)
        main = for_merge[0]
        rest = for_merge[1:]
        for crystal in rest:
            main = merge_crystals(main, crystal)
            self.crystals.remove(crystal)
        main.is_selected = False

    def _add_new_fired(self):
        new = Crystal(self.main)
        self.crystals.append(new)

    def _plot_1d_fired(self,):
        self.selected.plot_1d(self.kind)


    def _plot_2d_fired(self):
        self.selected.plot_2d(self.kind)


    def _plot_3d_fired(self):
        self.selected.plot_3d(self.alpha,self.kind)


class ProjectTableEditor(TableEditor):

    columns = [
                CheckboxColumn(name='is_selected', label='', width=0.05, horizontal_alignment='center', ),
                ObjectColumn(name = 'name',label = 'Name',width = 0.35,horizontal_alignment = 'left',editable=True),
                ObjectColumn(name = 'crystal_cnt',label = 'Crystals',horizontal_alignment = 'center',
                             width = 0.05,editable=False),

                ObjectColumn(name = 'comments',label = 'Comments',width = 0.55,
                             horizontal_alignment = 'center',editable=False),
                #ObjectColumn(name = 'em_pol',label = 'Emission POL',width = 0.08,horizontal_alignment = 'center'),



              ]

    auto_size = True
    sortable = False
    editable = False

