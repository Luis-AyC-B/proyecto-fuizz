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

    