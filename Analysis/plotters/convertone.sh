FILE=$1
OUTFILE=${FILE//pdf/png}
convert -density 200 -crop 1600x1070+700+80 $FILE $OUTFILE
echo "Done" $FILE
