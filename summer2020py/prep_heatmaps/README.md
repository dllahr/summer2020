prep_heatmap
things in bold are likely what will become methods, a list of them will be written up here once done

importing os, shutil, glob, panda, cmapPy.pandasGEXpress.GCToo and cmapPy.pandasGEXpress.write_gct

os provides a portable way of using operating system dependent functionality

shutil provides a number of high-level operations on files and collections of files. 
	In particular, functions are provided which support file copying and removal

glob finds all the pathnames matching a specified pattern according to the rules used by the Unix shell, 
	although results are returned in arbitrary order.

panda is a software library written for the Python programming language for data manipulation and analysis.

pandasGEXpress package allowing users to easily read, modify, and write .gct and .gctx files
	A GCT file (. gct) is a tab-delimited text file that contains gene expression data
	The GCTx data format is a binary file used to store annotated data matrices


source_dir is where everything will be done, where the files will be created a such
experiment id is what the experiment, presuming they are unique so expirments can be easily found by searching the id
dge_stats_for_heatmaps = ["logFC", "t"] at this point in time I don't undestand what this does, might understand if after 
					I go through the whole code

output_template will be used as a template for the heatmaps

base_data_path is where the data is

url_template is a template for the urls that will be created

output_html_link_file it a html file that will store html stuff (don't know at the moment of writing this)

*prepare output directory* 
if the path that you want to put the outputs at alread exists, delete it then make it
if the path that you want to put the outputs doesn't exists, make it

*find DGE data file as pandas dataframe*
save to dge_file_list all the files in the source_dir direcotry dge_data that start with the expirment id
and then _*_DGE_r*.txt where * is the wildcard symbol meaning anything can go there

*read DGE data file as pandas dataframe*
take all the files read them, and then display then in a table
	have to understand this

*prepare heatmap GCToo object with data and metadata*
do thing to prepare data, will look more deeply into how this is done soon

*write heatmap GCToo objects to files in heatmap_dir*
	do thing, really need to understand tables in python more

*prepare links to interactive heatmaps in html file*
	what is sounds like this is where the url_template is used, all the url are added to a list

	then output_html_link_file has the list 


