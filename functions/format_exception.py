import traceback
from termcolor import colored


def error():
	print(colored(traceback.format_exc()))
