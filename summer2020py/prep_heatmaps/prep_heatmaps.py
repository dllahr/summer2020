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
    parser.add_argument("--hostname", help="lims db host name", type=str, default="getafix-v")

    parser.add_argument("--sourcedir", "-s", help = "source directory, where the DGE data is and where the heatmaps will be created", type = str, required = True )
    parser.add_argument("--expirmentid", "-e", help = "id of the expirment", type = str, required = True)
    
    parser.add_argument("--dgestatsforheatmaps", "-d", help = "dge stats for heatmaps",type = str,  default = ["logFC", "t"])
    parser.add_argument("--basedatapath", "-b", help = "path to directory with experiment id in it", type = str, default = "/data/experiments/RNA_SEQ/")
    parser.add_argument("--relativepath", "-r", help = "path from experiment id to where you want the heatmaps", type = str, default = "/analysis/heatmaps/")
    parser.add_argument("--server", "-s", help = "server for the heatmaps to be put onto", type = str, default = "http://fht.samba.data/fht_morpheus.html?gctData=")

    parser.add_argument("--config_filepath", help="path to config file containing information about how to connect to CDD API, ArxLab API etc.",
        type=str, default=summer2020py.default_config_filepath)
    parser.add_argument("--config_section", help="section of config file to use for information about how to connect to CDD API, ArxLab API etc.",
        type=str, default=summer2020py.default_config_section)

    
    return parser


def prepare_output_dir(source_dir):
    heatmap_dir = os.path.join(source_dir, "heatmaps")
    logger.debug("heatmap_dir: {}".format(heatmap_dir))
    #if the path heatmaps exists in source_dir, delete it
    if os.path.exists(heatmap_dir):
        shutil.rmtree(heatmap_dir)

    os.mkdir(heatmap_dir) #create the path heatmaps in source_dir
    return heatmap_dir

def  find_DGE_files(source_dir, experiment_id):
    dge_file_list = glob.glob(
    os.path.join(source_dir, "dge_data", experiment_id + "_*_DGE_r*.txt")
    )
    #set equa to dge_file_list all the files in source dir, in dge_data that start with the experiment id and end with _*_DGE_r*.txt where * is wildcard

    dge_file_list.sort()
    #sort the file list

    logger.debug("len(dge_file_list): {}".format(len(dge_file_list)))
    logger.debug("dge_file_list\n{}".format(dge_file_list))

    return(dge_file_list)

def read_DGE_files(dge_file_list):
    dge_df_list = [
    (pandas.read_csv(dge_file, sep="\t", index_col=0),
    os.path.basename(dge_file))
    for dge_file in dge_file_list
    ]
    #this is a list comprehension, it is the same as the code in the comment below
        # for dge_file in dge_file_list
            #dge_df_list.append(pandas.read_csv(dge_file, sep="\t", index_col=0),os.path.basename(dge_file))
    
    logger.debug([x[0].shape for x in dge_df_list])
    #another list comprhension this one is the same as this
        #for x in dge_df_list
            #[x[0]].shape
    
    #print out the name and data frame head of each tuple in list
    for dge_df, dge_file in dge_df_list:
        logger.debug("dge_file: {}".format(dge_file))
        logger.debug("dge_df.head()\n{}".format(dge_df.head()))
    
    return dge_df_list

def prepare_GCToo_objects(dge_stats_for_heatmaps, dge_df_list):
    heatmap_gct_list = []

    # for dge_df in dge_df_list:
    for dge_stat in dge_stats_for_heatmaps:
        row_metadata_df = dge_df_list[0][0][["gene_symbol"]]
        
        col_metadata_dict = {}
        extract_df_list = []
        for dge_df, dge_file in dge_df_list:
            basename = os.path.splitext(dge_file)[0]
            annotation_values = basename.split("_")
            annotation_str = "_".join(annotation_values[1:-2])
            logger.debug("annotation_str: {}".format(annotation_str))
            
            
            extract_df = dge_df[[dge_stat]]
            col_id  = dge_stat + "_" + annotation_str
            extract_df.columns = [col_id]
            #display(extract_df.head())
            extract_df_list.append(extract_df)
        
            col_metadata_dict[col_id] = annotation_values
        
        combined_df = pandas.concat(extract_df_list, axis=1)
        logger.debug("combined_df.shape: {}".format(combined_df.shape))
        logger.debug("combined_df.head()\n{}".format(combined_df.head()))
        
        col_metadata_df = pandas.DataFrame(col_metadata_dict).T
        col_metadata_df = col_metadata_df.loc[combined_df.columns]
        col_metadata_df.columns = ["annot{}".format(c) for c in col_metadata_df.columns]
        col_metadata_df["dge_statistic"] = dge_stat
        logger.debug("col_metadata_df: {}".format(col_metadata_df))

        heatmap_g = GCToo.GCToo(combined_df, col_metadata_df=col_metadata_df, row_metadata_df=row_metadata_df)
        logger.debug("heatmap_g: {}".format(heatmap_g))
        heatmap_gct_list.append((dge_stat, heatmap_g))

    logger.debug("len(heatmap_gct_list): {}".format(len(heatmap_gct_list)))
    logger.debug([(dge_stat, heat_g.data_df.shape) for dge_stat, heat_g in heatmap_gct_list])
    return heatmap_gct_list

def write_GCToo_objects_to_files(heatmap_gct_list, output_template, heatmap_dir):
    for dge_stat, heatmap_g in heatmap_gct_list:
        output_filename = output_template.format(
            dge_stat=dge_stat, rows=heatmap_g.data_df.shape[0], cols=heatmap_g.data_df.shape[1]
        )
        heatmap_g.src = output_filename
    
        output_filepath = os.path.join(heatmap_dir, output_filename)
        logger.debug("output_filepath: {}".format(output_filepath))
    
        write_gct.write(heatmap_g, output_filepath)

def prepare_links(heatmap_gct_list, url_template, base_data_path):
    url_list = []

    for dge_stat, heatmap_g in heatmap_gct_list:
        data_path = os.path.join(base_data_path, heatmap_g.src)
        logger.debug("data_path: {}".format(data_path))
    
        cur_url = url_template.format(data_path=data_path)
        logger.debug("cur_url: {}".format(cur_url))
    
        url_list.append((dge_stat, cur_url))
    logger.debug(len(url_list))
    return url_list

def write_to_html(heatmap_dir, output_html_link_file, url_list, experiment_id):
    html_filepath = os.path.join(heatmap_dir, output_html_link_file)
    logger.debug(html_filepath)
    logger.debug("")

    a_lines = ["""<li><a href="{url}"> heatmap of dge statistic:  {dge_stat}</a></li>
    """.format(url=url, dge_stat=dge_stat) for dge_stat, url in url_list]

    html = ("""<html>
    <body>
    <h1>{exp_id} links to interactive heatmaps of differential gene expression (DGE) statistics</h1>
    <ul>""".format(exp_id=experiment_id)
    + "".join(a_lines)
    + """</ul>
    </body>
    </html>"""
    )

    logger.debug(html)
    logger.debug("")
    
    f = open(html_filepath, "w")
    f.write(html)
    f.close()


def main(args):
    output_template = args.experimentid + "_heatmap_{dge_stat}_r{rows}x{cols}.gct"
    logger.debug("output_template{}".format(output_template))
    #the output template that will be used later 

    base_data_path = "{base_path}{exp_id}{relative_path}".format(base_path = args.basedatapath, exp_id= args.experimentid, relative_path = args.relativepath)
    logger.debug(base_data_path)
    #where the data is 

    url_template = "{server}{data_path}".format(server = args.server)
    logger.debug("url_template: {}".format(url_template))
    #template for the urls that will be used later

    output_html_link_file = "{exp_id}_interactive_heatmap_links.html".format(exp_id= args.experimentid)
    logger.debug("output_html_link_file: {}".format(output_html_link_file))
    #the file name of the html file that will have all the urls for the heatmaps

    heatmap_dir = prepare_output_dir(args.source_dir)
    #prpare the output directory 

    dge_file_list = find_DGE_files(args.source_dir, args.experimentid)
    #finding the DGE files and saving them to dge file list

    dge_df_list = read_DGE_files(dge_file_list)
    #reading the DGE files and returning a list with the data instead of a list with csv in it

    heatmap_gct_list = prepare_GCToo_objects(args.dgestatsforheatmaps, dge_df_list)
    #prpare GCToo objects

    write_GCToo_objects_to_files(heatmap_gct_list, output_template, heatmap_dir)
    #writing GCToo objects to files

    url_list = prepare_links(heatmap_gct_list, url_template, base_data_path)
    #creating list of urls that will be added to file

    write_to_html(heatmap_dir, output_html_link_file, url_list, args.experimentid)
    #writing url list to html file




if __name__ == "__main__":
    args = build_parser().parse_args(sys.argv[1:])

    setup_logger.setup(verbose=args.verbose)

    logger.debug("args:  {}".format(args))

    main(args)
