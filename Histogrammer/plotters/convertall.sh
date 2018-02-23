for FILE in pdfs/*.pdf
do
	./convertone $FILE
done

# Don't do this anymore, use parallel:
# ls pdfs/* | parallel ./convertone {}
# parallel automatically manages threading and bg processes for you!
