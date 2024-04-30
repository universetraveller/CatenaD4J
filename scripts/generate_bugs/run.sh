./clean.sh
python3 run.py 
python3 validate.py
python3 export.py -m all
cd statstics && python3 statstics.py && cd ..
