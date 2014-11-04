Cipher-Problem
==============

To run the file,

python cipher-forward-backward.py -data [path to english.data] -cipher [path to cipher.data] -iter [no. of iterations] -rstart [no. of restarts] -plot [show graph]

Examples:

python cipher-forward-backward.py -data english.data -cipher cipher.data -iter 5 -rstart 0 -plot 1
will perform 5 iterations, no random restart - uniform start and graph will be shown

python cipher-forward-backward.py -data ../english.data -cipher ../cipher.data -iter 10 -rstart 5 -plot 0
will perform 10 iterations, 5 random restart and graph will not be shown
