"""
Dash App for SemiPy
"""
from dash_cjm.plots.Plotting2DApp import StaticPlotting2DApp
from dash_cjm.formatting.formatting import get_subscript_unicode, get_superscript_unicode, get_symbol_unicode
from dash_cjm.basicdivs.uploading import get_upload_div
import dash_table
from dash_cjm.loading import load_csv_or_xls
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from dash_cjm.named_components import NamedDropdown, NamedInput
from SemiPy.Extractors.Transistor.FETExtractor import FETExtractor
import numpy as np

from SemiPy.helper.math import round_to_n


class IVExtractionApp(StaticPlotting2DApp):

    output_values = {'Vt_fwd': 'Forward Threshold Voltage (V)', 'Vt_bwd': 'Backward Threshold Voltage (V)',
                     'mobility': 'Field-Effect Mobility (cm{0}V{1}{2}s{3}{4})'.format(get_superscript_unicode('2'), get_superscript_unicode('-'),
                                                                         get_superscript_unicode('1'), get_superscript_unicode('-'),
                                                                         get_superscript_unicode('1')),
                    'min_ss': 'Minimum Subthreshold Swing (mV/dec)', 'max_gm': 'Maximum Transconductance ({0}S/{1}m)'.format(get_symbol_unicode('mu'), get_symbol_unicode('mu'))}

    x_options = {'id': 'Drain Current ({0}A/{1}m)'.format(get_symbol_unicode('mu'), get_symbol_unicode('mu')),
                 'vg': 'Gate Voltage (V)', 'ss': 'Subthreshold Swing (mV/dec)'}

    data_table_default_data = [{'output_name': output, 'output_value': 0.0} for output in output_values.values()]

    def __init__(self, *args, **kwargs):

        super(IVExtractionApp, self).__init__(upload_input=True, *args, **kwargs)

        named_header_style = {'font-size': '80%', 'margin': '2px'}
        named_header_result_style = {'font-size': '80%', 'margin': '2px', 'font-weight': 'bold', }

        header_style = {'font-weight': 'bold', 'text-decoration': 'underline'}

        self.callback_inputs += [Input('uploaded-data', 'children'), Input('dielectric', 'value'), Input('tox', 'value'),
                                 Input('length', 'value'), Input('width', 'value')]

        # self.callback_outputs += [Output(value, 'value') for value in self.output_values]
        self.callback_outputs += [Output('output_table', 'data')]

        above_graph_layout = html.Div(className='container',
                                         children=[
                                             html.Div(className='row', children=[
                                                 html.Div(
                                                     className='col-sm',
                                                     children=NamedInput(
                                                         name='Dielectric Constant (unitless)',
                                                         id='dielectric',
                                                         placeholder='Give the dielectric constant',
                                                         type='number',
                                                         value=3.9,
                                                         style=named_header_style,
                                                     ),
                                                 ),
                                                 html.Div(
                                                     className='col-sm',
                                                     children=NamedInput(
                                                         name='Gate Oxide Thickness (nm)',
                                                         id='tox',
                                                         placeholder='Give the gate oxide thickness',
                                                         type='number',
                                                         value=30,
                                                         style=named_header_style,
                                                     ),
                                                 ),
                                                 html.Div(
                                                     className='col-sm',
                                                     children=NamedInput(
                                                         name='FET Length ({0}m)'.format(get_symbol_unicode('mu')),
                                                         id='length',
                                                         placeholder='0.0',
                                                         type='number',
                                                         value=1.0,
                                                         style=named_header_style,
                                                     ),
                                                 ),
                                                 html.Div(
                                                     className='col-sm',
                                                     children=NamedInput(
                                                         name='FET Width ({0}m)'.format(get_symbol_unicode('mu')),
                                                         id='width',
                                                         placeholder='0.0',
                                                         type='number',
                                                         value=1.0,
                                                         style=named_header_style,
                                                     ),
                                                 ),
                                             ]),
                                         ])

        below_graph_layout = html.Div([
            html.Div([
                dash_table.DataTable(
                    id='output_table',
                    columns=([{'id': 'output_name', 'name': 'Output Value Extracted'},
                              {'id': 'output_value', 'name': 'Input Value'}]),
                    data=self.data_table_default_data,
                    editable=False,
                )
            ]),
            get_upload_div(' Id Vg Data')
        ])

        self.add_div(div=below_graph_layout, bottom=True)
        self.add_div(div=above_graph_layout, top=True)

    @classmethod
    def create_app_instance(cls, name, *args, **kwargs):
        return IVExtractionApp(name=name, y_variables=[cls.x_options['id'], cls.x_options['ss']], x_variables=[cls.x_options['vg']],
                               compute_function=cls.compute_function, class_name='class', hidden_update=True, *args, **kwargs)

    @staticmethod
    def compute_function(*args, **kwargs):

        # if the uploaded-data is not None, then start the extraction
        if kwargs['uploaded-data'] is not None:
            test = FETExtractor(width=kwargs['width'], length=kwargs['length'], tox=kwargs['tox'],
                                epiox=kwargs['dielectric'], device_polarity='n', idvg_path=kwargs['uploaded-data'])

            print('created FET')

            table_list = [(IVExtractionApp.output_values['Vt_fwd'], round_to_n(test.FET.Vt_fwd.value, 3)),
                          (IVExtractionApp.output_values['Vt_bwd'], round_to_n(test.FET.Vt_bwd.value, 3)),
                          (IVExtractionApp.output_values['mobility'], round_to_n(test.FET.max_mobility.value, 3)),
                          (IVExtractionApp.output_values['max_gm'], round_to_n(test.FET.max_gm.value, 3)),
                          (IVExtractionApp.output_values['min_ss'], round_to_n(test.FET.min_ss, 3))]

            output_table = [{'output_name': name, 'output_value': value} for name, value in table_list]

            result = {IVExtractionApp.x_options['id']: test.idvg.get_column('id'),
                      IVExtractionApp.x_options['vg']: test.idvg.get_column('vg'),
                      IVExtractionApp.x_options['ss']: test.idvg.get_column('ss'),
                      'class': ['Vd = {0}'.format(val) for val in test.idvg.get_secondary_indep_values()],
                      'output_table': output_table}
            # except Exception:
            #     print('found issue')
            #     result = {IVExtractionApp.x_options['id']: np.array([[1]]), IVExtractionApp.x_options['vg']: np.array([[1]]),
            #               'class': ['In'], 'output_table': IVExtractionApp.data_table_default_data}
        else:
            result = {IVExtractionApp.x_options['id']: np.array([[1]]), IVExtractionApp.x_options['vg']: np.array([[1]]),
                      'class': ['In'], 'output_table': IVExtractionApp.data_table_default_data}
        return result

