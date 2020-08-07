rm -r ./build
rm -r ./dist
rm -r ./Extractions.egg-info
python setup.py install
python setup.py sdist
