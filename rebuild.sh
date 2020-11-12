rm -r ./build
rm -r ./dist
rm -r ./SemiPy.egg-info/
python setup.py install
python setup.py sdist
