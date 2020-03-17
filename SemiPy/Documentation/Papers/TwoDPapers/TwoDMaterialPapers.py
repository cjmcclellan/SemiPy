"""
Module for listing 2D material papers
"""

from SemiPy.Documentation.ScientificPaper import ScientificPaper
import datetime


class MoS2Thickness(ScientificPaper):

    name = 'THE CRYSTAL STRUCTURE OF MOLYBDENITE'

    authors = ['Roscoe G. Dickinson', 'Linus Pauling']

    publisher = 'Journal of the American Chemical Society'

    doi = '10.1021/ja01659a020'

    date = datetime.datetime(1923, 6, 1)

    synopsis = 'Gives the single layer thickness of MoS2 to be 6.15 Angstroms'
