from __future__ import unicode_literals
from os.path import abspath, join, dirname
import random
"""
Created on 25 February 2017
.. module:: name
	:platform: Unix, Windows
	:synopsis: Random Name Generator
.. projectauthor:: Raghav Khandelwal <LIT2015002>

Module used to generate random number from a list of available first and last names of both gender, Male and Female and return the generated name to the calling function.

:Dependencies: 'last.txt', 'male.txt', 'female.txt'

:Example: 

>>>from name import get_full_name
>>>get_full_name('female')
Alexia Carter

"""
full_path = lambda filename: abspath(join(dirname(__file__), filename))

FILES = {
	'first:male': full_path('male.txt'),
	'first:female': full_path('female.txt'),
	'last': full_path('last.txt'),
}

def get_name(filename):
	selected = random.random() * 90
	with open(filename) as name_file:
		for line in name_file:
			name, _, cummulative, _ = line.split()
			if float(cummulative) > selected:
				return name
	return ""  # Return empty string if file is empty

def get_first_name(gender=None):
	if gender is None:
		gender = random.choice(('male', 'female'))
	if gender not in ('male', 'female'):
		raise ValueError("Only 'male' and 'female' are supported as gender")
	return get_name(FILES['first:%s' % gender]).capitalize()

def get_last_name():
	return get_name(FILES['last']).capitalize()


def get_full_name(gender=None):
	return "{0} {1}".format(get_first_name(gender), get_last_name())