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

# to use praat
import parselmouth
from parselmouth import Sound, praat, TextGrid

#                                                    Constants
corpus_folder = "auxiliar" + os.sep + "corpus"
script_folder = "auxiliar" + os.sep + "manipular-pitch"
labeled_intervals_to_wav = "save_labeled_intervals_to_wav_sound_files.praat"
synthetized_folder = "auxiliar" + os.sep + "synthetized"
tmp_synthetized_folder = synthetized_folder + os.sep + "tmp"


#                                                   Auxiliar Functions

def empty_folder(folder):
    '''
    Delete all files in the folder
    :param folder:
    :return:
    '''

    assert os.path.exists(folder), folder

    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))


def check_constraints(text, corpus_folder=corpus_folder, praat_scripts=script_folder, synthetized_folder=synthetized_folder):
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

    # for every diphone in the string text
    for i in range(0, len(text)):
        diphone = text[i]
        # if the diphone was the starting or the end it will have a '-' at beg or ending respectively,
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

            shutil.copyfile(file_location, destination + os.sep + "tmp" + os.sep + "%s.wav" % i)

        except:
            raise Exception("Archivo no encontrado: " + file_name)

        # Script de PRAAT
        archivo = destination + os.sep + "tmp" + os.sep + "%s.wav" % i
        praat += "Read from file... %s\n" % archivo

        if i == 0:
            praat2 += "select Sound %s\n" % i
        else:
            o = i + 1
            praat2 += "plus Sound %s\n" % i

    praat3 = "Concatenate with overlap... 0.0005\n"
    praat3 += "Resample... 16000 16\n"
    praat3 += "Write to WAV file... %s" % "results" + os.sep + textfile

    praat_script = "%s\n%s\n%s" % (praat, praat2, praat3)

    name = textfile.split(".")[0]

    # write praat script and save it
    praat_file = destination + os.sep + name + ".praat"
    f = open(praat_file, "w")
    f.write(praat_script)
    f.close()

    # run praat script
    os.system("Praat.exe " + "." + os.sep + synthetized_folder + os.sep + name + ".praat")

    source_wav = destination + os.sep + "results" + os.sep + textfile
    print(source_wav)
    result_dir = os.getcwd() + os.sep + synthetized_folder + os.sep + textfile

    shutil.copyfile(source_wav, result_dir)


# flag to check if the sentence is a prosody
prosody = False

# empty trash from folder where to save the audios (tmp folder)
empty_folder(tmp_synthetized_folder)

# ask for text
text = input("\nInserte el texto a reproducir : ")
prosody = "?" in text

# check that the number of arguments is as expected
assert len(sys.argv) != 3,\
    "Error en el número de argumentos, deben ser 2"

if prosody:
    text.split("?")[0]

# filename with the requested text audio
textfile = str(text + ".wav")
text = "-" + text + "-"

# check that the string fulfills the constraints
constraints, text = check_constraints(text)
assert not constraints, "La cadena introducida no cumple con los requisitos del lenguaje"

# set folder to destination and source
destination = os.getcwd() + os.sep + synthetized_folder
source = os.getcwd() + os.sep + corpus_folder

create_sound(text, textfile, source, destination)


