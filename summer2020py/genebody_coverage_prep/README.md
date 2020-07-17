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



	 

