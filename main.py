'''
1. TODO Diseñar y grabar el inventario de sonidos (difonos), en mono, 16kHz, 16 bits.
2. TODO En Praat, etiquetar los difonos en una capa de intervalos (interval tier) en un archivo TextGrid.
3. TODO Recortar los difonos y generar un archivo wav para cada uno.
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

# Instalación de bibliotecas

#                                                       Libraries
import os

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

# todo generalizar funcion para cualquier script -> meter todos los datos en listas para que corra de cualquier manera
def callPraatScript(file_name, script_name):
    """
    callPraatScript

    call the Praat Script script_name and runs it on the sound file file_name. It is run in one by one sound file, so
    if you want to run it on several sound files, just call it several times on different sound files.

    :param file_name: path + name of the sound file (.wav)
    :param script_name: path + name of the script file (.praat)
    :return: resulting_objects: list of objects results of the script
    """
    # Check that all the parameters exists
    assert os.path.exists(file_name) and os.path.exists(script_name), "ERROR"

    # constant parameters for the script
    tier = 1  # (int) Which IntervalTier in this TextGrid would you like to process?
    start_from = 1  # (int) Starting at which interval?
    end_at = 0  # (int) ending at which interval?
    exclude_empty_labels = True  # (boolean)
    exclude_intervals_labeled_as_xxx = True  # (boolean)
    exclude_intervals_starting_with_dot = True  # (boolean)
    positive_margin = 0.0001  # (float) Give a small margin for the files if you like (seconds)
    sentence_folder = "corpus/"  # Give the folder where to save the sound files
    sentence_prefix = "TMP_"  # Give an optional prefix for all filenames:
    sentence_suffix = ""  # Give an optional suffix for all filenames (.wav will be added anyway):

    # parameters = [tier, Start_from, End_at, Exclude_empty_labels, Exclude_intervals_labeled_as_xxx,
    #              Exclude_intervals_starting_with_dot, positive_Margin, sentence_Folder, sentence_Prefix,
    #              sentence_Suffix]

    snd = Sound(file_name)
    # snd.save("tests/test.wav","WAV")

    tgt = TextGrid(0, 1, "Mary John bell", "bell")
    # tgt.save("tests/test.TextGrid")

    objects = [tgt, snd]

    # So everything before the script (script_name) are selected objects, everything after are arguments to this
    # form
    resulting_objects = praat.run_file(objects, script_name, tier, start_from, end_at, exclude_empty_labels,
                                       exclude_intervals_labeled_as_xxx, exclude_intervals_starting_with_dot,
                                       positive_margin, sentence_folder, sentence_prefix, sentence_suffix)

    # assert that resulting_objects is not empty
    assert resulting_objects

    # if we want to save the results in the folder tests/Results_idx + .TextGrid
    for idx, resulting_object in enumerate(resulting_objects):
        resulting_objects[idx].save("tests/result_" + str(idx) + ".TextGrid")

    return resulting_objects


# test the function
file_name = "auxiliar/manipular-pitch/12345.wav"
script_name = "auxiliar/save_labeled_intervals_to_wav_sound_files.praat"

resulting_textgrid = callPraatScript(file_name, script_name)
print(resulting_textgrid)
