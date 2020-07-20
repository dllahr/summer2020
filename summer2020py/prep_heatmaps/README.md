prep_heatmap

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