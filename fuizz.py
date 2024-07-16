import sys
import argparse
import signal
import requests
from tqdm import tqdm
from termcolor import colored
from threading import Thread, lock
import json

running = True

def def_hundler(sig, frame):
    global running
    print(colored("[!] Saliendo del programa...", 'red'))
    running = False
    sys.exit(1)

signal.signal(signal.SIGINT, def_hundler)

parser = argparse.ArgumentParser(description="Fuzzing")
parser.add_argument("url", help="Proporcionar una URL")
parser.add_argument("diccionario", help="Proporcionar un diccionario")
parser.add_argument("--threads", type=int, default=10, help="Número de hilos concurrentes (por defecto: 10)")
parser.add_argument("--headers", type=str, help="Cabeceras en formato JSON")
parser.add_argument("--data", type=str, help="Datos del cuerpo de la solicitud en formato JSON")
parser.add_argument("--show_headers", action="store_true", help="Mostrar cabeceras de la respuesta")
parser.add_argument("--show_body", action="store_true", help="Mostrar cuerpo de la respuesta")
args = parser.parse_args()

with open(args.diccionario) as file:
    wordlist = file.read().splitlines()

barra = tqdm(total=len(wordlist), desc="Progreso", unit="urls", dynamic_ncols=True)
found_directories = []
lock = Lock()

def fuzzing(url, wordlist, headers=None, data=None):
    global running
    for linea in wordlist:
        if not running:
            break
        if '#' in linea:
            with lock:
                barra.update(1)
            continue
        url_completa = url + linea
        try:
            response = requests.get(url_completa, headers=headers, data=data)
            if response.status_code == 200:
                with lock:
                    found_directories.append(url_completa)
                    size = len(response.contet)
                    tqdm.write("Directorios encontrados: " + colored(f"{url_completa}" + " Tamnio Res.:"+colored(f"{size}"), "green"))

                     if show_headers:
                        tqdm.write("Cabeceras:")
                        for key, value in response.headers.items():
                            tqdm.write(f"{key}: {value}")
                    
                    
                    if show_body:
                        tqdm.write("Cuerpo de la respuesta:")
                        tqdm.write(response.text)

        except requests.RequestException as e:
            tqdm.write(colored(f"Error al acceder a {url_completa}: {e}", "red"))
        finally:
            with lock:
                barra.update(1)

chunk_size = len(wordlist) // args.threads
threads = []

headers = None
data = None

if args.headers:
    headers = json.loads(args.headers)
if args.data:
    data = json.loads(args.data)

try:
    for i in range(args.threads):
        start = i * chunk_size
        end = (i + 1) * chunk_size if i != args.threads - 1 else len(wordlist)
        thread = Thread(target=fuzzing, args=(args.url, wordlist[start:end], headers, data))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

finally:
    barra.close()

if found_directories:
    print("\nDirectorios encontrados:")
    for directory in found_directories:
        print(directory)
else:
    print("\nNo se encontraron directorios.")