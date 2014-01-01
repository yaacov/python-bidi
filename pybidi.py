#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# Copyright (C) 2008 Yaacov Zamir <kzamir_a_walla.co.il>

# Partial implementation of Unicode Bidirectional Algorithm
# http://www.unicode.org/unicode/reports/tr9/
# test cases from http://imagic.weizmann.ac.il/~dov/freesw/FriBidi/

# Algorithm parts implemented -
# 1. 3 levels of bidi nesting
# 2. can recognize bidi-types of Hebrew and Latin chars
# 3. implement bidi mirror of () and <>

import string
import sys

def bidi_char_type(ch, uper_is_rtl = False):
	''' partialy implements Bidirectional Character Types, Unicode 5.1.0
	
	L  	Left-to-Right  									Latin alphabet
	R  	Right-to-Left  									Hebrew alphabet, and related punctuation
	
	EN  European Number European 				Digits
	ES  European Number Separator  			Plus sign, minus sign
	CS  Common Number Separator  				Colon,  comma, full stop (period)
	
	WS  Whitespace  										Space
	ON  Other Neutrals  								All other characters
	'''
	
	# lower case latin
	if ch >= u'a' and ch <= u'z':
		return 'L '
		
	# uper case latin
	if ch >= u'A' and ch <= u'Z':
		if uper_is_rtl:
			return 'R '
		else:
			return 'L '
	
	# hebrew
	if ch >= u'×' and ch <= u'×ª':
		return 'R '
		
	# numbers
	if ch >= u'0' and ch <= u'9':
		return 'EN'
	
	# plus, minus
	if ch == u'-' or ch == u'+' or ch == u'/' or ch == u'*' or ch == u'^' or ch == u'%':
		return 'ES'
		
	# number separator
	if ch == u',' or ch == u'.' or ch == u':':
		return 'CS'
		
	# white space
	if ch == u' ':
		return 'WS'
		
	# all other
	return 'ON'

def paragraph_level (in_string, uper_is_rtl = False):
	''' partialy implements Find the Paragraph Level, Unicode 5.1.0 '''
	
	# P2: Unicode 5.1.0
	for i in range (0, len(in_string)):
		if bidi_char_type(in_string[i], uper_is_rtl) == 'R ':
			return 'R '
		elif bidi_char_type(in_string[i], uper_is_rtl) == 'L ':
			return 'L '
			
	# default to L
	return 'L '

def eor_level (in_string, uper_is_rtl = False):
	''' partialy implements Find the Paragraph Level, Unicode 5.1.0 '''
	
	# not in Unicode 5.1.0
	for i in range (len(in_string) -1, -1, -1):
		if bidi_char_type(in_string[i], uper_is_rtl) == 'R ':
			return 'R '
		elif bidi_char_type(in_string[i], uper_is_rtl) == 'L ':
			return 'L '
			
	# default to L
	return 'L '
	
def resolve_weak_types (char_type_array, embed_level):
	''' partialy implements Resolving Weak Types, Unicode 5.1.0 '''
	
	# W4: Unicode 5.1.0
	for i in range (1, len(char_type_array) - 1):
		prev_type = char_type_array[i - 1]
		curr_type = char_type_array[i - 0]
		next_type = char_type_array[i + 1]
		
		if (curr_type == 'ES' or curr_type == 'CS') and \
			(prev_type == 'EN' and next_type == 'EN'):
			char_type_array[i] = 'EN'
	
	# W5: Unicode 5.1.0
	for i in range (0, len(char_type_array)):
		curr_type = char_type_array[i]
		
		if (curr_type == 'ES' or curr_type == 'CS'):
			char_type_array[i] = 'ON'
			
	# W7: Unicode 5.1.0
	last_strong_type = embed_level
	for i in range (0, len(char_type_array)):
		curr_type = char_type_array[i]
		if curr_type == 'L ' or curr_type == 'R ':
			last_strong_type = curr_type
		
		if curr_type == 'EN' and last_strong_type == 'L ':
			char_type_array[i] = 'L '

	
def resolve_neutral_types (char_type_array, embed_level, eor):
	''' partialy implements Resolving Neutral Types, Unicode 5.1.0 '''
	
	# find eor type
	
	# N1: Unicode 5.1.0
	for i in range (1, len(char_type_array) - 1):
		prev_type = char_type_array[i - 1]
		curr_type = char_type_array[i - 0]
		
		j = i + 1
		next_type = char_type_array[j]
		while j < len(char_type_array) and (next_type == 'WS' or next_type == 'ON'):
			next_type = char_type_array[j]
			j = j + 1
		if j == len(char_type_array):
			next_type = eor
			
		if prev_type == 'EN' : prev_type = 'R '
		if next_type == 'EN' : next_type = 'R '
		
		if curr_type == 'WS' or curr_type == 'ON':
			if prev_type == 'R ' and next_type == 'R ':
				char_type_array[i] = 'R '
			if prev_type == 'L ' and next_type == 'L ':
				char_type_array[i] = 'L '
				
	# N2: Unicode 5.1.0
	for i in range (0, len(char_type_array)):
		curr_type = char_type_array[i]
		
		if curr_type == 'WS' or curr_type == 'ON':
			char_type_array[i] = embed_level
		
def resolve_implicit_levels (char_type_array, embed_level):
	''' partialy implements Resolving Implicit Levels, Unicode 5.1.0
	we only implement levels 0,1 and 2'''
	
	# I1 + I2: Unicode 5.1.0
	for i in range (0, len(char_type_array)):
		curr_type = char_type_array[i]
		
		if embed_level == 'L ':
			if curr_type == 'L ':
				char_type_array[i] = '0 '
			if curr_type == 'R ':
				char_type_array[i] = '1 '
			if curr_type == 'EN':
				char_type_array[i] = '2 '
		else:
			if curr_type == 'L ':
				char_type_array[i] = '2 '
			if curr_type == 'R ':
				char_type_array[i] = '1 '
			if curr_type == 'EN':
				char_type_array[i] = '2 '
	
def reordering_resolved_levels (in_string, char_type_array):
	''' partialy implements Reordering Resolved Levels, Unicode 5.1.0 
	we only implement levels 0,1 and 2'''
	
	# L2: Unicode 5.1.0
	
	# reverse level 2
	i = 0
	while i < len(char_type_array):
		curr_type = char_type_array[i]
		
		if curr_type == '2 ':
			revers_start = i
			while i < len(char_type_array) and curr_type == '2 ':
				curr_type = char_type_array[i]
				i = i + 1
				
			if i < len(char_type_array) or curr_type != '2 ':
				revers_end = i - 2
			else:
				revers_end = i - 1
				
			in_string = reverse_string (in_string, revers_start, revers_end)
			i = i - 1
			
		i = i + 1
	
	# reverse level 1
	i = 0
	while i < len(char_type_array):
		curr_type = char_type_array[i]
		
		if curr_type == '1 ' or curr_type == '2 ':
			revers_start = i
			while i < len(char_type_array) and (curr_type == '1 ' or curr_type == '2 '):
				curr_type = char_type_array[i]
				i = i + 1
				
			if i < len(char_type_array) or curr_type == '0 ':
				revers_end = i - 2
			else:
				revers_end = i - 1
			
			in_string = reverse_string (in_string, revers_start, revers_end)
			i = i - 1
			
		i = i + 1
	
	return in_string

def reverse_string (in_string, start, end):
	''' just reverse string parts '''
	temp_string = map(lambda x:x, in_string)
	out_string = map(lambda x:x, in_string)
	
	for i in range(start, end + 1):
		out_string[i] = temp_string[start + end - i]
	
	return string.join(out_string, '')


def applay_bidi_mirrore (in_string, char_type_array):
	''' partialy implements Bidi_Mirrored, Unicode 5.1.0 '''
	out_string = map(lambda x:x, in_string)
	
	for i in range (0, len(char_type_array)):
		curr_type = char_type_array[i]
		
		if curr_type != '0 ':
			if out_string[i] == '(':
				out_string[i] = ')'
			elif out_string[i] == ')':
				out_string[i] = '('
			if out_string[i] == '<':
				out_string[i] = '>'
			elif out_string[i] == '>':
				out_string[i] = '<'
	
	return string.join(out_string, '')
	
def string_to_letters (in_string):
	''' string to letters array '''
	return map(lambda x: x + u' ', in_string)

def string_to_bidi_char_types (in_string, uper_is_rtl = False):
	''' string to bidi char types array '''
	return map(lambda x: bidi_char_type(x, uper_is_rtl), in_string)

def do_bidi (in_string, uper_is_rtl = False):
	''' wrapper for doing bidi on strings '''
	# get input
	char_array = string_to_letters (in_string)
	embed_level = paragraph_level (in_string, uper_is_rtl)
	eor = eor_level (in_string, uper_is_rtl)
	
	# get char types
	char_type_array  = string_to_bidi_char_types (in_string, uper_is_rtl)
	
	# resolve week char types
	resolve_weak_types (char_type_array, embed_level)
	
	# resolve neutral char types
	resolve_neutral_types (char_type_array, embed_level, eor)
	
	# resolve mplicit levels
	resolve_implicit_levels (char_type_array, embed_level)
	
	# applay bidi mirror
	out_string = applay_bidi_mirrore (in_string, char_type_array)

	# reorder string
	return reordering_resolved_levels (out_string, char_type_array)
	
def debug_string (in_string, uper_is_rtl = False):
	''' wrapper for doing bidi on strings with debug information output '''
	# get input
	char_array = string_to_letters (in_string)
	embed_level = paragraph_level (in_string, uper_is_rtl)
	eor = eor_level (in_string, uper_is_rtl)
	
	# get char types
	char_type_array  = string_to_bidi_char_types (in_string, uper_is_rtl)
	
	# print input string
	print string.join(char_array, '')
	print string.join(char_type_array, '')
	
	# resolve week char types
	resolve_weak_types (char_type_array, embed_level)
	print string.join(char_type_array, '')
	
	# resolve neutral char types
	resolve_neutral_types (char_type_array, embed_level, eor)
	print string.join(char_type_array, '')
	
	# resolve mplicit levels
	resolve_implicit_levels (char_type_array, embed_level)
	print string.join(char_type_array, '')
	
	# applay bidi mirror
	out_string = applay_bidi_mirrore (in_string, char_type_array)
	
	# reorder string
	out_string = reordering_resolved_levels (out_string, char_type_array)
	
	print in_string
	print out_string
	
	# print embed level
	print 'Paragraph level: ' + paragraph_level (in_string, uper_is_rtl) + eor_level (in_string, uper_is_rtl)

def do_tests ():
	''' do tests from http://imagic.weizmann.ac.il/~dov/freesw/FriBidi/
	car is THE CAR in arabic            => car is RAC EHT in arabic           
	CAR IS the car IN ENGLISH           =>           HSILGNE NI the car SI RAC
	he said "IT IS 123, 456, OK"        => he said "KO ,456 ,123 SI TI"       
	he said "IT IS (123, 456), OK"      => he said "KO ,(456 ,123) SI TI"     
	he said "IT IS 123,456, OK"         => he said "KO ,123,456 SI TI"        
	he said "IT IS (123,456), OK"       => he said "KO ,(123,456) SI TI"      
	HE SAID "it is 123, 456, ok"        =>        "it is 123, 456, ok" DIAS EH
	<H123>shalom</H123>                 =>                 <123H/>shalom<123H>
	<h123>SAALAM</h123>                 => <h123>MALAAS</h123>                
	HE SAID "it is a car!" AND RAN      =>      NAR DNA "!it is a car" DIAS EH
	HE SAID "it is a car!x" AND RAN     =>     NAR DNA "it is a car!x" DIAS EH
	-2 CELSIUS IS COLD                  =>                  DLOC SI SUISLEC -2
	SOLVE 1*5 1-5 1/5 1+5               =>               1+5 1/5 1-5 5*1 EVLOS
	THE RANGE IS 2.5..5                 =>                 5..2.5 SI EGNAR EH
	'''

	in_string = u'car is THE CAR in arabic'
	print in_string + ' => ' + do_bidi(in_string, True)
	
	in_string = u'CAR IS the car IN ENGLISH'
	print in_string + ' => ' + do_bidi(in_string, True)
	
	in_string = u'he said "IT IS 123, 456, OK"'
	print in_string + ' => ' + do_bidi(in_string, True)
	
	in_string = u'he said "IT IS (123, 456), OK"'
	print in_string + ' => ' + do_bidi(in_string, True)

	in_string = u'he said "IT IS 123,456, OK"'
	print in_string + ' => ' + do_bidi(in_string, True)
	
	in_string = u'he said "IT IS (123,456), OK"'
	print in_string + ' => ' + do_bidi(in_string, True)
	
	in_string = u'he said "IT IS 123, 456, OK"'
	print in_string + ' => ' + do_bidi(in_string, True)
	
	in_string = u'he said "IT IS (123, 456), OK"'
	print in_string + ' => ' + do_bidi(in_string, True)
	
	in_string = u'HE SAID "it is 123, 456, ok"'
	print in_string + ' => ' + do_bidi(in_string, True)
	
	in_string = u'<H123>shalom</H123>'
	print in_string + ' => ' + do_bidi(in_string, True)
	
	in_string = u'<h123>SAALAM</h123>'
	print in_string + ' => ' + do_bidi(in_string, True)
	
	in_string = u'HE SAID "it is a car!" AND RAN'
	print in_string + ' => ' + do_bidi(in_string, True)

	in_string = u'HE SAID "it is a car!x" AND RAN'
	print in_string + ' => ' + do_bidi(in_string, True)
	
	in_string = u'-2 CELSIUS IS COLD'
	print in_string + ' => ' + do_bidi(in_string, True)
	
	in_string = u'SOLVE 1*5 1-5 1/5 1+5'
	print in_string + ' => ' + do_bidi(in_string, True)
	
	in_string = u'THE RANGE IS 2.5..5'
	print in_string + ' => ' + do_bidi(in_string, True)

def main():
	''' main program '''
	if len(sys.argv) == 1:
		print 'Auto test: '
		do_tests ()
		
	if len(sys.argv) == 2:
		print do_bidi(unicode(sys.argv[1], 'utf-8'), False)
		sys.exit(0)
	
	if len(sys.argv) == 3 and sys.argv[2] == '--capsrtl':
		print do_bidi(unicode(sys.argv[1], 'utf-8'), True)
		sys.exit(0)
	
	if len(sys.argv) == 3 and sys.argv[2] == '--debug':
		debug_string(unicode(sys.argv[1], 'utf-8'), False)
		sys.exit(0)
	
	if len(sys.argv) == 4 and (sys.argv[2] == '--debug' or sys.argv[3] == '--debug') \
			and (sys.argv[2] == '--capsrtl' or sys.argv[3] == '--capsrtl'):
		debug_string(unicode(sys.argv[1], 'utf-8'), True)
		sys.exit(0)
	
	print
	print
	print 'usage: pybidi.py "string" [--caprtl] [--debug]'
	print 'caprtl - Caps Latin chars are rtl (testing)'
	print 'debug - Show algorithm steps'
	
	sys.exit(1)
		
if __name__ == "__main__":
    main()
    

