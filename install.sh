#!/bin/bash
LOCAL=$(pwd)
ACTIVATE_PATH=$(pwd)/.venv/bin/activate

# Installation de git
sudo apt install -y git

# installation OpenFace
git clone https://github.com/TadasBaltrusaitis/OpenFace.git
cd OpenFace
bash ./download_models.sh
sudo bash ./install.sh
cd $LOCAL
mv OpenFace $HOME/

# Installation de virtualenv
sudo apt install python3-virtualenv -y

# Création d'un environnement virtuel
virtualenv .venv

# Installation des requirements dans l'environnement virtuel
.venv/bin/pip3 install -r requirements.txt

#Installation de ffmpeg
sudo apt install -y ffmpeg

# Création d'alias :
echo "alias work_resileyes='source $ACTIVATE_PATH'" >> ~/.bashrc

