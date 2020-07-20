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

    parser.add_argument("--output_symlinks_dir_name", "-osd", help = """name of the output directory containing symlinks to 
        original input""", type=str, default="input_gbdy_cov")
    parser.add_argument("--output_calc_dir_name", "-ocdn", help = """name of the output directory that will contain 
        subdirectories that will hold the results of the actual genebody_coverage calculation""",
        type=str, default="output_gbdy_cov")

    parser.add_argument("--config_filepath", help="path to config file containing information about how to connect to CDD API, ArxLab API etc.",
        type=str, default=summer2020py.default_config_filepath)
    parser.add_argument("--config_section", help="section of config file to use for information about how to connect to CDD API, ArxLab API etc.",
        type=str, default=summer2020py.default_config_section)
    return parser


def main(args):
    main_params(args.SAMPLES, args.SAMPLEFILE, args.output_dir, args.input_dir, args.output_symlinks_dir_name, 
        args.output_calc_dir_name)


def main_params(samples, sample_file, output_dir, input_dir, output_symlinks_dir_name, output_calc_dir_name):
    Sample_list = None
    #creating the variable Sample_list to store a list of the samples 
    if(sample_file is None ): #checking to see if the command line used the file or if they just added a Sample
        logger.debug("using samples")
        logger.debug("samples:  {}".format(samples))
        #adding the sample given on the command line into the sample list
        Sample_list = samples
    else:
        logger.debug("using sample_file")
        logger.debug("sample_file:  {}".format(sample_file))
        #calling the method load sample to add all of the samples in the file to the sample list
        Sample_list = load_sample(sample_file)

    output_symlinks_dir, output_calc_dir = prepare_output_dir(output_dir, output_symlinks_dir_name, output_calc_dir_name)

    for sample in Sample_list:
        prepare_sample_symlinks_dir(sample, input_dir, output_symlinks_dir)

        prepare_sample_output_calc_dir(sample, output_calc_dir)


def load_sample(Sample_File):
    with open(Sample_File) as f:
        samplelist = [line.rstrip() for line in f]
    logger.debug("samplelist:{}".format(samplelist))
    return samplelist


def prepare_output_dir(output_dir_path, output_symlinks_dir_name, output_calc_dir_name):
    if os.path.exists(output_dir_path): #if the path output_dir_path exists 
	    logger.debug("output_dir_path directory exists, output_dir_path: {}".format(output_dir_path))
	    shutil.rmtree(output_dir_path) #delete the path output_dir_path

    logger.debug("making output directory output_dir_path: {}".format(output_dir_path))
    os.mkdir(output_dir_path) #create the directory output_dir_path

    output_symlinks_dir = os.path.join(output_dir_path, output_symlinks_dir_name)
    os.mkdir(output_symlinks_dir)

    output_calc_dir = os.path.join(output_dir_path, output_calc_dir_name)
    os.mkdir(output_calc_dir)

    return output_symlinks_dir, output_calc_dir


def prepare_sample_symlinks_dir(sample, input_dir, out_dir):
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
    cur_search = os.path.join(input_dir,sample + "*" ) #variable cur_search is the joined paths input.dir and cur_sample plus wildcard
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


def prepare_sample_output_calc_dir(sample, output_calc_dir):
    output_sample_calc_dir = os.path.join(output_calc_dir, sample)
    os.mkdir(output_sample_calc_dir)
    return output_sample_calc_dir


if __name__ == "__main__":
    args = build_parser().parse_args(sys.argv[1:])

    setup_logger.setup(verbose=args.verbose)

    logger.debug("args:  {}".format(args))

    main(args)
