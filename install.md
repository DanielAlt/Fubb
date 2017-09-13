### MovieFubb

#### Installing for production (Ubuntu+Nginx+Pserve)

Clone the application

```bash
git clone https://github.com/DanielAlt/Fubb
```

Install dependencies if necessary

```bash
sudo apt-get install python-pip
sudo pip install virtualenv
```

Create VirtualEnv for Python2.7

```bash
virtualenv --no-site-packages -p python2 FubbEnv
```

Source virtualenv and Export path.

```bash
source FubbEnv/bin/activate
export VENV=FubbEnv/bin
```

Install the application

```bash
cd path/to/Fubb
sudo $VENV/python setup.py install
sudo $VENV/initialize_MovieFubb_db production.ini
```

```bash
sudo $VENV/pip install supervisor
```
