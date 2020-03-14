"""
Module for listing 2D material papers
"""

from SemiPy.Documentation.ScientificPaper import ScientificPaper
import datetime


class Stanford2DSPaper(ScientificPaper):

    name = 'S2DS: Physics-based compact model for circuit simulationof two-dimensional semiconductor devices including non-idealities'

    authors = ['Saurabh V.Suryavanshi', 'Eric Pop']

    publisher = 'Journal of Applied Physics'

    doi = '10.1063/1.4971404'

    date = datetime.datetime(2016, 12, 15)
