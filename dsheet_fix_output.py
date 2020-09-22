"""
    File name: dsheet_fix_output.py
    Author: Rob Swart (Mobilis TBI)
    Date last modified: 14/09/2020

    Script to enable opening of console generated D-Sheet files in GUI program by replacing version number
    in "CREATED BY..." line

"""

with open("dsheet_test.shd", 'r') as f:
    get_all = f.readlines()

with open("dsheet_test.shd", 'w') as f:
    for i, line in enumerate(get_all, 1):  # STARTS THE NUMBERING FROM 1 (by default it begins with 0)
        if i == 8:  # OVERWRITES line:2
            f.writelines("CREATED BY : D-Sheet Piling version 19.3.1.27104 \n")
        else:
            f.writelines(line)
