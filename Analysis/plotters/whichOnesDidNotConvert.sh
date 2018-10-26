ls pdfs/*.pdf > tmp1
ls pngs/*.png > tmp2
sed -i 's/png/pdf/g' tmp2
sort tmp1 > tmp; mv tmp tmp1
sort tmp2 > tmp; mv tmp tmp2
diff tmp1 tmp2 | sed -n '/pdfs/s/< //p' > missing
rm tmp1 tmp2
