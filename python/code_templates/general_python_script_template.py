import logging
import FHTLIMS
import FHTLIMS.setup_logger as setup_logger
import argparse
import sys


logger = logging.getLogger(setup_logger.LOGGER_NAME)


def build_parser():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--verbose", "-v", help="Whether to print a bunch of output.", action="store_true", default=False)
    parser.add_argument("--hostname", help="lims db host name", type=str, default="getafix-v")

    parser.add_argument("--config_filepath", help="path to config file containing information about how to connect to CDD API, ArxLab API etc.",
        type=str, default=FHTLIMS.default_config_filepath)
    parser.add_argument("--config_section", help="section of config file to use for information about how to connect to CDD API, ArxLab API etc.",
        type=str, default=FHTLIMS.default_config_section)

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
    logger.info("hello world!")


if __name__ == "__main__":
    args = build_parser().parse_args(sys.argv[1:])

    setup_logger.setup(verbose=args.verbose)

    logger.debug("args:  {}".format(args))

    main(args)