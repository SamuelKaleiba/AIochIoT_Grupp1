# Python venv virtual environment cheat sheet
## Create a venv
To create a virtual environment, go to the root of your project and run

``python -m venv venv``

It will create a virtual environment called venv

## Activate venv
``.\venv\Scripts\activate``

## Intall packages
``pip install jupyter matplotlib numpy pandas scipy scikit-learn``

or

``python -m pip install -U jupyter matplotlib numpy pandas scipy scikit-learn``

## Create requirements.txt
``pip freeze > requirements.txt``

## Deactivate venv
``deactivate``

## Install packages from requirements.txt
``pip install -r requirements.txt``

Place the ``requirements.txt`` file in the root of your project directory. When ready to install the dependencies, ensure your terminal is navigated to the project directory and your virtual environment is activated. Then, run ``pip install -r requirements.txt`` to install the listed packages within your virtual environment
