FILE=$1
OUTFILE=${FILE//pdf/png}
convert -density 200 -crop 1500x1070+730+80 $FILE $OUTFILE
echo "Done" $FILE
