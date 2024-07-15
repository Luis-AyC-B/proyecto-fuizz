import sys
import argparse
import signal
import requests
from tqdm import tqdm
from termcolor import colored

def def_hundler(sig, frame):
    print(colored("[!] Saliendo del programa...", 'red'))
    sys.exit(1)
signal.signal(signal.SIGINT, def_hundler)

parser = argparse.ArgumentParser(description="Fuzzing")
parser.add_argument("url", help="Proporcionar una url")
parser.add_argument("diccionario", help="Proporcionar un diccionario")
args = parser.parse_args()

with open(args.diccionario) as file:
    wordlist = file.read().splitlines()

try:
    barra = tqdm(total=len(wordlist), desc="Progreso", unit="urls", dynamic_ncols=True)
    for linea in wordlist:
        url_completa = args.url + linea
        response = requests.get(url_completa)
        if response.status_code == 200:
            tqdm.write("Directorios encontrados: " + colored(f"{url_completa}", "green"))
            barra.update(1)
    
finally :
    barra.close()
