if the path output.gbdy_prep exists, 
print that you are deleting it, 
then delete it

print that you are making a directory gbdy_prep 
make directory gdby_prep

for the number of cur_sample in SAMPLES
	print  cur_sample and then what cur_sample it is
	joins the directory path created before with the path cur_sample and saves it to the 
	variable cur_dir
	create the path cur_dir
	
	variable cur_search is the joined paths input.dir and cur_sample plus wildcard 
	print out what cur_search is 
	Return a  list of path names that matchcur_search and put that in cur_file_list
	sort the list of path names 
	print out the list of path names
		for each file in the file last 
			Return the base name of pathname path at set it equal to basename
				//I do not know what this means, I looked up what basename does
			join the paths cur_dir and basename and set it equal to dst
			print dst
			creates symbolic link
				//do not undestand this either 

Start of command

if [ -d "output.gdby_prep" ] 
then 
	echo "output directory exists, deleting gbdy_prep: " 
	rm -r output.gdby_prep 
echo "making output directory gbdy_prep:" 
mkdir(output.gbdy_prep)
for cur_sample in SAMPLES
do 
	echo"cur_sample $cure_sample"
	cur_dir = //could not find how to do this part
	mkdir(cur_dir)
	
	cur_search = //same thing as cur_dir
	echo"cur_search $cur_search"
	cur_file_list = cure_search* //do not believe this is correct but believe it's something like this
	sort -o cur_file_list cur_file_list //this might work but I don't think it will
	echo"cur_file_list $cur_file_list)
	
	for cur_file in cur_file_list
		basenme = basename($cur_file)
		dst = //same thing as cur_dir
		echo "dst $dst"
		ln -s cur_file dst
done
	

	 

