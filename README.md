# Loup-Garou CPP
View full project (voir le projet entier) : baruch.hol.es 

## Installation

You'll need Python 3.X, Flask and sqlite3 | Vous aurez besoin de Python 3.X, Flask et sqlite3.

(pip install flask, pip install sqlite3)

NB : they are already installed in Annaconda | NB : ils sont installés de base dans Annaconda 

1. Download or clone the project | Télécharger ou cloner le dossier
2. Using the terminal (Linux - Mac OS) or cmd (Windows), navigate to the directory where serv.py is | En utilisant le terminal (Mac OS ou Linux) ou la cmd (Windows), naviguez vers l'emplacement où est serv.py
3. Windows : `set FLASK_APP=serv.py`  | Mac OS / Linux : `export FLASK_APP=serv.py`
4. `flask run`
5. The website will be available at the localhost adress shown in the cmd or terminal
6. You'll need to edit `users.db` : during the sign-in phase, `moment` in `ext` will have to be set to "start". Then, you'll need to manually atribute the roles, and set the moment to "loups". This can be done with any sqlite database editor.
Note : 6 is WIP.


## Bug report 

Contact me : baruch.byrdin@grenoble-inp.org
