'''
4. TODO Crear un programa que, dada una secuencia de fonos, concatene los archivos de los
    difonos correspondientes, genere un archivo wav y (de ser necesario) modifique su
    prosodia.

    • El programa debe funcionar en modo batch (no interactivo), recibiendo como
    únicos argumentos la secuencia de fonos a sintetizar y el nombre del archivo
    wav a crear. Ejemplo:

    python tts.py EsemeketrEfe? /tmp/output.wav

    • La salida debe guardarse como un archivo wav (mono, 16kHz, 16 bits).
    • TODO El programa tendrá además dos opciones
        i.  Reproducir automáticamente el audio
        ii. no reproducir automáticamente el audio.
'''

#                                                       Libraries
import os
import shutil
import sys
import math

# to use praat
import parselmouth
from parselmouth import Sound, praat, TextGrid

#                                                    Constants
corpus_folder = "auxiliar" + os.sep + "corpus"
script_folder = "auxiliar" + os.sep + "scripts"     #"manipular-pitch"
labeled_intervals_to_wav = "save_labeled_intervals_to_wav_sound_files.praat"
extraer_pitch_track = "extraer-pitch-track.praat"
reemplazar_pitch_track = "reemplazar-pitch-track.praat"

synthetized_folder = "auxiliar" + os.sep + "synthetized"

#                                                   Auxiliar Functions

def empty_folder(folder):
    '''
    Delete all files in the folder
    :param folder:
    :return:
    '''

    if os.path.exists(folder):
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print('Error al borrar %s. Razon: %s' % (file_path, e))
    else:
        print("La carpeta " + folder + " no existe, por lo que no se puede vaciar")
        print("Continuando con la ejecucion...")

def check_constraints(text, corpus_folder=corpus_folder, praat_scripts=script_folder,
                      synthetized_folder=synthetized_folder):
    # 1. Check if folders exists
    assert os.path.exists(corpus_folder) & os.path.exists(praat_scripts), \
        "No podemos seguir con el programa por no localizar la carpeta con los Difonos"

    string_to_find = []

    # L there are two phonetic restrictions:
    #       - sound r cannot be initial in a sentence
    #       - sound of r cannot follow an [s]
    found = False  # if there is a 'r' followed by an 's' or 'r' is initial in a sentence

    iterations = len(text) - 1  # len of introduced string (text)
    index = 0

    # 2. Check the constraints of the language L

    # 2.1. if 'r' is initial in a sentence
    if "-r" == text[0:2]:
        found = True

    while index < iterations and not found:
        # 2.2. 'r' followed by an 's'
        if "r" == text[index] and text[index + 1] == "s":
            found = True

        if found and ((index + 2) < iterations):
            break

        string_to_find = string_to_find + [(text[index] + text[index + 1])]

        index += 1

    return found, string_to_find


def create_sound(text, textfile, source, destination):
    praat = ""
    praat2 = ""

    # empty destination folder
    empty_folder(destination)

    # get path of tmp and results folders
    destination_tmp = destination + os.sep + "tmp"
    destination_results = destination + os.sep + "results"

    # create the necessary  subdirectories from the destination folder
    os.mkdir(destination_tmp)
    os.mkdir(destination_results)

    # for every diphone in the string text
    for i in range(0, len(text)):
        diphone = text[i]
        # if the diphone was the starting or the end it will have a '-' at beginning or ending respectively,
        # so we will replace for nothing, so instead of "-e" we will have "e"
        diphone = diphone.replace("-", "")

        # try to open the diphone (.wav) audio file and copy yo the destination tmp folder
        try:
            file_name = diphone + ".wav"
            if "E" in diphone:
                file_location = source + os.sep + file_name.replace("E", "E_")
                # print(file_location) -> check what files have an accent (E)
            else:
                diphone.lower()  # Para ponerlo en minúscula
                file_location = source + os.sep + file_name

            # copy diphone to tmp folder
            shutil.copyfile(file_location, destination_tmp + os.sep + "%s.wav" % i)

        except:
            raise Exception("Archivo no encontrado: " + file_name)

        # Script de PRAAT
        file = destination_tmp + os.sep + "%s.wav" % i
        praat += "Read from file... %s\n" % file

        if i == 0:
            praat2 += "select Sound %s\n" % i
        else:
            praat2 += "plus Sound %s\n" % i

    praat3 = "Concatenate with overlap... 0.0005\n"
    praat3 += "Resample... 16000 16\n"                  # 16kHz, 16 bits
    praat3 += "Write to WAV file... %s" % "results" + os.sep + textfile

    praat_script = "%s\n%s\n%s" % (praat, praat2, praat3)

    name = textfile.split(".")[0]

    # write praat script and save it in tmp folder
    praat_file_path = destination + os.sep + name + ".praat"
    f = open(praat_file_path, "w")
    f.write(praat_script)
    f.close()

    # run praat script
    os.system("Praat.exe" +
              " ." + os.sep + synthetized_folder + os.sep + name + ".praat")

    '''source_wav = destination_results + os.sep + textfile
    print(source_wav)
    result_dir = os.getcwd() + os.sep + synthetized_folder + os.sep + textfile

    shutil.copyfile(source_wav, result_dir)'''

    # empty and delete tmp folder
    empty_folder(destination_tmp)
    os.rmdir(destination_tmp)
    # delete praat script
    os.remove(praat_file_path)


def modify_prosody(filename_wav):
    name = filename_wav.split(".")[0]   # file.wav -> file / wav where file = [0] and wav = [1]

    # set path results folder
    syn_results_folder = "synthetized" + os.sep + "results"

    # extract original pitchtier
    os.system("Praat.exe" +
              " ." + os.sep + script_folder + os.sep + extraer_pitch_track +
              " .." + os.sep + syn_results_folder + os.sep + filename_wav +  # from where to take the source
              " .." + os.sep + syn_results_folder + os.sep + name + ".PitchTier 50 400")  # where to save it

    # modify pitchtier
    file = open(synthetized_folder + os.sep + "results" + os.sep + name + ".PitchTier", "r")

    lines = []

    for line in file:
        lines.append(line)

    Pointsline = lines[5].split(" = ")
    PointsNum = Pointsline[1]

    start = 0
    end = math.floor(float(PointsNum) * 0.2)

    for idx in range(start, end):
        l = 8 + (3 * (idx))
        data = lines[l].split(" = ")
        value = data[1]
        finalValue = float(value) + (5 * (idx + 1))
        lines[l] = data[0] + " = " + str(finalValue) + "\n"

    start = math.floor(float(PointsNum) * 0.7)
    end = int(PointsNum)

    for i in range(start, end):
        l = 8 + (3 * (i))
        data = lines[l].split(" = ")
        value = data[1]
        finalValue = float(value) + (11 * (i + 1))
        lines[l] = data[0] + " = " + str(finalValue) + "\n"

    praat = ""
    for i in range(0, len(lines)):
        praat += lines[i]

    # write PitchTier modified file
    f = open(synthetized_folder + os.sep + "results" + os.sep + name + "_modified.PitchTier", "w")
    f.write(praat)
    f.close()

    # run script to replace pitch track
    os.system(
        "Praat.exe" +
        " " + script_folder + os.sep + reemplazar_pitch_track +
        " .." + os.sep + syn_results_folder + os.sep + filename_wav +   # file_wav_in .wav
        " .." + os.sep + syn_results_folder + os.sep + name + "_modified.PitchTier" +   # file_PitchTier_in .PitchTier
        " .." + os.sep + syn_results_folder + os.sep + name + "_modified.wav"   # file_wav_out .wav
        " 50"
        " 400")


# flag to check if the sentence is a prosody
prosody = False

# ask for text
text = input("\nInserte el texto a reproducir : ")

# check that the number of arguments is as expected
assert len(sys.argv) != 3, \
    "Error en el número de argumentos, deben ser 2"

prosody = "?" in text

# if prosody, we already have the flag so we just take the word to synthesize
if prosody:
    text = text.split("?")[0]

# filename with the requested text audio
filename_wav = str(text + ".wav")
text = "-" + text + "-"

# check that the string fulfills the constraints
constraints, text = check_constraints(text)
assert not constraints, "La cadena introducida no cumple con los requisitos del lenguaje"

# set destination and source folders
destination = os.getcwd() + os.sep + synthetized_folder
source = os.getcwd() + os.sep + corpus_folder

# create sound taking the diphones from source and saving it in destination
create_sound(text, filename_wav, source, destination)

if prosody:
    print("Creating prosody...")
    modify_prosody(filename_wav)
else:
    name = filename_wav.split(".")[0]
    os.system("Praat.exe" +
              " ." + os.sep + script_folder + os.sep + "extraer-pitch-track.praat" +
              " .." + os.sep + "synthetized" + os.sep + "results" + os.sep + filename_wav +
              " .." + os.sep + "results" + os.sep + name + ".PitchTier 50 400")
