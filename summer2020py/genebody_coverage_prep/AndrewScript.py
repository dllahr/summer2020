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
    parser.add_argument("--hostname", help="lims db host name", type=str, default="getafix-v")

    parser.add_argument("--config_filepath", help="path to config file containing information about how to connect to CDD API, ArxLab API etc.",
        type=str, default=summer2020py.default_config_filepath)
    parser.add_argument("--config_section", help="section of config file to use for information about how to connect to CDD API, ArxLab API etc.",
        type=str, default=summer2020py.default_config_section)

    parser.add_argument("--queue_choice", "-qc", help="which of the queues to work on - valid values are roast, brew, both", type=str,
        choices=["roast", "brew", "both"], default="both")
    parser.add_argument("--add_to_queue", "-a", help="add the det_plate entries to the roast_queue", type=str, nargs="+", default=None)
    # To make --option1 and --option2 mutually exclusive, one can define mutually_exclusive_group in argparse,
    # argparse asserts that the options added to the group are not used at the same time and throws exception if otherwise
    mutually_exclusive_group = parser.add_mutually_exclusive_group()
    mutually_exclusive_group.add_argument("--option1", action="store", dest="option1", help="provide argument for option1", default=None)
    mutually_exclusive_group.add_argument("--option2", action="store", dest="option2", help="provide argument for option2", default=None)
    return parser

def main(args):
    choice = input("c for Command line or g for.grp file")
    output = input("diretory of output")
    inputs = input("directory of input")
    if(choice =="c"):
        print("command line")
        filename = sys.argv[-1]
        print(filename)
        #do some thing using the filename so that you can call snippet using the Sample you want as the argument
        #and it all works as it should 
    elif(choice =="g"):
        print(".grp file")
        filename = sys.argv[-1]
        print(filename)
        #do some thing using the filename so that you can call snippet using the Sample you want as the argument
        #and it all works as it should 
    else:
        print("bad input")

def snippet(SAMPLES,output,inputs):
    if os.path.exists(output.gbdy_prep):
	    print("output directory exists, deleting gbdy_prep:", output.gbdy_prep)
	    shutil.rmtree(output.gbdy_prep)

    print("making output directory gbdy_prep:", output.gbdy_prep)
    os.mkdir(output.gbdy_prep)

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
