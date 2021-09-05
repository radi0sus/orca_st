# -*- coding: utf-8 -*-
'''
# orca-st
'''

import re                               #regular expressions
import argparse                         #argument parser

# global constants
found_uv_section=False                                                                   #check for uv data in out
specstring_start = 'ABSORPTION SPECTRUM VIA TRANSITION ELECTRIC DIPOLE MOMENTS'          #check orca.out from here
specstring_end = 'ABSORPTION SPECTRUM VIA TRANSITION VELOCITY DIPOLE MOMENTS'            #stop reading orca.out from here
state_string_start = 'TD-DFT/TDA EXCITED STATES'
state_string_end = 'TD-DFT/TDA-EXCITATION SPECTRA'
threshold = 0

#global lists
statelist=list()            #mode
energylist=list()           #energy cm-1
intenslist=list()           #fosc
nmlist=list()               #wavelength 
orblist=list()              #list of orbital -> orbital transition
statedict=dict()            #dictionary of states with all transitions
selected_statedict=dict()   #dictionary of selected states with all transitions and or with those above the threshold
md_table = list()           #table for the markdown output

# parse arguments
parser = argparse.ArgumentParser(prog='orca_st', 
    description='Easily get states from from orca.out into tables\n'
                '-----------------------------------------------\n'
                'create tables are in markdown format:\n'
                '(python) orca-st.py filename > filename.md\n'
                'convert to docx with pandoc (external program):\n'
                'pandoc filename.md -o filename.docx',
                 formatter_class=argparse.RawTextHelpFormatter)

#filename is required
parser.add_argument("filename", help="the ORCA output file")

#show the matplotlib window
parser.add_argument('-s','--states',
    default='all',
    help='select one ore more or all states\n'
    'e.g. -s 1,2,3,29,30')

#do not save the png file of the spectrum
parser.add_argument('-t','--threshold',
    type = float,
    default=0,
    help='define a threshold in %% \n'
    'transitions below the threshold will not be printed\n'
    'e.g. -t 2')

#parse arguments
args = parser.parse_args()

#check if threshold is between 0 and 100%, reset if not
if args.threshold:
    if args.threshold > 100 or args.threshold < 0:
        print("Warning! Threshold out of range. Reset to 0.")
        threshold=0
    else:
        threshold = args.threshold
        
#open a file
#check existence
try:
    with open(args.filename, "r") as input_file:
        for line in input_file:
            #start exctract text 
            if state_string_start in line:
                for line in input_file:
                    #build the state - with several transitions dict: dict[state]=list(orb1 -> orb2, xx%), list(orb3 -> orb4, xx%)
                    #first the state
                    if re.search("STATE\s{1,}(\d{1,}):",line):
                        match_state=re.search("STATE\s{1,}(\d{1,}):",line)
                    #transitions here in orblist
                    elif re.search("\d{1,}[a,b]\s{1,}->\s{1,}\d{1,}[a,b]",line):
                        match_orbs=re.search("(\d{1,}[a,b]\s{1,}->\s{1,}\d{1,}[a,b])\s{1,}:\s{1,}(\d{1,}.\d{1,})",line)
                        orblist.append((match_orbs.group(1).replace("  "," "),match_orbs.group(2)))
                    #add orblist to statedict and clear orblist for next state
                    elif re.search('^\s*$',line):
                        if orblist:
                            statedict[match_state.group(1)] = orblist
                            orblist=[] 
                    #exit here
                    elif state_string_end in line:
                        break
                        
            if specstring_start in line:
            #found UV data in orca.out
                found_uv_section=True
                for line in input_file:
                    #stop exctract text 
                    if specstring_end in line:
                        break
                    #only recognize lines that start with number
                    #split line into 3 lists mode, energy, intensities
                    #line should start with a number
                    if re.search("\d\s{1,}\d",line): 
                        statelist.append(int(line.strip().split()[0])) 
                        energylist.append(float(line.strip().split()[1]))
                        nmlist.append(float(line.strip().split()[2]))
                        intenslist.append(float(line.strip().split()[3]))
                        
#file not found -> exit here
except IOError:
    print(f"'{args.filename}'" + " not found")
    sys.exit(1)

#no UV data in orca.out -> exit here
if found_uv_section == False:
    print(f"'{specstring_start}'" + "not found in" + f"'{args.filename}'")
    sys.exit(1)

#build selected_statedict from statedict with selected states
if args.states == 'all':   
    selected_statedict=statedict
elif re.search("\d",args.states):
    matchstateslist=(re.findall("\d+",args.states))
    for elements in matchstateslist:
        selected_statedict[elements]=statedict[elements]

#remove transitions below threshold from selected_statedict
for elements in selected_statedict:
    transition_list=[]
    for v in selected_statedict[elements]:
        if float(v[1])*100 >= threshold:
            transition_list.append(v)
    selected_statedict[elements]=transition_list    

#generate md table
for entry in selected_statedict:
    table_row_str = "|  {:>4} | {:>13} | {:>15} | {:>12.9f} | {:}".format(entry, energylist[int(entry)-1],nmlist[int(entry)-1],intenslist[int(entry)-1],
        " ".join("{:} ({:3.1%}),".format(v[0],float(v[1])) for v in selected_statedict[entry]))
    table_row_str = table_row_str.strip(",")
    md_table.append(table_row_str)


#print md table
header1="| State | Energy (cm⁻¹) | Wavelength (nm) | fosc         | Selected transitions"
header2="|-------|---------------|-----------------|--------------|---------------------"
max_len_line = len(max(md_table, key=len))
max_len_header = len(header1)
if max_len_line < max_len_header:
    max_len_line = max_len_header
header1=header1.ljust(max_len_line,' ')
header2=header2.ljust(max_len_line,'-')
print(header1+"|")
print(header2+"|")
for element in md_table:
    print(f'{element:{max_len_line}}|')
