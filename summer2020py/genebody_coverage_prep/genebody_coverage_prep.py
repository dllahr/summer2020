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
    logger.debug("This is args{}".format(args))
    Sample_list = None
    #choice = input("c for Command line or g for.grp file")
    #output = input("diretory of output") #output should not be a string but I don't know what it should be
    #inputs = input("directory of input")#no idea what the input.dir line is for this is here so that I can pass it as an a
                                        #argument and not get an error of course the code doesn't work now 
                                        #but there are other problems besides this
    if(args.SAMPLEFILE is None ):
        logger.debug("SAMPLES")
        logger.debug(args.SAMPLES)
        Sample_list = args.SAMPLES
        #do some thing using the filename so that you can call snippet using the Sample you want as the argument
        #and it all works as it should 
    else:
        logger.debug("SAMPLEFILE")
        logger.debug(args.SAMPLEFILE)
        Sample_list = load_sample(args.SAMPLEFILE)
    prepare_output_dir(args.output_dir)
    for sample in Sample_list:
        prepare_sample_dir(sample,args.out_dir,args.input_dir)

def load_sample(Sample_File):
    pass

def prepare_output_dir(output_dir_path):
    if os.path.exists(output_dir_path):
	    print("output_dir_path directory exists, output_dir_path:", output_dir_path)
	    shutil.rmtree(output_dir_path)

    print("making output directory output_dir_path:", output_dir_path)
    os.mkdir(output_dir_path)

def prepare_sample_dir(sample, out_dir,input_dir):
    cur_dir = make_sample_dir(sample, out_dir)
    Sample_input_files = find_sample_input_files(sample, input_dir)
    for input_file in Sample_input_files:
        create_sample_symlink(input_file,cur_dir)
def make_sample_dir(sample, out_dir):
    pass
def find_sample_input_files(sample, input_dir):
    pass
def create_sample_symlink(input_file, cur_dir):
    pass

def snippet(SAMPLES,output,inputs):
    

    for cur_sample in SAMPLES:
	    print("cur_sample:", cur_sample)
	    cur_dir = os.path.join(output.gbdy_prep, cur_sample)
	    os.mkdir(cur_dir)

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
