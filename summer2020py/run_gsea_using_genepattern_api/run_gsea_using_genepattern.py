import logging
import summer2020py
import summer2020py.setup_logger as setup_logger
import argparse
import sys
import os
import glob
import zipfile
import shutil

import pandas

import gp


logger = logging.getLogger(setup_logger.LOGGER_NAME)


def build_parser():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--verbose", "-v", help="Whether to print a bunch of output.", action="store_true", default=False)
    parser.add_argument("--hostname", help="lims db host name", type=str, default="getafix-v")


    parser.add_argument("--sourcedir", "-s", help = "source directory, where the DGE data is and where the heatmaps will be created", type = str, required = True )
    parser.add_argument("--experimentid", "-e", help = "id of the expirment", type = str, required = True)
    
    parser.add_argument("--dgestatsforrnklist", "-d", help = "dge stats for heatmaps",  default = ["logFC", "t"])

    parser.add_argument("--gpserver", "-gps", help = "gp server", required = True)
    parser.add_argument("--gpusername", 'gpu', help = "gp password", required = True)
    parser.add_argument("--gppassword", 'gpp', help = "gp password", required = True)

    #could make the default args for this dave's username password and server path, and then removed required but not going to do that now
    
    return parser


def prepare_output_dir(source_dir):
    gsea_dir = os.path.join(source_dir, "gsea")
    logger.debug("gsea_dir: {}".format(gsea_dir))
    if os.path.exists(gsea_dir):
        shutil.rmtree(gsea_dir)
    os.mkdir(gsea_dir)

    rnk_dir = os.path.join(gsea_dir, "rnk")
    logger.debug("rnk_dir: {}".format(rnk_dir))
    os.mkdir(rnk_dir)
    return gsea_dir, rnk_dir

def find_DGE_files(source_dir, experiment_id):
    dge_file_list = glob.glob(
    os.path.join(source_dir, "dge_data", experiment_id + "_*_DGE_r*.txt")
    )
    dge_file_list.sort()
    logger.debug("len(dge_file_list): {}".format(len(dge_file_list)))
    logger.debug("dge_file_list: \n {}".format(dge_file_list))
    return dge_file_list

def build_all_rnk_files(dge_file_list, dge_stats_for_rnk_list, rnk_dir):
    input_rnk_files_list = []

    for dge_file in dge_file_list[:]:
        logger.debug("dge_file: {}".format(dge_file))
        dge_df = pandas.read_csv(dge_file, sep="\t")
        logger.debug("dge_df.shape: {}".format(dge_df.shape))
        
        base_dge_filename = os.path.splitext(os.path.basename(dge_file))[0]
        logger.debug("base_dge_filename: {}".format(base_dge_filename))
        
        base_output_filename = "_".join(base_dge_filename.split("_")[:-2])
        logger.debug("base_output_filename: {}".format(base_output_filename))
        
        for dge_stat_for_rnk in dge_stats_for_rnk_list:

            rnk_df, output_filepath = build_rnk_file(dge_df, dge_stat_for_rnk, base_output_filename, rnk_dir)
            
            input_rnk_files_list.append(output_filepath)
            rnk_df.to_csv(output_filepath, sep="\t", index=False)
        
        logger.debug("")

        logger.debug("len(input_rnk_files_list): {}".format(len(input_rnk_files_list)))
        logger.debug("input_rnk_files_list: \n {}".format(input_rnk_files_list))

        return input_rnk_files_list

def build_rnk_file(dge_df, dge_stat_for_rnk, base_output_filename, rnk_dir):
    rnk_df = rnk_df = dge_df.loc[~pandas.isnull(dge_df.gene_symbol), 
                                ["gene_symbol", dge_stat_for_rnk]].copy()
    new_cols = list(rnk_df.columns)
    new_cols[0] = "#" + new_cols[0]
    rnk_df.columns = new_cols
    logger.debug("rnk_df.head(): \n {}".format(rnk_df.head()))
        
    output_rnk_file = base_output_filename + "_{dge_stat}_r{rows}x{cols}.rnk".format(
    dge_stat=dge_stat_for_rnk, rows=rnk_df.shape[0], cols=rnk_df.shape[1]
    )
    logger.debug("output_rnk_file: {}".format(output_rnk_file))
        
    output_filepath = os.path.join(rnk_dir, output_rnk_file)

    return rnk_df, output_filepath


def create_gp_server(gp_url, gp_username, gp_password):
    # Create a GenePattern server proxy instance
    gpserver = gp.GPServer(gp_url, gp_username, gp_password)
    return gpserver

def upload_input_gp_files(input_rnk_files_list, gpserver):
    # upload input files
    input_gp_files_list = []

    for input_file in input_rnk_files_list:
        uploaded_file_name = os.path.basename(input_file)
        logger.debug("uploaded_file_name: {}".format(uploaded_file_name))

        input_gp_file = gpserver.upload_file(uploaded_file_name, input_file)
        #print(dir(input_gp_file))
        logger.debug("input_gp_file.get_url(): {}".format(input_gp_file.get_url()))
        input_gp_files_list.append(input_gp_file)

    return input_gp_files_list

def task_list(gpserver):
    # Get the list of tasks
    task_list = gpserver.get_task_list()

    gsea_task_list = [x for x in task_list if "gsea" in x.get_name().lower()]
    logger.debug("len(gsea_task_list):{}".format(len(gsea_task_list)))
    logger.debug("[x.get_name() for x in gsea_task_list] \n {}".format([x.get_name() for x in gsea_task_list]))

    t = [x for x in gsea_task_list if x.get_name() == "GSEAPreranked"]
    assert len(t) == 1
    gsea_preranked_task = t[0]
    logger.debug("dir(gsea_preranked_task): {}".format(dir(gsea_preranked_task)))
    logger.debug("gsea_preranked_task.name: {}".format(gsea_preranked_task.name))
    logger.debug("gsea_preranked_task.lsid: {}".format(gsea_preranked_task.lsid))

    gsea_preranked_module = gp.GPTask(gpserver, gsea_preranked_task.lsid)
    logger.debug("dir(gsea_preranked_module): {}".format(dir(gsea_preranked_module)))

    return gsea_preranked_module

def create_params_list(gsea_preranked_module):
    # Get the list of GPTaskParam objects
    params_list = gsea_preranked_module.get_parameters()

    print_param_info(params_list)

    print_valid_param_choices(params_list)

    return params_list


def print_param_info(params_list):
    for param in params_list:              # Loop through each parameter
        logger.debug("param.get_name(): {}".format(param.get_name()) )          # Print the parameter's name
        logger.debug( "type: {}".format(param.get_type()) )          # Print the parameter's type (text, number, file, etc.)
        logger.debug( param.get_description() )   # Print the parameter's description
        logger.debug( "default_value: {}".format(param.get_default_value()) ) # Print the parameter's default value
        logger.debug( "is_optional: {}".format(param.is_optional() ))       # Print whether the parameter is optional
        logger.debug( '' )                        # Leave a blank line between printed parameters

def print_valid_param_choices(params_list):
    for param in params_list:
        if param.is_choice_param():        # If the parameter is a choice param
            logger.debug("param.get_name(): {}".format(param.get_name()) )       # Print the parameter's name
            
            choices = param.get_choices()  # Get a list of valid choices 
            for choice in choices:         # Print the label and value for each choice
                logger.debug( choice['label'] + " = " + choice['value'] )
                
            # Print the default selected value for each choice
            logger.debug("param.get_choice_selected_value(): {}".format(param.get_choice_selected_value() ))
            logger.debug(" ")

def create_reference_geneset_urls(params_list, reference_genesets):
    genesets_param = [x for x in params_list if x.get_name().startswith("gene.sets.database")]
    assert len(genesets_param) == 1, len(genesets_param)
    genesets_param = genesets_param[0]

    reference_geneset_urls = []
    for group_name, group_geneset_labels in reference_genesets:
        logger.debug("group_name: {}".format(group_name))
        
        matching_geneset_choices = [x for x in genesets_param.get_choices() if x["label"] in group_geneset_labels]
        logger.debug("len(matching_geneset_choices): {}".format(len(matching_geneset_choices)))
        check = set([x["label"] for x in matching_geneset_choices])
        assert check == group_geneset_labels, (len(check), len(group_geneset_labels), check, group_geneset_labels)
        
        reference_geneset_urls.append((
            group_name, [x["value"] for x in matching_geneset_choices]
        ))

    logger.debug(" ")
    logger.debug("len(reference_geneset_urls): {}".format(len(reference_geneset_urls)))
    logger.debgug("\n\n {}".format([str(x) for x in reference_geneset_urls]))

    return reference_geneset_urls

def create_all_job_spec_list(num_permutations, job_memory, input_gp_files_list, reference_geneset_urls, gsea_preranked_module):
    all_job_spec_list = []

    change_default_params = {"number.of.permutations": str(num_permutations),
                            "collapse.dataset": "No_Collapse"}

    add_params = {"job.memory":job_memory}
        
    for input_gp_file in input_gp_files_list:
        for gs_group_name, gs_urls in reference_geneset_urls:
            # Create the GPJobSpec
            job_spec = gsea_preranked_module.make_job_spec()
    #         print(dir(job_spec))

            for param_name,param_value in add_params.items():
                job_spec.set_parameter(param_name, param_value)

            # Loop through all the parameters and set their default values
            for param in gsea_preranked_module.get_parameters():  
                # If the parameter has a default value, set that value
                param_name = param.get_name()
                param_default_value = param.get_default_value()
    #             print(param_name, param_default_value)

                if param_name in change_default_params:
                    job_spec.set_parameter(param_name, change_default_params[param_name])
                elif param.get_default_value() != None: 
                    # Set the default value
                    job_spec.set_parameter(param_name, param_default_value)

            # Attach the input file to the correct parameter
            job_spec.set_parameter("ranked.list", input_gp_file.get_url()) 

            job_spec.set_parameter("gene.sets.database", gs_urls)
                #["ftp://gpftp.broadinstitute.org/module_support_files/msigdb/gmt/c1.all.v7.1.symbols.gmt"])

            # job_spec.set_parameter("number.of.permutations", "10")
    #       job_spec.params

            all_job_spec_list.append((gs_group_name, job_spec))

    logger.debug("len(all_job_spec_list): {}".format(len(all_job_spec_list)))
    logger.debug("[x for x in all_job_spec_list]: {}".format([x for x in all_job_spec_list]))

    return all_job_spec_list

def print_all_job_spec_list(all_job_spec_list):
    logger.debug("all_job_spec_list[0][0]: {}".format(all_job_spec_list[0][0]))
    t = all_job_spec_list[0][1]
    dir(t)
    t.params


def create_job_list(all_job_spec_list, gpserver):
    job_list = []

    for gs_group_name, job_spec in all_job_spec_list:
        # This will return the job object and continue execution even if the job isn't finished
        job = gpserver.run_job(job_spec, False)
    #     print(dir(job))

        # Prints a brief description of the job's current state
        logger.debug( job.get_status_message() )

        # Quaries the server and returns True if the job is complete, False otherwise
        logger.debug( job.is_finished() )

        job_list.append((gs_group_name, job))
    #     job.wait_until_done()

    for i, (gs_group_name, job) in enumerate(job_list):
        logger.debug("waiting on job index i:  {}".format(i))
        job.wait_until_done()

    return job_list

def create_zip_dir(gsea_dir):
    zip_dir = os.path.join(gsea_dir, "zip_files")
    if not os.path.exists(zip_dir):
        os.mkdir(zip_dir)
    return zip_dir


def prepare_zip_files_list(job_list, zip_dir):
    zip_files_list = []

    no_zip_files = []

    for gs_group_name, job in job_list:
    #     print(gs_group_name)

        t = [x for x in job.get_output_files() if x.get_name().endswith(".zip")]
        
        if len(t) == 1:
            dl_filepath = if_len_t_1(t, zip_dir, gs_group_name)

            zip_files_list.append(dl_filepath)
            
        elif len(t) == 0:
            logger.debug("********************* ALERT! ************************")
            logger.debug("Zip file not found may mean job failed to run")
            logger.debug("gs_group_name: {}".format(gs_group_name))
            no_zip_files.append((gs_group_name, job))
            logger.debug("*****************************************************")
        else:
            logger.debug("********************* WARNING ************************")
            logger.debug("More than 1 zip file found in job output, skipping")
            logger.debug("gs_group_name: {}".format(gs_group_name))
            logger.debug("*****************************************************")
        
    logger.debug()
    logger.debug("#####################################")
    logger.debug("info about zip_files_list:")
    logger.debug(len(zip_files_list))
    logger.debug("\n".join(zip_files_list))
    logger.debug()

    return zip_files_list, no_zip_files

def if_len_t_1(t, zip_dir, gs_group_name):
    zip_output_file = t[0]
    #print(zip_output_file.get_name())
    #print(zip_output_file.get_url())

    dl_filename = os.path.splitext(zip_output_file.get_name())[0] + "_" + gs_group_name + ".zip"
    #print(dl_filename)

    dl_filepath = os.path.join(zip_dir, dl_filename)
    

    logger.debug(zip_output_file.get_url())
    logger.debug(dl_filepath)

    f = open(dl_filepath, "wb")
    f.write(zip_output_file.open().read())
    f.close()

    return dl_filepath



def print_no_zip_flies(no_zip_files):
    for gs_group_name, job in no_zip_files:
        logger.debug(gs_group_name)
        logger.debug(job.job_number)
        logger.debug(job.get_job_status_url())
        logger.debug([x.get_name() for x in job.get_output_files()])


def zipping_zip_files(zip_files_list, gsea_dir):
    for zip_file in zip_files_list:
    #     print(zip_file)
        
        dir_name = os.path.splitext(
            os.path.basename(zip_file)
        )[0]
        
        extract_dir = os.path.join(gsea_dir, dir_name)
        print(extract_dir)
        
        if os.path.exists(extract_dir):
            shutil.rmtree(extract_dir)
        os.mkdir(extract_dir)
        
        my_zipfile = zipfile.ZipFile(zip_file, "r")
        my_zipfile.extractall(extract_dir)

def main(args):
    logger.info("run_gsea_using_genepattern")
    source_dir = args.sourcedir
    experiment_id = args.experiment_id

    dge_stats_for_rnk_list = args.dgestatsforrnklist

    num_permutations = 1000

    job_memory = "4 Gb"

    # guidance from GenePattern forum:
    # gseapreranked_job_spec.set_parameter("job.memory", "2 Gb")
    # gseapreranked_job_spec.set_parameter("job.queue", "gp-cloud-default")
    # gseapreranked_job_spec.set_parameter("job.cpuCount", "1")
    # gseapreranked_job_spec.set_parameter("job.walltime", "02:00:00")

    reference_genesets = [
    ("all", {"c1.all.v7.1.symbols.gmt [Positional]", "c2.all.v7.1.symbols.gmt [Curated]", "c3.all.v7.1.symbols.gmt [Motif]",
     "c5.all.v7.1.symbols.gmt [Gene Ontology]", "c6.all.v7.1.symbols.gmt [Oncogenic Signatures]",
     "c7.all.v7.1.symbols.gmt [Immunologic signatures]", "h.all.v7.1.symbols.gmt [Hallmarks]"}),
    ("just_hallmarks", {"h.all.v7.1.symbols.gmt [Hallmarks]"})
    ]
    logger.debug("len(reference_genesets): {}".format(len(reference_genesets)))
    logger.debug([(k,len(v)) for k,v in reference_genesets])

    gp_username = args.gpusername
    gp_password = args.gppassword
    gp_url = args.gpserver


    gsea_dir, rnk_dir = prepare_output_dir(source_dir)

    dge_file_list = find_DGE_files(source_dir, experiment_id)

    input_rnk_files_list = build_all_rnk_files(dge_file_list, dge_stats_for_rnk_list, rnk_dir)

    gpserver = create_gp_server(gp_url, gp_username, gp_password)

    input_gp_files_list = upload_input_gp_files(input_rnk_files_list, gpserver)

    gsea_preranked_module = task_list(gpserver)

    params_list = create_params_list(gsea_preranked_module)

    reference_geneset_urls = create_reference_geneset_urls(params_list, reference_genesets)

    all_job_spec_list = create_all_job_spec_list(num_permutations, job_memory, input_gp_files_list, reference_geneset_urls, gsea_preranked_module)

    print_all_job_spec_list(all_job_spec_list)

    job_list = create_job_list(all_job_spec_list, gpserver)

    zip_dir = create_zip_dir(gsea_dir)

    zip_files_list, no_zip_files = prepare_zip_files_list(job_list, zip_dir)

    print_no_zip_flies(no_zip_files)

    zipping_zip_files(zip_files_list, gsea_dir)






if __name__ == "__main__":
    args = build_parser().parse_args(sys.argv[1:])

    setup_logger.setup(verbose=args.verbose)

    logger.debug("args:  {}".format(args))

    main(args)
