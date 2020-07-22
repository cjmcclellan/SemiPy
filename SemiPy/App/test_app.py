"""
Testing of the SemiPy Dash App
"""
import unittest
from SemiPy.App.app import IVExtractionApp


class IVExtractionAppTest(unittest.TestCase):

    def test_app(self):
        test = IVExtractionApp.create_app_instance('Test')
        test.build_app()
        # test.app.run_server(debug=True)
