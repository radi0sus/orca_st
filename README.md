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

Convert markdown to docx:
(Install [PANDOC](https://pandoc.org) first.)
```console
pandoc filename.md > filename.docx
```
This will convert the markdown file to a docx file. Open it with your favorite
word processor.

## Command-line options
- `filename` , required: filename
- `-s` `S1, S2, ... Sx` , optional: process all or selected states (default is `S = all`)
- `-t` `N`, optional: set a threshold in %. Transitions below the threshold value will not be printed (default is `N = 0`)
- `-nto`, optional: process all or selected states for natural transition orbitals (default is `S = all`)

## Code options
You can change the table header in the script (take care of the row size if necessary). 

## Remarks
- The data are taken from the section "ABSORPTION SPECTRUM VIA TRANSITION ELECTRIC DIPOLE MOMENTS".
- Only tested with "normal" outputs (including NTO) from TD-DFT calculations.
- Selected transitions that are below the threshold will not be printed in the table. This may result in empty cells.
- If NTO transitions are present int the output file and NTO transitions should be printed, use the `-nto` keyword. 
Otherwise, do not use the `-nto` keyword.

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
|     1 |       19649.8 |           508.9 |  0.047997730 | 54a -> 55a (99.7%)                                        |
|     2 |       30350.7 |           329.5 |  0.012389355 | 54a -> 55a (95.8%)                                        |
|     3 |       31343.0 |           319.1 |  0.023203271 | 54a -> 55a (97.5%)                                        |
|     4 |       32895.8 |           304.0 |  0.002292035 | 54a -> 55a (96.1%)                                        |
|     5 |       34091.2 |           293.3 |  0.176347015 | 54a -> 55a (99.3%)                                        |
|    12 |       47572.2 |           210.2 |  0.012926362 | 54a -> 55a (76.0%), 53a -> 56a (16.3%)                    |
|    20 |       50693.7 |           197.3 |  0.349127321 | 54a -> 55a (38.6%), 53a -> 56a (31.2%), 52a -> 57a (27.7%)|
|    25 |       53666.2 |           186.3 |  0.001229720 | 54a -> 55a (62.0%), 53a -> 56a (29.7%)                    |
