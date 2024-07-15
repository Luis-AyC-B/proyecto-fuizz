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
