"""
Testing for transistor models
"""
import unittest
from SemiPy.Extractors.TLM.TLMExtractor import TLMExtractor
from SemiPy.Devices.Devices.FET.ThinFilmFET import nTFT
from SemiPy.Devices.Materials.Oxides.MetalOxides import SiO2
from SemiPy.Devices.Materials.Semiconductors.BulkSemiconductors import Silicon
from SemiPy.Devices.Materials.TwoDMaterials.TMD import MoS2
from SemiPy.helper.paths import get_abs_semipy_path
from physics.value import Value, ureg
import numpy as np

idvd_path = get_abs_semipy_path('SampleData/TLMExampleData/WSe2_Sample_4_Id_Vd.txt') # unused
idvg_path = get_abs_semipy_path('SampleData/TLMExampleData')

widths = Value(4.0, ureg.micrometer)
lengths = Value.array_like(np.array([0.5, 1.0, 2.0, 2.5, 3.0, 3.5]), unit=ureg.micrometer)

gate_oxide = SiO2(thickness=Value(30, ureg.nanometer))
channel = MoS2(layer_number=1)
result = TLMExtractor(widths=widths, lengths=lengths,
                      gate_oxide=gate_oxide, channel=channel,
                      FET_class=nTFT,
                      idvg_path=idvg_path,
                      vd_values=[1.0, 2.0],
                      substrate=Silicon())

result.save_tlm_plots()
