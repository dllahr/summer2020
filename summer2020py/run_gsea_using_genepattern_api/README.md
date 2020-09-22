
links 

using genepattern in python
https://www.genepattern.org/programmers-guide#_Using_GenePattern_from_Python

unit test mocking
https://docs.python.org/3/library/unittest.mock.html

genepattern mocking
https://groups.google.com/forum/?utm_medium=email&utm_source=footer#!topic/genepattern-help/eZWRJrJxQ6Y

zipfile 
https://docs.python.org/3.8/library/zipfile.html





importing various things 
os and shutil to do stuff with directories
pandas to do data frame
zipfile to i presume zip files

gp - don't know 
%matplotlib notebook don't know what this line does either

variables that I used in prep_heatmaps

num_permutations - presume this will be used later

job_memory - also presume this will be used later, maybe limiting the amount of memory 
the code can use?

**prepare directories for output** 
simple enough, used this code before

**build rnk files from DGE data files**
The RNK file contains a single, rank ordered gene list (not gene set) in a simple newline-delimited text format. 
It is used when you have a pre-ordered ranked list that you want to analyze with GSEA
presume I will need to read up on these a bit more like I did with gctoo, 
looking at the code here, it is very similar to the GCToo from dge data files, so I understand it

**run GSEA using rnk files**

reference_genesets is a thing, I understand how they are put into the list, just not what they are useful for

gp username password and url are all things that are then used to create a server, I don't want to run this code without 
talking about it to dave

upload the basename and then the file to the server, the file is put into a url link, presume that's what the gpserver.upload does
simple method, don't know why it is there but I can understand it

task_list = gpserver.get_task_list(), this would be a simple line, If i knew what the tasks were

printing out the tasks in the task list that have gsea in them 

something with the gseapreranked task 

????? The code looks simple but contains things I don't understand, will look into those

all job spec list is a list that is then filled 

job list is another list 

zip file is a list of the files that are zipped 
