# xml_to_csv
Reads arbitrary xml formats and saves as csv. The yaml file used to create the conda environment this was tested in has been included for convenience.


## Creating the Environment
On MacOS and Linux:
```
conad env create -f environment.yml
source activate xml_to_csv
```
Or
```
conad env create -f environment.yml
conda activate xml_to_csv
```

Pandas and Numpy dependencies might be removed in the future. Unsure about xmltodict. Make sure you install xmltodict (in a virtual environment, yaml included).

## Dependencies
This code has been tested in this environment.

Python 3 3.7.x, 3.8.x
Numpy 1.19.1
Pandas 1.1.0
xmltodict 0.12.0

### OS
MacOS Catalina 10.15.6
Windows 10 July 2020
