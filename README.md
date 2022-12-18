# Sintetizador_Concatenativo_de_Difonos

## 1. Generar difonos
Correr el programa 0_Corpus_Library_Generation.py para generar los difonos si no están ya generados en la carpeta auxiliar/diphones.

Esto generará los difonos de los audios que pertenecen al lenguaje que vamos a procesar. Tener en cuenta que serán generados de la forma:  nombredepalabra_n_difono donde n es el lugar del difono (ejemplo para efre generará e-ef-fr-e donde n(e) = 0, n(ef) = 1...).

## 2. Generar Corpus
En la carpeta auxiliar/corpus se encuentran los difonos, se ha cogido un sonido por difono y se ha simplificado el nombre a difono.wav (para efre -> e.wav, fr.wav...). Si una palabra tenía una vocal acentuada se ha usado la mayuscula acompañado de '_'. Es decir si tenemos:
- EfrE -> E_.wav, E_f.wav, fr.wav, rE_.wav, E_.wav, al ya tener E_.wav el ultimo no se guardará como difono
- efre -> e.wav, ef.wav, fr.wav, re.wav, e.wav

## 3. Sintetizar sonido
Correr el programa 1_Synthesizer.py. La consola pedirá introducir el sonido que queremos obtener y al introducirlo lo sintetizará.