# pySMFRETda
pySMFRETda is demonstration app of the parameter server implementation for [gSMFRETda](https://github.com/liu-kan/gSMFRETda).
It contains a set of Python tools to help you preparing hdf5 data file and serving as a parameter server for running [gSMFRETda](https://github.com/liu-kan/gSMFRETda).

## Install
```bash
#if debian or ubuntu
sudo apt install build-essential libhdf5-dev pkg-config protobuf-compiler libprotobuf-dev libnanomsg-dev
#elif centos or redhat
sudo dnf install protobuf-devel hdf5-devel nanomsg-devel python3-protobuf python3-devel 
#endif
pip3 install --user -r requirements.txt
```
For windows installation, go to [INSTALL_WIN.md](INSTALL_WIN.md).

##  Prepare data for gSMFRETda

```bash
git clone https://github.com/liu-kan/pySMFRETda.git
cd pySMFRETda
python3 untils/ptu2hdf.py
python3 untils/arrivalTimePDAdata.py
```

## Trouble shooting
If you meet errors like
```bash
Traceback (most recent call last):
  File "untils/arrivalTimePDAdata.py", line 10, in <module>
    from data import  prepData
  File "/home/liuk/data/build/g/pySMFRETda/untils/data/prepData.py", line 17, in <module>
    from fretbursts import *
  File "/home/liuk/miniconda3/envs/gSMFRETda/lib/python3.7/site-packages/fretbursts/__init__.py", line 144, in <module>
    from . import burst_plot as bpl
  File "/home/liuk/miniconda3/envs/gSMFRETda/lib/python3.7/site-packages/fretbursts/burst_plot.py", line 43, in <module>
    from matplotlib.mlab import normpdf
ImportError: cannot import name 'normpdf' from 'matplotlib.mlab' (/home/liuk/miniconda3/envs/gSMFRETda/lib/python3.7/site-packages/matplotlib/mlab.py)
```
Build [FRETBursts](https://github.com/OpenSMFS/FRETBursts) from [@tritemio](https://github.com/tritemio) in [my repository](https://github.com/liu-kan/FRETBursts), which replace mpl.normpdf with scipy.stats.norm.pdf.
```bash
pip3 uninstall fretbursts # or conda uninstall fretbursts
git clone --depth=1 https://github.com/liu-kan/FRETBursts.git
cd FRETBursts
python3 setup.py build
python3 setup.py install
```
