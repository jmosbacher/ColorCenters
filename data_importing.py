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
from file_selector import FileSelectionTool
from measurement import SpectrumMeasurement, BaseMeasurement
from auxilary_functions import color_map, wl_to_rgb, organize_data, read_ascii_file
#from crystal import Crystal
from pyface.api import confirm, error, YES, CANCEL
try:
    import cPickle as pickle
except:
    import pickle


class AutoSpectrumImportToolHandler(Handler):

    def import_data(self,info,group):
        org_data = info.object.import_group(group)
        if org_data is not None:
            if len(org_data):
                code = confirm(info.ui.control, 'Data imported successfully, continue importing? Press Cancel to discard data',
                               title="Import more data?", cancel=True)

                if code == CANCEL:
                    return
                else:
                    info.object.store_data(org_data)
                    if code == YES:
                        return
                    else:
                        info.ui.dispose()
        else:
            error(None, 'Data extraction unsuccessful', title='No Data')

    def object_import_all_changed(self,info):
        self.import_data(info,info.object.selector.filtered_names)


    def import_selected_changed(self,info):
        self.import_data(info,info.object.selector.selected)


class AutoSpectrumImportTool(HasTraits):
    experiment = Any() #Instance(Crystal)
    selector = Instance(FileSelectionTool)
    delimiter = Str(' ')
    #mode = Enum(['New Measurement', 'Append to Selected'])
    import_selected = Button(name='Import Selected',action='import_selected_fired')
    import_all = Button(name='Import All')

    view = View(
        VGroup(
        Group(
            Item(name='selector',show_label=False,style='custom'),
        show_border=True,label='Files to import'),
        HGroup(
            Item(name='delimiter', label='Delimiter', ),
            Item(name='import_selected', show_label=False, ),
            Item(name='import_all', show_label=False, ),
        ),
        ),
        buttons=['OK'],
        kind='modal',
        handler=AutoSpectrumImportToolHandler(),
    )

    def __init__(self, experiment):
        HasTraits.__init__(self)
        self.experiment = experiment



    def _selector_default(self):
        return FileSelectionTool()

    def import_group(self, names):
        dir_path = self.selector.dir
        data = {}
        for name in names:
            path = os.path.join(dir_path, name)
            if os.path.isfile(path):
                data[name] = read_ascii_file(path, self.delimiter)
        organized = organize_data(data)
        return organized

    def store_data(self,org_data):
        for name, data in org_data.items():
            new = self.experiment.add_new()
            new.name = name
            try:
                ex_wl = eval(name.split('in')[0])
                if isinstance(ex_wl, (float, int)):
                    new.ex_wl = ex_wl
            except:
                pass
            new.signal = data.get('sig',([],[]))[0]
            new.bg = data.get('bgd', ([],[]))[0]
            new.ref = data.get('ref', ([],[]))[0]
            new.file_data = {}
            new.file_data['sig'] = data.get('sig', ([], []))[1]
            new.file_data['bgd'] = data.get('bgd', ([], []))[1]
            new.file_data['ref'] = data.get('ref', ([], []))[1]


"""
class BaseDataImportTool(HasTraits):
    main = Any()
    selector = Instance(FileSelectionTool)
    delimiter = Str(' ')
    #mode = Enum(['New Measurement', 'Append to Selected'])
    kind = Enum(['Signal', 'Background'])
    meas_type = Enum(['Spectrum', 'Raman'])
    import_selected = Button('Import Selected')
    import_all = Button('Import All')

    view = View(
        VGroup(
        Group(
            Item(name='selector',show_label=False,style='custom'),
        show_border=True,label='Files to import'),
        HGroup(
            Item(name='delimiter', label='Delimiter', ),
            Item(name='kind', label='Data Type', ),
            Item(name='meas_type', label='Data Type', ),
            Item(name='import_selected', show_label=False, ),
            Item(name='import_all', show_label=False, ),
        ),
        ),
        buttons=['OK'],
        kind='modal'
    )

    def _selector_default(self):
        return FileSelectionTool()


class NewDataImportTool(HasTraits):

    def import_group(self,group):
        dir_path = self.selector.dir
        collection = []
        for name in group:
            path = os.path.join(dir_path, name)
            if os.path.isfile(path):
                #data = self.import_file(path,self.delimiter)
                if self.meas_type == 'Spectrum':
                    spec = SpectrumMeasurement(main=self.main)
                spec.load_from_file(path,self.delimiter,self.kind)
                collection.append(spec)
        return collection

    def _import_selected_fired(self):
        coll = self.import_group(self.selector.selected)
        self.collection.extend(coll)

    def _import_all_fired(self):
        col = self.import_group(self.selector.filtered_names)
        self.collection.extend(col)

    def __init__(self,main,collection):
        HasTraits.__init__(self)
        self.main = main
        self.collection = collection


class AppendDataImportTool(HasTraits):
    meas = Instance(BaseMeasurement)
    path = File()
    delimiter = Str(' ')
    kind = Enum(['Signal', 'Background'])
    import_selected = Button('Import')

    view = View(
        VGroup(
            Group(
                Item(name='path', show_label=False, style='custom'),
                show_border=True, label='File to import'),
            HGroup(
                Item(name='delimiter', label='Delimiter', ),
                Item(name='kind', label='Data Type', ),
                Item(name='import', show_label=False, ),

            ),
        ),
        buttons=['OK'],
        kind='modal'
    )

    def _import_selected_fired(self):
        self.meas.load_from_file(self.path, self.delimiter, self.kind)

    def __init__(self,meas):
        HasTraits.__init__(self)
        self.meas = meas

"""
