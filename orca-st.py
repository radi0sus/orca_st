# -*- coding: utf-8 -*-
'''
# orca-st
'''

import sys                              #system
import re                               #regular expressions
import argparse                         #argument parser

#remove comment in case you get an encoding error when saving the output to a file with ">" under windows
#alternatively replace 'cm⁻¹' with 'cm-1' in the table header (close to the end of script)
#alternatively you can configure the windows console with "set PYTHONIOENCODING=utf-8" before starting the script
#replace 'cm⁻¹' with 'cm-1' for pdf file conversion with pandoc in case of unicode issues
sys.stdout.reconfigure(encoding='utf-8')                                                     

# global constants
found_uv_section = False                                                                 #check for uv data in out
specstring_start = 'ABSORPTION SPECTRUM VIA TRANSITION ELECTRIC DIPOLE MOMENTS'          #check orca.out from here
specstring_end = 'ABSORPTION SPECTRUM VIA TRANSITION VELOCITY DIPOLE MOMENTS'            #stop reading orca.out from here
state_string_start = 'TD-DFT/TDA EXCITED STATES'                                         #check for states from here
state_string_end = 'TD-DFT/TDA-EXCITATION SPECTRA'                                       #stop reading states from here
nto_string_start ='NATURAL TRANSITION ORBITALS'                                          #NTOs start here
threshold = 0                                                                            #default threshold
found_nto = False                                                                        #found NTOs in orca.out
#for ORCA 6
state = 0                                                                                #ORCA 6 does not list the state in the table
orca6 = False                                                                            #for including transitions in case of ORCA 6 on request

#global lists
statelist = list()            #mode
energylist = list()           #energy cm-1
intenslist = list()           #fosc
nmlist = list()               #wavelength 
orblist = list()              #list of orbital -> orbital transition
statedict = dict()            #dictionary of states with all transitions
selected_statedict = dict()   #dictionary of selected states with all transitions and or with those above the threshold
md_table = list()             #table for the markdown output
#for ORCA 6
#in ORCA 6 there is no state given in the list
translist = list()
#for NTO
nto_orblist=list()            #list of orbital -> orbital transition for NTOs
nto_statedict=dict()          #dictionary of states with all transitions for NTOs


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

#select states
parser.add_argument('-s','--states',
    default='all',
    help='select one ore more or all states\n'
    'e.g. -s 1,2,3,29,30')

#threshold
parser.add_argument('-t','--threshold',
    type = float,
    default=0,
    help='define a threshold in %% \n'
    'transitions below the threshold will not be printed\n'
    'e.g. -t 2')

#NTO
parser.add_argument('-nto','--nto',
    default=0, action='store_true',
    help='select NTO transitions')

#include Transition
parser.add_argument('-tr','--trans',
    default=0, action='store_true',
    help='include Transition in case of ORCA 6')

#parse arguments
args = parser.parse_args()

#change values according to arguments
nto = args.nto

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
                    if re.search(r"STATE\s{1,}(\d{1,}):",line):
                        match_state=re.search(r"STATE\s{1,}(\d{1,}):",line)
                    #transitions here in orblist
                    elif re.search(r"\d{1,}[a,b]\s{1,}->\s{1,}\d{1,}[a,b]",line):
                        match_orbs=re.search(r"(\d{1,}[a,b]\s{1,}->\s{1,}\d{1,}[a,b])\s{1,}:\s{1,}(\d{1,}.\d{1,})",line)
                        orblist.append((match_orbs.group(1).replace("  "," "),match_orbs.group(2)))
                    #add orblist to statedict and clear orblist for next state
                    elif re.search(r"^\s*$",line):
                        if orblist:
                            statedict[match_state.group(1)] = orblist
                            orblist=[] 
                                                        
                    #exit here
                    elif nto_string_start in line:
                        break
                    elif state_string_end in line:
                        break
            
            #same for NTOs
            if re.search(r"FOR STATE\s{1,}(\d{1,})",line):
                #found NTO in orca.out
                found_nto = True
                match_state_nto=re.search(r"FOR STATE\s{1,}(\d{1,})",line)
            elif re.search(r"\d{1,}[a,b]\s{1,}->\s{1,}\d{1,}[a,b]",line):
                match_orbs_nto=re.search(r"(\d{1,}[a,b]\s{1,}->\s{1,}\d{1,}[a,b])\s{1,}: n=\s{1,}(\d{1,}.\d{1,})",line)
                nto_orblist.append((match_orbs_nto.group(1).replace("  "," "),match_orbs_nto.group(2)))
            #add orblist to statedict and clear orblist for next state
            elif re.search(r"^\s*$",line):
                if nto_orblist:
                    nto_statedict[match_state_nto.group(1)] = nto_orblist
                    nto_orblist=[] 
            
            if specstring_start in line:
            #found UV data in orca.out
                found_uv_section=True
                for line in input_file:
                    #stop exctract text 
                    if specstring_end in line:
                        break
                    #only recognize lines that start with number
                    #split line into 4 lists state, energy, nm, intensities
                    #line should start with a number
                    if re.search(r"^\s{1,}\d+\s{1,}\d",line): 
                        statelist.append(int(line.strip().split()[0])) 
                        energylist.append(float(line.strip().split()[1]))
                        nmlist.append(float(line.strip().split()[2]))
                        intenslist.append(float(line.strip().split()[3]))
                    if re.search(r"\d+-\d+[A-Z]\s{1,}->\s{1,}\d",line): 
                        # ORCA 6
                        # search for '0-1A -> 1-3A' etc
                        # because state numbers are no longer listed
                        orca6 = True
                        state = state + 1
                        statelist.append(state) 
                        # include '0-1A -> 1-3A' etc in a list
                        transition = re.findall(r"\d+-\d+[A-Z]\s{1,}->\s{1,}\d+-\d+[A-Z]", line)
                        translist.append(transition)
                        energylist.append(float(line.strip().split()[4]))
                        nmlist.append(float(line.strip().split()[5]))
                        intenslist.append(float(line.strip().split()[6]))
#file not found -> exit here
except IOError:
    print(f"'{args.filename}'" + " not found")
    sys.exit(1)

#no UV data in orca.out -> exit here
if found_uv_section == False:
    print(f"'{specstring_start}'" + " not found in " + f"'{args.filename}'")
    sys.exit(1)
    
#no NTO data in orca.out -> exit here
if nto == True and found_nto == False:
    print(f"'{nto_string_start}'" + " not found in " + f"'{args.filename}'")
    sys.exit(1)

#build selected_statedict from statedict with selected states
try:
    if args.states == 'all':
        if nto:
            selected_statedict = nto_statedict
        else:
            selected_statedict = statedict
    elif re.search(r"\d",args.states):
        matchstateslist=(re.findall(r"\d+",args.states))
        for elements in matchstateslist:
            if nto:
                selected_statedict[elements]=nto_statedict[elements]
            else:
                selected_statedict[elements]=statedict[elements]
except KeyError:
    print("Warning! State(s) not present. Exit.")
    sys.exit(1)
            
#remove transitions below threshold from selected_statedict
for elements in selected_statedict:
    transition_list=[]
    for v in selected_statedict[elements]:
        if float(v[1])*100 >= threshold:
            transition_list.append(v)
    selected_statedict[elements]=transition_list    

#generate md table md table with Transition from ORCA 6
if args.trans and orca6:
    for entry in selected_statedict:
        table_row_str = "|  {:>4} | {:>15} | {:>13} | {:>15} | {:>12.9f} | {:}".format(entry, 
                        *translist[int(entry)-1], 
                         energylist[int(entry)-1],
                         nmlist[int(entry)-1],
                         intenslist[int(entry)-1],
                         " ".join("{:} ({:3.1%}),".format(v[0],float(v[1])) for v in selected_statedict[entry]))
        table_row_str = table_row_str.strip(",")
        md_table.append(table_row_str)
else:
    #generate md table from other ORCA .out
    for entry in selected_statedict:
        table_row_str = "|  {:>4} | {:>13} | {:>15} | {:>12.9f} | {:}".format(entry, 
                        energylist[int(entry)-1],
                        nmlist[int(entry)-1],
                        intenslist[int(entry)-1],
                        " ".join("{:} ({:3.1%}),".format(v[0],float(v[1])) for v in selected_statedict[entry]))
        table_row_str = table_row_str.strip(",")
        md_table.append(table_row_str)

if args.trans and orca6:
    #print md table with Transition from ORCA 6
    header1="| State | Transition      | Energy (cm⁻¹) | Wavelength (nm) | fosc         | Selected transitions"
    header2="|-------|-----------------|---------------|--------------   |--------------|---------------------"
    if nto:
        header1=(header1+" (NTO)")
        header2=(header2+"------")
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
else:
    #print md table from other ORCA .out
    header1="| State | Energy (cm⁻¹) | Wavelength (nm) | fosc         | Selected transitions"
    header2="|-------|---------------|-----------------|--------------|---------------------"
    if nto:
        header1=(header1+" (NTO)")
        header2=(header2+"------")
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
