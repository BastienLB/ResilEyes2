import cv2
import os
import shutil
import pandas as pd
import glob
import subprocess
import time
import numpy as np

now = time.time()
here = os.path.abspath(__file__)
here = os.path.dirname(here)


def decoup(file, out_dir):
    """ "
    Fonction permettant de découper une vidéo en une séquence d'images

    file = vidéo à découper
    out_dir = nom du dossier où stocker la séquence d'images. Celui-ci est créé par la fonction
    """

    out_dir = str(out_dir)
    vidcap = cv2.VideoCapture(file)
    success, image = vidcap.read()
    count = 0

    try:
        os.mkdir(out_dir)
    except FileExistsError:
        pass

    os.chdir(out_dir)

    print("Découpage de la vidéo en une séquence d'images...")

    while success:

        cv2.imwrite("frame%d.jpg" % count, image)
        success, image = vidcap.read()
        print("Read a new frame: ", success)
        count += 1

    print("Découpage effectué avec succès !")
    os.chdir(here)


def traiter_img(input_dir, output_dir, remove: bool = True):
    """
    Fonction permettant de lancer OpenFace via python

    input_dir = dossier contenant les images à analyser
    output_dir = dossier où stocker les résultats de l'analyse
    remove = booléen, par défaut = 'True' ==> conserve uniquement les fichiers csv
                            si = 'False' ==> conserve toute l'analyse de OpenFace
    """

    builder = "~/OpenFace/build/bin/FaceLandmarkImg"

    print("########## \nLancement d'OpenFace... \n")

    # Création d'un dossier où stocker les fichiers csv
    # Si le dossier existe déjà, cette action est sautée
    try:
        os.mkdir(output_dir)
    except FileExistsError:
        pass

    temp = output_dir + "/temp"

    # Création d'un dossier temporaire où stocker tous les résultats d'OpenFace
    # Si le dossier existe déjà, cette action est sautée
    try:
        os.mkdir(temp)
    except FileExistsError:
        pass

    # Exécution de la commande permettant de faire tourner OpenFace
    command = builder + " -fdir " + input_dir + " -out_dir " + temp
    os.system(command)

    # Migration de tous les fichiers csv dans le dossier de sortie
    for a in os.listdir(temp):
        if a.endswith("csv"):
            try:
                to_move = temp + "/" + a
                shutil.move(to_move, output_dir)
            except shutil.Error:
                pass

    if remove:
        # Suppression de tous les dossiers et fichiers à l'exception des fichiers csv
        shutil.rmtree(temp)

    print("\n########## \nFin d'OpenFace \n")
    return temp


def traiter_vid(video_name, remove: bool = True):
    """
    Fonction permettant d'utiliser OpenFace sur des vidéos

    video_name = vidéo à traiter
    remove = booléen transmis à la fonction traiter_img
    """

    # Appel de la fonction decoup
    decoup(str(video_name), "processed")

    # Création du dossier de sortie où stocker les fichiers de l'analyse d'OpenFace
    out_dir = str(video_name) + "_processed"
    traiter_img("processed", out_dir, remove=remove)

    # Suppression du dossier 'processed' intermédiaire
    shutil.rmtree("processed")
    return out_dir


def concatener_csv(input_dir):
    """
    Fonction permettant de récolter tous les fichiers csv d'un dossier et de les concaténer
    dans un unique dataframe. Ce dataframe est retourné par la fonction

    input_dir : dossier contenant les fichiers csv
    """

    # On se déplace jusqu'au dossier cible
    os.chdir(input_dir)

    # Stockage des fichiers csv dans une liste
    all_files = glob.glob("*.csv")

    # Itération sur la liste de fichiers csv pour effectuer une concaténation
    frame = pd.concat((pd.read_csv(f, index_col=None, header=0) for f in all_files))

    # On revient finalement à l'endroit où se trouve le programme
    os.chdir(here)

    # Création d'un fichier csv contenant la concaténation
    final_name = input_dir + "_concatenated.csv"
    frame.to_csv(str(final_name), index=False)

    return frame


def vid_to_csv(
    video, trans_vid: bool = False, remove_results: bool = True, remove_csv: bool = True
):
    """
    Fonction permettant d'utiliser OpenFace sur des vidéos et d'obtenir en sortie un fichier csv
    contenant l'évolution des AU au cours des frames

    video = vidéo à traiter
    trans_vid = booléen indiquant s'il faut créer une vidéo comportant l'analyse d'openface, par défaut False
    remove_results = booléen transmis à la fonction traiter_vid, par défaut True
    remove_csv = booléen indiquant s'il faut supprimer les fichiers csv ayant servis à la concaténation, par défaut True
    """

    if trans_vid:
        remove_results = False

    out_dir = traiter_vid(video, remove=remove_results)
    frame = concatener_csv(out_dir)

    if trans_vid:
        dir = os.path.join(out_dir, "temp")
        os.chdir(dir)
        output = str(video) + "_analysed.mp4"
        subprocess.call(["ffmpeg", "-i", "frame%d.jpg", output])
        shutil.move(output, here + "/" + out_dir)
        os.chdir(here + "/" + out_dir)
        os.chdir(here)

    if remove_csv:
        os.chdir(out_dir)

        # Suppression des fichiers csv ayant servis pour la concaténation
        for file in os.listdir():
            if file.endswith("csv"):
                os.remove(file)

    os.chdir(here)

    if trans_vid == False & remove_csv == False & remove_results == False:
        os.chdir(here)
        shutil.rmtree(out_dir)

    os.chdir(here)
    return frame


vid_to_csv(
    "multi_face.avi",
    trans_vid=True,
    remove_csv=True,
    remove_results=False,
)

print(f"Temps d'exécution du programme : {np.round(time.time() - now, 5)} secondes.")
