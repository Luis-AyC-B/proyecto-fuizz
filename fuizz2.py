import sys
import argparse
import signal
import requests
from tqdm import tqdm
from termcolor import colored
from threading import Thread, Lock
import json
from fake_useragent import UserAgent  


running = True

def def_handler(sig, frame):
    global running
    print(colored("[!] Saliendo del programa...", 'red'))
    running = False
    sys.exit(1)

signal.signal(signal.SIGINT, def_handler)

parser = argparse.ArgumentParser(description="Fuzzing")
parser.add_argument("url", help="Proporcionar una URL")
parser.add_argument("diccionario", help="Proporcionar un diccionario")
parser.add_argument("--threads", type=int, default=10, help="Número de hilos concurrentes (por defecto: 10)")
parser.add_argument("--fuzz_headers", action="store_true", help="Activar fuzzing en cabeceras")
parser.add_argument("--headers", type=str, help="Cabeceras en formato JSON")
args = parser.parse_args()

with open(args.diccionario) as file:
    wordlist = file.read().splitlines()

barra = tqdm(total=len(wordlist), desc="Progreso", unit="urls", dynamic_ncols=True)
found_directories = []
lock = Lock()

ua = UserAgent()  

def fuzzing(url, wordlist, headers=None):
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
            user_agent = ua.random  
            headers['User-Agent'] = user_agent  
            print(user_agent)
            response = requests.get(url_completa, headers=headers)
            with lock:
                barra.update(1)
                if response.status_code == 200:
                    found_directories.append((url_completa, response.status_code))  
                    tqdm.write("Directorios encontrados: " + colored(f"{url_completa}", "green"))
                    tqdm.write("Código de estado: " + colored(f"{response.status_code}", "blue"))
               
        except requests.RequestException as e:
            with lock:
                tqdm.write(colored(f"Error al acceder a {url_completa}: {e}", "red"))

chunk_size = len(wordlist) // args.threads
threads = []

headers = {}

if args.headers:
    headers = json.loads(args.headers)

try:
    for i in range(args.threads):
        start = i * chunk_size
        end = (i + 1) * chunk_size if i != args.threads - 1 else len(wordlist)
        thread = Thread(target=fuzzing, args=(args.url, wordlist[start:end], headers.copy()))  # Pasamos una copia de las cabeceras
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

finally:
    barra.close()

if found_directories:
    print("\nDirectorios encontrados:")
    for directory, status_code in found_directories:
        print(f"URL: {directory}")
        print(f"Código de estado: {status_code}")
        print()
else:
    print("\nNo se encontraron directorios.")