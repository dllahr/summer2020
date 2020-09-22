import logging
import summer2020py
import summer2020py.setup_logger as setup_logger
import argparse
import sys
import os
import shutil
import glob
import pandas
import cmapPy.pandasGEXpress.GCToo as GCToo
import cmapPy.pandasGEXpress.write_gct as write_gct


logger = logging.getLogger(setup_logger.LOGGER_NAME)


def build_parser():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--verbose", "-v", help="Whether to print a bunch of output.", action="store_true", default=False)

    parser.add_argument("--source_analysis_dir", "-s", 
        help = "source directory containin analysis, where the DGE data is found and where the heatmaps (subdirectory) will be created",
        type = str, required = True)
    parser.add_argument("--experiment_id", "-e", help = "id of the expirment", type = str, required = True)
    
    parser.add_argument("--dge_stats_for_heatmaps", "-d", help = "dge stats for heatmaps",  default = ["logFC", "t"])
    parser.add_argument("--base_server_data_path", "-b", help = "base path to directory on server with subfolders of experiment id in it", 
        type = str, default = "/data/experiments/RNA_SEQ/")
    parser.add_argument("--relative_analysis_path", "-r", 
        help = """relative path from directory for specific experiment to analysis directory""",
        type = str, default = "analysis/")
    parser.add_argument("--base_url", "-u", help = "base url for the heatmaps to be put onto", type = str, default = "http://fht.samba.data/fht_morpheus.html?gctData=")

    parser.add_argument("--dge_dir_name", "-ddn", 
        help="name of subdirectory in source_analysis_dir that contains differential gene expression (dge) data tables",
        type=str, default="dge_data")

    parser.add_argument("--config_filepath", help="path to config file containing information about how to connect to CDD API, ArxLab API etc.",
        type=str, default=summer2020py.default_config_filepath)
    parser.add_argument("--config_section", help="section of config file to use for information about how to connect to CDD API, ArxLab API etc.",
        type=str, default=summer2020py.default_config_section)

    
    return parser


def prepare_output_dir(source_analysis_dir):
    heatmap_dir = os.path.join(source_analysis_dir, "heatmaps")
    logger.debug("heatmap_dir: {}".format(heatmap_dir))
    #if the path heatmaps exists in source_dir, delete it
    if os.path.exists(heatmap_dir):
        shutil.rmtree(heatmap_dir)

    os.mkdir(heatmap_dir) #create the path heatmaps in source_dir
    return heatmap_dir


def  find_DGE_files(source_analysis_dir, dge_dir_name, experiment_id):
    dge_file_list = glob.glob(
        os.path.join(source_analysis_dir, dge_dir_name, experiment_id + "_*_DGE_r*.txt")
    )
    #set equal to dge_file_list all the files in source dir, in dge_data that start with the experiment id and end with _*_DGE_r*.txt where * is wildcard

    dge_file_list.sort()
    #sort the file list

    logger.debug("len(dge_file_list): {}".format(len(dge_file_list)))
    logger.debug(
        "dge_file_list:\n{}".format(
            "\n".join(dge_file_list)
        )
    )

    return(dge_file_list)


def read_DGE_files(dge_file_list):
    dge_df_list = [
        (
            pandas.read_csv(dge_file, sep="\t", index_col=0),
            os.path.basename(dge_file)
        )
        for dge_file in dge_file_list
    ]
    #this is a list comprehension, it is the same as the code in the comment below
    # dge_df_list = []
    # for dge_file in dge_file_list
    #   dge_df_list.append(pandas.read_csv(dge_file, sep="\t", index_col=0),os.path.basename(dge_file))
    
    logger.debug([x[0].shape for x in dge_df_list])
    #another list comprhension this one is the same as this
        #for x in dge_df_list
            #[x[0]].shape
    
    #print out the name and data frame head of each tuple in list
    for dge_df, dge_file in dge_df_list:
        logger.debug("dge_file: {}".format(dge_file))
        logger.debug("dge_df.head()\n{}".format(dge_df.head()))
    
    return dge_df_list


def prepare_all_GCToo_objects(dge_stats_for_heatmaps, dge_df_list):
    heatmap_gct_list = []

    for dge_stat in dge_stats_for_heatmaps:

        heatmap_g = prepare_GCToo_object(dge_stat, dge_df_list)

        heatmap_gct_list.append((dge_stat, heatmap_g))

    logger.debug("len(heatmap_gct_list): {}".format(len(heatmap_gct_list)))
    logger.debug([(dge_stat, heat_g.data_df.shape) for dge_stat, heat_g in heatmap_gct_list])
    return heatmap_gct_list


def prepare_data_df(dge_stat, dge_df_list):
    extract_df_list = []
    
    for dge_df, dge_file in dge_df_list:
        basename = os.path.splitext(dge_file)[0]
        annotation_values = basename.split("_")
        annotation_str = "_".join(annotation_values[1:-2])
        logger.debug("annotation_str: {}".format(annotation_str))

        extract_df = dge_df[[dge_stat]]
        col_id  = dge_stat + "_" + annotation_str
        extract_df.columns = [col_id]
        logger.debug("extract_df.head():\n{}".format(extract_df.head()))

        extract_df_list.append(extract_df)

    data_df = pandas.concat(extract_df_list, axis=1)
    logger.debug("data_df.shape: {}".format(data_df.shape))
    logger.debug("data_df.head()\n{}".format(data_df.head()))
    
    return data_df


def prepare_col_metadata(dge_stat, data_df_columns):
    col_meta_list = [x.split("_") for x in data_df_columns]
    col_metadata_df = pandas.DataFrame(col_meta_list)
    col_metadata_df.columns = ["annot{}".format(c) for c in col_metadata_df.columns]
    col_metadata_df["dge_statistic"] = dge_stat
    col_metadata_df.index = data_df_columns
    logger.debug("col_metadata_df: \n{}".format(col_metadata_df.head()))
    return col_metadata_df


def prepare_GCToo_object(dge_stat, dge_df_list):
    row_metadata_df = dge_df_list[0][0][["gene_symbol"]]

    data_df = prepare_data_df(dge_stat, dge_df_list)

    col_metadata_df = prepare_col_metadata(dge_stat, data_df.columns)

    heatmap_g = GCToo.GCToo(data_df, col_metadata_df=col_metadata_df, row_metadata_df=row_metadata_df)
    logger.debug("heatmap_g: {}".format(heatmap_g))
    return heatmap_g


def write_GCToo_objects_to_files(heatmap_gct_list, output_template, heatmap_dir):
    for dge_stat, heatmap_g in heatmap_gct_list:
        output_filename = output_template.format(
            dge_stat=dge_stat, rows=heatmap_g.data_df.shape[0], cols=heatmap_g.data_df.shape[1]
        )
        heatmap_g.src = output_filename
    
        output_filepath = os.path.join(heatmap_dir, output_filename)
        logger.debug("output_filepath: {}".format(output_filepath))
    
        write_gct.write(heatmap_g, output_filepath)


def prepare_links(heatmap_gct_list, url_template, output_server_path):
    url_list = []
    logger.debug("heatmap{}".format(heatmap_gct_list))

    for dge_stat, heatmap_g in heatmap_gct_list:
        data_path = os.path.join(output_server_path, "heatmaps", heatmap_g.src)
        logger.debug("data_path: {}".format(data_path))
    
        cur_url = url_template.format(data_path=data_path)
        logger.debug("cur_url: {}".format(cur_url))
    
        url_list.append((dge_stat, cur_url))
    logger.debug(len(url_list))
    logger.debug("url_list: \n{}".format(url_list))
    return url_list


def prepare_html(url_list, experiment_id):
    a_lines = [
        """\t<li><a href="{url}"> heatmap of dge statistic:  {dge_stat}</a></li>""".format(url=url, dge_stat=dge_stat) 
        for dge_stat, url in url_list
    ]

    html = (
        """<html>
<body>
<h1>{exp_id} links to interactive heatmaps of differential gene expression (DGE) statistics</h1>
<ul>
""".format(exp_id=experiment_id)

        + "\n".join(a_lines)

        + """
</ul>
</body>
</html>"""
    )
    logger.debug(html)
    logger.debug("")

    return html

def determine_html_filepath(heatmap_dir, output_html_link_file):
    html_filepath = os.path.join(heatmap_dir, output_html_link_file)
    logger.debug("html_filepath: {}".format(html_filepath))
    logger.debug("")

    return html_filepath


def write_html_to_file(html, html_filepath):
    logger.debug("writing html to html_filepath")
    f = open(html_filepath, "w")
    f.write(html)
    f.close()


def main(args):
    output_template = args.experiment_id + "_heatmap_{dge_stat}_r{rows}x{cols}.gct"
    logger.debug("output_template:  {}".format(output_template))
    #the output template that will be used later 
    
    output_server_path = os.path.join(args.base_server_data_path, args.experiment_id, args.relative_analysis_path)
    logger.debug("output_server_path:  {}".format(output_server_path))

    url_template = "{base_url}{{data_path}}".format(base_url = args.base_url)
    logger.debug("url_template: {}".format(url_template))
    #template for the urls that will be used later

    output_html_link_file = "{exp_id}_interactive_heatmap_links.html".format(exp_id=args.experiment_id)
    logger.debug("output_html_link_file: {}".format(output_html_link_file))
    #the file name of the html file that will have all the urls for the heatmaps

    heatmap_dir = prepare_output_dir(args.source_analysis_dir)
    #prepare the output directory 

    dge_file_list = find_DGE_files(args.source_analysis_dir, args.dge_dir_name, args.experiment_id)
    #finding the DGE files and saving them to dge file list

    dge_df_list = read_DGE_files(dge_file_list)
    #reading the DGE files and returning a list with the data instead of a list with csv in it

    heatmap_gct_list = prepare_all_GCToo_objects(args.dge_stats_for_heatmaps, dge_df_list)
    #prpare GCToo objects

    write_GCToo_objects_to_files(heatmap_gct_list, output_template, heatmap_dir)
    #writing GCToo objects to files

    url_list = prepare_links(heatmap_gct_list, url_template, output_server_path)
    #creating list of urls that will be added to file

    html_filepath = determine_html_filepath(heatmap_dir, output_html_link_file)
    #creating the filepath to where the html file will be

    html =  prepare_html(url_list, args.experiment_id)
    #creating the html that will be written to the file

    write_html_to_file(html, html_filepath)
    #writing the html to the file

    return html


if __name__ == "__main__":
    args = build_parser().parse_args(sys.argv[1:])

    setup_logger.setup(verbose=args.verbose)

    logger.debug("args:  {}".format(args))

    main(args)
