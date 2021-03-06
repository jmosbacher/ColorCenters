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
from experiment import BaseExperiment
from auxilary_functions import merge_crystals
from saving import CanSaveMixin
from handlers import ProjectHandler
from compare_experiments import AllExperimentList

class Project(CanSaveMixin):
    main = Any()
    name = Str('New Project')
    notes = Str()
    comments = Str('No Comments')

    #####       Data     #####
    crystals = List(Crystal)
    comparisons = List(BaseExperiment)
    crystal_cnt = Property()
    selected = Instance(Crystal)

    #####       Flags      #####
    is_selected = Bool(False)

    #####       UI     #####
    add_new = Button('New Crystal')
    #import_data = Button('Add Measurements')
    remove = Button('Remove')
    edit = Button('Open')
    merge = Button('Merge')
    select_all = Button('Select All')
    unselect_all = Button('Un-select All')
    compare = Button('All Experiments')



    view = View(
        VGroup(
            HGroup(
                Item(name='add_new', show_label=False),
                Item(name='edit', show_label=False, enabled_when='selected'),
                Item(name='compare', show_label=False),
                spring,
                Item(name='select_all', show_label=False),
                Item(name='unselect_all', show_label=False),
                Item(name='remove', show_label=False, enabled_when='selected'),
                #Item(name='merge', show_label=False),
                #Item(name='import_data', show_label=False, enabled_when='selected'),
            ),

            Group(

                Item(name='crystals', show_label=False, editor=CrystalTableEditor(selected='selected')),
                show_border=True, label='Crystals'),


            Group(
                Item(name='notes', show_label=False, springy=True, editor=TextEditor(multi_line=True), style='custom'),
                show_border=True, label='Notes'),
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
    def __init__(self, **kargs):
        HasTraits.__init__(self)
        self.main = kargs.get('main',None)

    def _anytrait_changed(self):
        if self.main is None:
            return
        self.main.dirty = True

    def _get_crystal_cnt(self):
        return len(self.crystals)

    def _edit_fired(self):
        self.selected.edit_traits()

    def _compare_fired(self):
        comp = AllExperimentList(self)
        comp.edit_traits()

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
    def _remove_fired(self):
        if self.selected is not None:
            self.crystals.remove(self.selected)
    def _add_new_fired(self):
        new = Crystal(main=self.main)
        self.crystals.append(new)

    #def _import_data_fired(self):
        #self.selected.import_data()




class ProjectTableEditor(TableEditor):

    columns = [
                CheckboxColumn(name='is_selected', label='', width=0.1, horizontal_alignment='center', ),
                ObjectColumn(name = 'name',label = 'Name',width = 0.35,horizontal_alignment = 'left',editable=True),
                ObjectColumn(name = 'crystal_cnt',label = 'Crystals',horizontal_alignment = 'center',
                             width = 0.1,editable=False),

                ObjectColumn(name = 'comments',label = 'Comments',width = 0.45,
                             horizontal_alignment = 'center',editable=False),
                #ObjectColumn(name = 'em_pol',label = 'Emission POL',width = 0.08,horizontal_alignment = 'center'),



              ]
    orientation = 'vertical'

    auto_size = True
    sortable = False
    editable = False

