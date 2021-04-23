#!/bin/sh

echo Installation de pip3
sudo apt install python3-pip

echo Installation des librairies Python
pip3 install opencv-python
pip3 install os
pip3 install shutil
pip3 install pandas
pip3 install glob
pip3 install subprocess
pip3 install time


echo Installation de ffmpeg
sudo apt install ffmpeg

echo Installation de git
sudo apt install git

echo Installation d OpenFace
cd ~/
git init
git clone https://github.com/TadasBaltrusaitis/OpenFace.git
cd ~/OpenFace/
bash install.sh
