#!/bin/bash

# arguments are one of
# ./convertone               PDFFILE
# ./convertone --normal      PDFFILE
# ./convertone --ratioFull   PDFFILE
# ./convertone --ratioSquash PDFFILE
if [[ $1 =~ \.pdf ]]
then
    MODE='--normal'
    FILE=$1
else
    MODE=$1
    FILE=$2
fi
OUTFILE=${FILE//pdf/png}

# "normal"      is for 800 x 600                 made by Plotter class
# "ratioFull"   is for 800 x 800 with ratio plot made by Plotter class
# "ratioSquash" is for 800 x 600 with ratio plot made by Plotter class
if   [ $MODE == '--normal'      ]
then
    convert -density 200 -crop 1600x1070+700+80 $FILE $OUTFILE
elif [ $MODE == '--ratioFull'   ]
then
    convert -density 200 -crop 1600x1500+700+80 $FILE $OUTFILE
elif [ $MODE == '--ratioSquash' ]
then
    convert -density 200 -crop 1600x1120+700+70 $FILE $OUTFILE
fi

echo "Done" $FILE
