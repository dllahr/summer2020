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
    pass #taking in a .grp file returns a list of all the sample in that file

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
    logger.debug(" cur_sample: {}".format(cur_sample))
    cur_dir = os.path.join(sample, out_dir) #create a variable to store where you want the directory to go 
    os.mkdir(cur_dir)
    return cur_dir #return where the directory is so that it can be saved to a variable to use elsewhere


def find_sample_input_files(sample, input_dir):
    pass



def create_sample_symlink(input_file, cur_dir):
    pass

def snippet(SAMPLES,output,inputs):
    

    for cur_sample in SAMPLES:
	    print("cur_sample:", cur_sample)


	    cur_search = os.path.join(inputs.dir, cur_sample + "*")
	    print("cur_search:", cur_search)
	    cur_file_list = glob.glob(cur_search)
	    cur_file_list.sort()
	    print("cur_file_list:", cur_file_list)

	    for cur_file in cur_file_list:
	        basename = os.path.basename(cur_file)
	        dst = os.path.join(cur_dir, basename)
	        print("dst:", dst)

	        os.symlink(cur_file, dst)




if __name__ == "__main__":
    args = build_parser().parse_args(sys.argv[1:])

    setup_logger.setup(verbose=args.verbose)

    logger.debug("args:  {}".format(args))

    main(args)
