# igrida_launchers
Collections of script to launch your matlab expreriments on IGRIDA. 

## The Rational
I spend (please read "I waste") hours understanding how to copile matlab code on IGRIDA.
I spend hours annoying my colleagues begging for their help.
Finally I came up with the folliwing python scripts to compile matlab code and run my expreriment on the amazing IGRIDA clusteer.

## Acknowledgment
Not even a single line was possible without the help of _Clement_ and _Chatalic Carnage_.  
Please whish them _Long Days and Pleasent Nights_

## THE IGRIDA_LAUNCERS COLLECTION
These scripts are python wrapper to easily launch:
- matlab compilation on IGRIDA.
- matlab jobs on IGRIDA.
Moreover they features some function to:
- generate all combination of parameters for your favorite expreriment
- synchronize local2igrida folders 
- send emails with job status
- print jobs status (well, if your forget your username (?) or you are too lazy to ype oarstat)

## PYTHON and PYTORCH on IGRIDA
### Set up the virtualenv
create your project folder

    $ mkdir -p 'my_project'
    $ cd my_project/
run a interactive job (otherwire python and virtualenv module are not available)

    $ oarsub -I -l walltime=1:00:00 # 1hour interactive job
    $ ##If you want to pip-install a huge module (such as pytorch) remeber to reserve enought space
      ##i fact 
    $ oarsub -I -l /nodes=1,walltime=1:00:00 -p 'mem_node > 3*1024'
load the python module of the desired version and the related virtualenv. For python3.6 do the following
    
    $ module load python-3.6.5-gcc-4.9.2-zswqcs2 
    $ module load py-virtualenv-16.0.0-gcc-4.9.2-ogdwl3o
create the virtualenv, activate and pip-install all you want
    
    $ virtualenv venv -p python3.6
    $ source venv/bin/activatie
    $ pip install ...

### Run PYTORCH with GPU-CUDA
Run interactive job (with gpu) and activate the virtualenv

    $ oarsub -I -l /nodes=1/gpu_device=2,walltime=1:00:00 -p 'mem_node > 3*1024' #!!! note the GPU device flag
    $ source venv/bin/activatie
Load module

    $ module load cuda
and goo

    $ python main.py
