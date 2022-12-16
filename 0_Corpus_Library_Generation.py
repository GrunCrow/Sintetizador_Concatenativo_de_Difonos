'''
1. Diseñar y grabar el inventario de sonidos (difonos), en mono, 16kHz, 16 bits.
2. En Praat, etiquetar los difonos en una capa de intervalos (interval tier) en un archivo TextGrid.
3. Recortar los difonos y generar un archivo wav para cada uno.
'''

# Instalación de bibliotecas

#                                                       Libraries
import os
import shutil

# to use praat
import parselmouth
from parselmouth import Sound, praat, TextGrid

#                                                       Constants

#                               DICTIONARY

# Phones
v = ["e"]  # vowel -> if with accent = E, without accent = e
c = ["f", "k", "m", "R", "s", "t"]  # consonants

# syllables
cv = ["fe", "ke", "me", "re", "se", "te"]
ccv = ["fre", "kre", "tre"]  # f, k , t + liquid consonant r + vowel (e)
vc_cvc_ccvc = ["es", "fes", "kes", "mes", "res", "ses", "tes", "fre", "kre",
               "tre"]  # resultantes de agregar [s] final a los tres tipos anteriores: [es], [fes],[fres], etc.

dictionary = v + cv + ccv + vc_cvc_ccvc

# L there are two phonetic restrictions:
#       - sound r cannot be initial in a sentence
#       - sound of r cannot follow an [s]

# one instance of each diphone -> no unit selection when synthesising a new sentence

# ==========================================================================

corpus_folder = "corpus/"
auxiliar_folder = "auxiliar/"
labeled_intervals_to_wav = "save_labeled_intervals_to_wav_sound_files.praat"


#                                                   Auxiliar Functions

def empty_folder(folder):
    '''
    Delete all files in the folder
    :param folder:
    :return:
    '''
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))

def get_files_from_folder(folder, ext):
    audiofiles = []
    for file in os.listdir(folder):
        if file.endswith(ext):
            audiofiles.append(folder + file)
    return audiofiles


def get_marks_content(file):
    '''
    Get the content of a mark file in a dictionary

    :param file: filename with the path
    :return: file_content_dictionary, dictionary with the content of the filename

    '''

    filename = open(file, 'r')
    Lines = filename.readlines()

    # how we are going to split the data of the file
    file_content_dictionary = {
        "time": [],
        "type": [],
        "start": [],
        "end": [],
        "value": []
    }

    for string in Lines:

        # clean characters that we dont want to use
        string = string.replace("{", "")
        string = string.replace("}", "")
        string = string.replace("\"", "")
        string = string.replace("\n", "")

        # split by each value
        str_content = string.split(",")

        # for each content of the string, add it to the dict
        for idx, content in enumerate(str_content):
            # if we have "time":125 we will save the value of the str (125), as we are separating it in 2, by the :
            content_key_from_dict = str_content[idx].split(":")[0]
            content_value = str_content[idx].split(":")[1]

            file_content_dictionary[content_key_from_dict].append(content_value)

    return file_content_dictionary


def get_parameters_from_dictionary(content_dictionary, line_to_start=14):
    n_file_lines = len(content_dictionary["time"])

    # value = []
    start_time = []
    end_time = []

    flag_founded = False
    for line in range(line_to_start, n_file_lines - 1):
        if content_dictionary["type"][line] != "word":

            # value.append(content_dictionary["value"][line])

            start_time.append((int(content_dictionary["time"][line])) / 1000)
            end_time.append(int((content_dictionary["time"][line + 1])) / 1000)
        else:
            flag_founded -= True

        if flag_founded: break

    next_start_time = ((int(content_dictionary["time"][line + 1])) / 1000)
    next_end_time = (int((content_dictionary["time"][line + 2])) / 1000)

    return start_time, end_time, next_start_time, next_end_time


def fix_diphones(start, end):
    for idx in range(0, len(start)):

        end_item = (start[idx] + end[idx]) / 2

        if idx != 0:
            start_item = end[idx-1]
        else:
            start_item = start[idx]

        if idx + 1 == len(start):
            start.append(end_item)
            end.append(end[idx])

        start[idx] = start_item
        end[idx] = end_item

    return start, end


def fix_value(values):

    aux = None
    for idx, value in enumerate(values):
        if idx != 0:
            value_item = aux + value
            aux = value
        else:
            value_item = value
            aux = value

        values[idx] = value_item

    values.append(value)

    return values


def callPraatScript(file_name, script_name, start_interval, end_interval, folder, saving_name):
    # Check that all the parameters exists
    assert os.path.exists(file_name) and os.path.exists(script_name), "ERROR"

    # constant parameters for the script
    tier = 1  # (int) Which IntervalTier in this TextGrid would you like to process?
    Start_from = start_interval  # (int) Starting at which interval?
    End_at = end_interval  # (int) ending at which interval?
    Exclude_empty_labels = True  # (boolean)
    Exclude_intervals_labeled_as_xxx = True  # (boolean)
    Exclude_intervals_starting_with_dot = True  # (boolean)
    positive_Margin = 0.0001  # (float) Give a small margin for the files if you like (seconds)
    sentence_Folder = folder  # Give the folder where to save the sound files
    sentence_Prefix = saving_name  # Give an optional prefix for all filenames:
    sentence_Suffix = ""  # Give an optional suffix for all filenames (.wav will be added anyway):

    # parameters = [tier, Start_from, End_at, Exclude_empty_labels, Exclude_intervals_labeled_as_xxx,
    #              Exclude_intervals_starting_with_dot, positive_Margin, sentence_Folder, sentence_Prefix,
    #              sentence_Suffix]

    snd = Sound(file_name)
    # snd.save("tests/test.wav","WAV")

    tgt = TextGrid(float(start_interval), float(end_interval), "Mary John bell", "bell")
    # tgt.save("tests/test.TextGrid")

    objects = [tgt, snd]

    # So the everything before the script (script_name) are selected objects, Everything after are arguments to this form
    praat.run_file(objects, script_name, tier, Start_from, End_at, Exclude_empty_labels,
                   Exclude_intervals_labeled_as_xxx, Exclude_intervals_starting_with_dot,
                   positive_Margin, sentence_Folder, sentence_Prefix, sentence_Suffix)

#                                               MAIN FUNCTIONS
def create_diphones(path_to_files, script_name, saving_folder):

    marks_files = get_files_from_folder(path_to_files, ".marks")

    '''marks_files = []
    f1 = "auxiliar/Frases para Extracción de Difonos/Efre.marks"
    f2 = "auxiliar/Frases para Extracción de Difonos/emEkre.marks"
    marks_files.append(f1)
    marks_files.append(f2)'''

    for file in marks_files:

        file_content_dictionary = get_marks_content(file)

        file = file.replace(".marks", ".mp3")

        filename = file.split("/")[2].replace(".mp3", "")

        start, end, next_start, next_end = get_parameters_from_dictionary(file_content_dictionary, 14)

        # print(start, end)

        # to change values from the array to start - start+end/2
        start, end = fix_diphones(start, end)

        # print(start, end)

        assert len(start) == len(end)

        value = []
        for item in filename:
            value.append(item)

        value = fix_value(value)

        assert len(value) == len(start)

        file.replace(".mp3", "")

        print("====================================================")
        print(filename)
        print("====================================================")
        # process all
        for idx in range(len(start)):
            if idx < len(value):
                phone = value[idx]

            saving_name = filename + "_" + str(idx) + "_" + phone

            '''diphone_to_check = saving_name.split(str(idx))[1] + ".wav"
            print(diphone_to_check)'''

            # print(idx, saving_name)

            print(phone, round(float(start[idx]), 3), round(float(end[idx]), 3))

            callPraatScript(file, script_name, float(start[idx]), float(end[idx]), saving_folder, saving_name)

            '''if (idx+1) % 2 == 0:
                tier = tier + 1'''
        print("\n")
            # callPraatScript(file, script_name, float(start[idx]), float(end[idx]), saving_folder, saving_name)


#                                           RUN THE PROGRAM
path_to_files = "auxiliar/Frases para Extracción de Difonos/"
script_name = "auxiliar/save_labeled_intervals_to_wav_sound_files.praat"
saving_folder = "diphones/"

folder = "auxiliar/" + saving_folder

# As diphones are already created we wont run it again, so we will comment those lines, to generate them, decomment
empty_folder(folder)
create_diphones(path_to_files, script_name, saving_folder)

