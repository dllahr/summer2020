import logging
import summer2020py
import summer2020py.setup_logger as setup_logger
import argparse
import sys

import glob
import os.path

import pandas
import numpy

import plotly.express as pltexpr


logger = logging.getLogger(setup_logger.LOGGER_NAME)

genebody_position_percentages = [20, 50, 80]

base_output_template_dict = {
    "all_pct":"{prefix}_all_genebody_coverage_r{{}}x{{}}.txt",
    "compare_80_20":"{prefix}_asymmetry_compare_80_20_r{{}}x{{}}.txt",
    "line_html":"{prefix}_genebody_{{}}.html",
    "histogram_html":"{prefix}_genebody_histogram_{{}}.html"
    # fill in others here. NB remove output and template from name since we know that given the dict name
}


def build_output_template_dict(prefix):
    output_template_dict = {
        name:template.format(prefix = prefix) for name, template in base_output_template_dict.items()
    }
    return output_template_dict


def build_parser():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--verbose", "-v", help="Whether to print a bunch of output.", action="store_true", default=False)

    parser.add_argument("--input_dir", "-i", help = "directory where inputs are, will search in the subdirectories of input_dir for the genebody coverage txt files", type = str, required = True)

    parser.add_argument("--output_dir", "-o", help = "directory where outputs are, often experiment ID ", type = str,  required = True)

    parser.add_argument("--output_file_prefix", "-of", help = "file prefix for outputted files, could be expirment ID", type = str, required = True)
   
    parser.add_argument("--config_filepath", help="path to config file containing information about how to connect to CDD API, ArxLab API etc.",
        type=str, default=summer2020py.default_config_filepath)
    parser.add_argument("--config_section", help="section of config file to use for information about how to connect to CDD API, ArxLab API etc.",
        type=str, default=summer2020py.default_config_section)

    return parser


def input_file_search(input_dir):
    input_search = os.path.join(input_dir, "*", "*.geneBodyCoverage.txt")
    logger.debug("input_search: {}".format(input_search))
    input_files = glob.glob(input_search)
    input_files.sort()
    logger.debug("len(input_files): {}".format(len(input_files)))
    logger.debug("\n input_files[:3]: {}".format(input_files[:3]))
    return input_files

def load_genebody_coverage_data(input_files):
    inp_df_list = []

    for inp_f in input_files[:]:
        logger.debug("inp_f: {}".format(inp_f))
        inp_df = pandas.read_csv(inp_f, sep="\t", index_col=0).T

        #sample_id = inp_df.columns[0].split(".")[0]

        #normpath converts any file seperator to \ so this works on both Mac and Windows

        sample_id = os.path.normpath(inp_f).split("\\")[-2]
        logger.debug("sample_id:{}".format(sample_id))


        #metimes the genebody coverage data for more than 1 sample ends up in a text file. 
        #Rather than rerun/fix that in the moment
        #if statement finds the one you want
        if inp_df.shape[1] > 1:
            select_col = [x for x in inp_df.columns if x.startswith(sample_id + ".")]
            inp_df = inp_df[select_col]
            
        inp_df.columns = ["coverage_counts"]
        inp_df["sample_id"] = sample_id
        
        inp_df.index.name = "genebody_pct"

        logger.debug("inp_df.shape: {}".format(inp_df.shape))
        #display(inp_df)

        inp_df_list.append(inp_df)

        
    logger.debug("len(inp_df_list): {}".format(len(inp_df_list)))
    logger.debug("inp_df_list[0].head(): {}".format(inp_df_list[0].head()))
    return inp_df_list    

def merge_dfs_into_one(inp_df_list):
    counts_df = pandas.concat(inp_df_list, axis=0)
    counts_df.reset_index(inplace=True)
    counts_df["genebody_pct"] = counts_df.genebody_pct.astype(int)
    logger.debug("counts_df.shape: {}".format(counts_df.shape))
    return counts_df

def sum_counts(counts_df):
    sum_counts_df = counts_df[["coverage_counts", "sample_id"]].groupby("sample_id").sum()
    sum_counts_df.columns = ["total_coverage_counts"]
    logger.debug("sum_counts_df.shape: {}".format(sum_counts_df.shape))
    return sum_counts_df

def calculate_percentile_df(counts_df, sum_counts_df):
    percentile_df = counts_df.join(sum_counts_df, on="sample_id", how="left")
    percentile_df["coverage_percentile"] = percentile_df.coverage_counts / percentile_df.total_coverage_counts
    logger.debug("percentile_df.shape: {}".format(percentile_df.shape))
    return percentile_df

def create_pct_df_list(percentile_df):

    pct_df_list = []
    for pct in genebody_position_percentages:
        pct_df_list.append(percentile_df.loc[
            (percentile_df.genebody_pct == pct), ["sample_id", "coverage_percentile"]
        ].set_index("sample_id"))

    logger.debug("len(pct_df_list): {}".format(len(pct_df_list)))
    for i, pct_df in enumerate(pct_df_list):
        pct = genebody_position_percentages[i]
        logger.debug("pct_df.shape: {}".format(pct_df.shape))
        pct_df.columns = ["coverage_{}pct".format(pct)]
        
    
    return pct_df_list

def create_pct_comp_df(pct_df_list):
    pct_comp_df = pandas.concat(pct_df_list, axis=1)
    pct_comp_df["coverage_diff"] = pct_comp_df.loc[:, "coverage_80pct"] - pct_comp_df.loc[:, "coverage_20pct"]
    pct_comp_df["cov_diff_pct"] = pct_comp_df.coverage_diff / pct_comp_df.loc[:, "coverage_50pct"]
    logger.debug("pct_comp_df.shape: {}".format(pct_comp_df.shape))
    return pct_comp_df

def add_label_col(pct_comp_df):
    pct_comp_df["label"] = pct_comp_df.index + "  " + ["%.2f" % x for x in pct_comp_df.cov_diff_pct]
    logger.debug("pct_comp_df.shape: {}".format(pct_comp_df.shape))
    return pct_comp_df

def add_labels_based_on_sample_id(percentile_df, pct_comp_df):
    percentile_df["label"] = [pct_comp_df.loc[x, "label"] for x in percentile_df.sample_id]
    logger.debug("percentile_df.shape: {}".format(percentile_df.shape))
    return percentile_df


def save_to_tsv(dir_path, filetemplate, dataframe):
    out_f = os.path.join(
    dir_path,
    filetemplate.format(dataframe.shape[0], dataframe.shape[1])
    )
    logger.debug("out_f: {}".format(out_f))
    dataframe.to_csv(out_f, sep="\t")

    return out_f

def create_and_save_genebody_coverage_graph(y_col, output_dir, percentile_df, filetemplate):
    logger.debug("y_col: {}".format(y_col))
    
    fig = pltexpr.line(percentile_df, x="genebody_pct", y=y_col, color="label", title="read {} vs. genebody location".format(y_col))


    output_filepath = os.path.join(output_dir, filetemplate.format(y_col))
    logger.debug("output_filepath: {}".format(output_filepath))

    fig.write_html(output_filepath, include_plotlyjs="cdn")

    return output_filepath

def create_and_save_histograms(measure, output_dir, pct_comp_df, filetemplate):
    hist_counts,hist_bins = numpy.histogram(pct_comp_df[measure], bins="auto")
    logger.debug("hist_counts: {}".format(hist_counts))
    x = hist_bins[:-1] + numpy.diff(hist_bins)

    fig = pltexpr.line(x=x, y=hist_counts, title="histogram of asymmetry values: difference in coverage 80th - 20th percentiles")
    fig.data[0].update(mode='markers+lines')
    

    output_filepath = os.path.join(output_dir, filetemplate.format(measure))
    logger.debug("output_filepath: {}".format(output_filepath))

    fig.write_html(output_filepath, include_plotlyjs="cdn")

    return output_filepath


def main(args):

    #setting up output templates 
    output_template_dict = build_output_template_dict(args.output_file_prefix)

    #search inputdir for files 
    input_files = input_file_search(args.input_dir)

    #convert files to data frames
    inp_df_list = load_genebody_coverage_data(input_files)

    #merge df into one
    counts_df = merge_dfs_into_one(inp_df_list)

    #sum coverage counts 
    sum_counts_df = sum_counts(counts_df)

    #converge percentile df 
    percentile_df = calculate_percentile_df(counts_df, sum_counts_df)

    #create pct_df_list
    pct_df_list = create_pct_df_list(percentile_df)

    #merge pct_df_list into one df
    pct_comp_df = create_pct_comp_df(pct_df_list)

    #add label column to pct_comp_df 
    pct_comp_df = add_label_col(pct_comp_df)

    #add label column to percentile df
    percentile_df = add_labels_based_on_sample_id(percentile_df, pct_comp_df)

    #save pct_comp_df and percentile_df to tsv in output dir
    save_to_tsv(args.output_dir, output_template_dict["compare_80_20"], pct_comp_df)
    save_to_tsv(args.output_dir, output_template_dict["all_pct"], percentile_df)

    #create line graphs for coverage counts and coverage percentiles 
    create_and_save_genebody_coverage_graph("coverage_counts", args.output_dir, percentile_df,output_template_dict["line_html"])
    create_and_save_genebody_coverage_graph("coverage_percentile", args.output_dir, percentile_df, output_template_dict["line_html"])

    #create and save histograms for coverage_diff and cov_diff_pct
    create_and_save_histograms("coverage_diff", args.output_dir, pct_comp_df, output_template_dict["histogram_html"])
    create_and_save_histograms("cov_diff_pct", args.output_dir, pct_comp_df, output_template_dict["histogram_html"])









if __name__ == "__main__":
    args = build_parser().parse_args(sys.argv[1:])

    setup_logger.setup(verbose=args.verbose)

    logger.debug("args:  {}".format(args))

    main(args)
