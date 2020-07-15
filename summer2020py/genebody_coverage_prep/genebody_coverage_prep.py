import logging
import summer2020py
import summer2020py.setup_logger as setup_logger
import argparse
import sys
import os
import glob
import shutil

logger = logging.getLogger(setup_logger.LOGGER_NAME)


def build_parser():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--verbose", "-v", help="Whether to print a bunch of output.", action="store_true", default=False)
    mutually_exclusive_group = parser.add_mutually_exclusive_group(required=True)
    mutually_exclusive_group.add_argument("--SAMPLES", "-s", help="SAMPLES", type=str, nargs="+", default=None,)
    mutually_exclusive_group.add_argument("--SAMPLEFILE","-sf", help="file with list of samples", type=str, default=None)
    parser.add_argument("--output_dir", "-o", help = "directory of the output",type=str, required = True)
    parser.add_argument("--input_dir", "-i", help = "directory of the input",type=str, required = True)


    parser.add_argument("--config_filepath", help="path to config file containing information about how to connect to CDD API, ArxLab API etc.",
        type=str, default=summer2020py.default_config_filepath)
    parser.add_argument("--config_section", help="section of config file to use for information about how to connect to CDD API, ArxLab API etc.",
        type=str, default=summer2020py.default_config_section)
    return parser



def main(args):
    Sample_list = None
    #creating the variable Sample_list to store a list of the samples 
    if(args.SAMPLEFILE is None ): #checking to see if the command line used the file or if they just added a Sample
        logger.debug("SAMPLES")
        logger.debug(args.SAMPLES)
        Sample_list = args.SAMPLES #adding the sample given on the command line into the sample list
    else:
        logger.debug("SAMPLEFILE")
        logger.debug(args.SAMPLEFILE)
        Sample_list = load_sample(args.SAMPLEFILE) #calling the method load sample to add all of the samples in the file to the sample list
    prepare_output_dir(args.output_dir) #preparing the output directory 
    for sample in Sample_list: #each sample in the sample list runs through the for loop
        prepare_sample_dir(sample,args.out_dir,args.input_dir) #calls the method prepare-sample-dir on the sample that is currently iterating



def load_sample(Sample_File):
    return [] #taking in a .grp file returns a list of all the sample in that file



def prepare_output_dir(output_dir_path):
    if os.path.exists(output_dir_path): #if the path output_dir_path exists 
	    logger.debug("output_dir_path directory exists, output_dir_path: {}".format(output_dir_path))
	    shutil.rmtree(output_dir_path) #delete the path output_dir_path

    logger.debug("making output directory output_dir_path: {}".format(output_dir_path))
    os.mkdir(output_dir_path) #create the directory output_dir_path



def prepare_sample_dir(sample, out_dir,input_dir):
    cur_dir = make_sample_dir(sample, out_dir)
    Sample_input_files = find_sample_input_files(sample, input_dir)
    for input_file in Sample_input_files:
        create_sample_symlink(input_file,cur_dir)



def make_sample_dir(sample, out_dir):
    logger.debug(" sample: {}".format(sample))
    cur_dir = os.path.join(out_dir, sample) #create a variable to store where you want the directory to go 
    os.mkdir(cur_dir)
    return cur_dir #return where the directory is so that it can be saved to a variable to use elsewhere



def find_sample_input_files(sample, input_dir):
    cur_search = os.path.join(input_dir, "*" ) #variable cur_search is the joined paths input.dir and cur_sample plus wildcard
    logger.debug("cur_search: {}".format(cur_search))
    cur_file_list = glob.glob(cur_search) #Return a list of path names that matchcur_search and put that in cur_file_list
    cur_file_list.sort() #sort the list of path names
    logger.debug("cur_file_list: {}".format(cur_file_list))
    return cur_file_list


def create_sample_symlink(input_file, cur_dir):
    basename = os.path.basename(input_file) #Return the base name of input_file and set it equal to basename
    dst = os.path.join(cur_dir, basename)#join the paths cur_dir and basename and set it equal to dst
    logger.debug("dst: {}".format(dst))
    os.symlink(input_file, dst)#creates symbolic link to input_file dst



def create_samples_for_testing(ending, dir):
    name = "sample_{}".format(ending)
    sample = os.path.join(dir, name)
    f = open(sample,"w")#opening the file in write mode
    f.write("1") #adding the number 1 to the file
    f.close()#closing the file
    not_sample = os.path.join(dir,ending)
    f = open(not_sample,"w")#opening the file in write mode
    f.write("1") #adding the number 1 to the file
    f.close()#closing the file



def snippet(SAMPLES,output,inputs):
    # if os.path.exists(output.gbdy_prep):
	#     print("output directory exists, deleting gbdy_prep:", output.gbdy_prep)
	#     shutil.rmtree(output.gbdy_prep)

    # print("making output directory gbdy_prep:", output.gbdy_prep)
    # os.mkdir(output.gbdy_prep)

    # for cur_sample in SAMPLES:
	#     print("cur_sample:", cur_sample)
	#     cur_dir = os.path.join(output.gbdy_prep, cur_sample)
	#     os.mkdir(cur_dir)

	#     cur_search = os.path.join(input.dir, cur_sample + "*")
	#     print("cur_search:", cur_search)
	#     cur_file_list = glob.glob(cur_search)
	#     cur_file_list.sort()
	#     print("cur_file_list:", cur_file_list)

	#     for cur_file in cur_file_list:
	#         basename = os.path.basename(cur_file)
	#         dst = os.path.join(cur_dir, basename)
	#         print("dst:", dst)

	#         os.symlink(cur_file, dst)
    #this is just here incase i need to look back on it 
    pass 


	    

	    



if __name__ == "__main__":
    args = build_parser().parse_args(sys.argv[1:])

    setup_logger.setup(verbose=args.verbose)

    logger.debug("args:  {}".format(args))

    main(args)
