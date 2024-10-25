# orca_st
A Python 3 script for (hassle-free) extraction of state informations from [ORCA](https://orcaforum.kofo.mpg.de) 
output files. Selection of states and threshold based printing is possible.

## External modules
 `re` 
 
## Quick start
 Start the script with:
```console
python3 orca-st.py filename
```
it will show the table in the console. The table will probably exceed the size of
your console window and the table might therefore look unfamiliar.

Start the script with:
```console
python3 orca-st.py filename > filename.md
```
it will save the table in markdown format.

Convert markdown to docx (install [PANDOC](https://pandoc.org) first):
```console
pandoc filename.md -o filename.docx
```
This will convert the markdown file to a docx file. Open it with your favorite
word processor. Convert the file to even more formats such as HTML, PDF or TeX with PANDOC.

## Command-line options
- `filename` , required: filename
- `-s` `S1, S2, ... Sx` , optional: process all or selected states (default is `S = all`)
- `-t` `N`, optional: set a threshold in %. Transitions below the threshold value will not be printed (default is `N = 0`)
- `-nto`, optional: process all or selected states for natural transition orbitals (NTO)
- `-tr`, optional: show 'Transition' in case of ORCA 6 output files

## Code options
You can change the table header in the script (take care of the row size if necessary). 

## Remarks
- The data are taken from the section "ABSORPTION SPECTRUM VIA TRANSITION ELECTRIC DIPOLE MOMENTS".
- Only tested with "normal" outputs (including NTO) from TD-DFT calculations.
- Selected transitions that are below the threshold will not be printed in the table. This may result in empty cells.
- If NTO transitions are present int the output file and NTO transitions should be printed, use the `-nto` keyword. 
Otherwise, do not use the `-nto` keyword.
- The script used two unicode characters, namely "⁻¹". Please have a look at the script if you experience any issues. The easiest
solution is to replace "⁻¹" with the ascii characters "-1".

## Examples
![show](/examples/show-use2.gif)

| State | Energy (cm⁻¹) | Wavelength (nm) | fosc         | Selected transitions                  |
|-------|---------------|-----------------|--------------|---------------------------------------|
|     1 |       23979.9 |           417.0 |  0.010256887 | 54a -> 55a (92.2%)                    |
|     2 |       31770.2 |           314.8 |  0.074054821 | 53a -> 55a (94.9%)                    |
|     3 |       34195.7 |           292.4 |  0.009570330 | 52a -> 55a (92.5%)                    |
|     4 |       34682.0 |           288.3 |  0.004586429 | 51a -> 55a (91.9%)                    |
|     5 |       36920.0 |           270.9 |  0.015882129 | 50a -> 55a (89.0%)                    |
|    12 |       46564.6 |           214.8 |  0.022945033 | 52a -> 56a (43.6%), 53a -> 58a (17.8%)|
|    20 |       50438.7 |           198.3 |  0.011430245 | 50a -> 58a (45.2%), 52a -> 59a (24.0%)|
|    25 |       53856.3 |           185.7 |  0.048902902 | 46a -> 55a (20.3%), 47a -> 55a (64.4%)|


| State | Energy (cm⁻¹) | Wavelength (nm) | fosc         | Selected transitions (NTO)                                |
|-------|---------------|-----------------|--------------|-----------------------------------------------------------|
|    20 |       50693.7 |           197.3 |  0.349127321 | 54a -> 55a (38.6%), 53a -> 56a (31.2%), 52a -> 57a (27.7%)|
|    25 |       53666.2 |           186.3 |  0.001229720 | 54a -> 55a (62.0%), 53a -> 56a (29.7%)                    |
|    30 |       55961.6 |           178.7 |  0.000789896 | 54a -> 55a (93.9%)                                        |
