"""
Module for Scientific Papers
"""
import warnings

list_of_publishers = ['Journal of Applied Physics']


class ScientificPaper(object):

    name = ''
    publisher = ''
    authors = []
    date = None
    doi = ''
    synopsis = ''

    def __init__(self, *args, **kwargs):
        if self.publisher not in list_of_publishers:
            warnings.warn('The publisher {0} for paper {1} is not in the list of publishers.'.format(self.publisher, self.name))

    @classmethod
    def doi_link(cls):
        return 'https://www.doi.org/' + cls.doi

    @classmethod
    def reference_short(cls):
        return '{0}, {1}. {2}; {3}'.format(cls.authors[0], cls.authors[-1], cls.publisher, cls.date.year)

    @classmethod
    def doc_string_ref(cls):
        return '`{0} <{1}>`_'.format(cls.reference_short(), cls.doi_link())

    def __str__(self):
        return self.reference_short()


def citation_decorator(citation):
    def dec(obj):
        obj.__doc__ = obj.__doc__.replace('<citation>', citation.doc_string_ref())
        return obj
    return dec
