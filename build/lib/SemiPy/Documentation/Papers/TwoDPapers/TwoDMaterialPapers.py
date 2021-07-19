"""
Module for listing 2D material papers
"""

from SemiPy.Documentation.ScientificPaper import ScientificPaper
import datetime


class MonolayerMoS2ThicknessDickinson(ScientificPaper):

    name = 'THE CRYSTAL STRUCTURE OF MOLYBDENITE'

    authors = ['Roscoe G. Dickinson', 'Linus Pauling']

    publisher = 'Journal of the American Chemical Society'

    doi = '10.1021/ja01659a020'

    date = datetime.datetime(1923, 6, 1)

    synopsis = 'Gives the single layer thickness of MoS2 to be 6.15 Angstroms'


class MonolayerMoS2ThermalConductivityYan(ScientificPaper):

    name = 'Thermal Conductivity of Monolayer Molybdenum Disulfide Obtained from Temperature-Dependent' \
           ' Raman Spectroscopy'

    authors = ['Rusen Yan', 'Jeffrey R. Simpson', 'Simone Bertolazzi', 'Jacopo Brivio', 'Michael Watson', 'Xufei Wu',
               'Andras Kis', 'Tengfei Luo', 'Angela R. Hight Walker', 'Huili Grace Xing']

    publisher = 'ACS Nano'

    doi = '10.1021/nn405826k'

    date = datetime.datetime(2014, 1, 1)

    synopsis = 'Measures the thermal conductivity of monolayer MoS2 to be 35 W/m/K at room temperature.'


class MoS2SiO2AlNThermalBoundaryResistance(ScientificPaper):

    name = ''

    authors = ['Eilam Yalon', 'Burak Aslan', 'Kirby K. H. Smithe', 'Connor J. McClellan', 'Saurabh V. Suryavanshi',
               'Feng Xiong', 'Aditya Sood','Christopher M. Neumann', 'Xiaoqing Xu', 'Kenneth E. Goodson',
               'Tony F. Heinz', 'Eric Pop']

    publisher = 'ACS AMI'

    doi = '10.1021/acsami.7b11641'

    date = datetime.datetime(2017, 10, 20)

    synopsis = 'Measures the thermal boundary resistance between MoS2 and SiO2, and MoS2 and AlN'