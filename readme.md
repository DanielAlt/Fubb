### MovieFubb

MovieFubb is an application designed to make sharing movie lists and favourite lists easy and fun. It's powered by a tiny collection of bots, who seek meta data in internet friendly ways.

Application programmed by Daniel Altenburg (c) 2016 - 2017

#### Installation

For production installation instructions please see [install.md](install.md)

To install for development

Start by cloning this repository

```bash
cd ~/
git clone https://github.com/DanielAlt/Fubb
```

##### Windows

- Download and install the python2.7 msi from [python.org](https://www.python.org/download/releases/2.7/)
- Run the installer.  
- Include python in you PATH environment variable. *This is usually located at ```C:\\python27\```*

If pip isn't already installed, Install Pip by doing the followings.

```ps1
wget -O get-pip.py https://bootstrap.pypa.io/get-pip.py
python get-pip.py
```

*make sure to include pip in your PATH environment variable, under normal circumstances it should be located at ```C:\\Python27\Scripts```*

if you experience any issues installing pip, please see [this stackoverflow question](https://stackoverflow.com/questions/4750806/how-do-i-install-pip-on-windows)

Now install virtualenv with pip.

```ps1
pip install virtualenv
```

With virtualenv installed create a new python virtual environment.

```ps1
virtualenv ~/FubbEnv
```

Source the python installation.

```ps1
FubbEnv/Scripts/activate

```

*if you experience an error, 'running scripts is disabled on this system,' execute ```Set-ExecutionPolicy Unrestricted -Force``` in powershell as administrator*

Now you're ready to install the application

```ps1
cd /path/to/Fubb
python setup.py develop
..\FubbEnv\Scripts\initialize_MovieFubb_db.exe development.ini
pserve development.ini
```

##### Ubuntu

Instructions for ubuntu are currently incomplete. 

```bash
# install pip if ubuntu 14.04 or below
# this is included with python on later distributions
sudo apt-get install python-pip
```

```bash
# install virtualenv with pip
sudo pip install virtualenv
```
