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

#                                   Libraries
import os

#                                   Constants
corpus_folder = "corpus"
auxiliar_folder = "auxiliar"
labeled_intervals_to_wav = "save_labeled_intervals_to_wav_sound_files.praat"

variable = "test" # variable de test para probar git push

def callPraatScript(file_name, script_name=auxiliar_folder + labeled_intervals_to_wav):
    # Check that all the parameters exists
    assert os.path.exists(file_name) and os.path.exists(script_name)


    os.system("Praat.exe " + script_name + " " + file_name)
