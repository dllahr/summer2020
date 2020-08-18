import unittest
import logging
import summer2020py.setup_logger as setup_logger
import summer2020py.run_gsea_using_genepattern_api.run_gsea_using_genepattern as rgug
import os
import tempfile
import pandas
import mock
import shutil
import pathlib
import zipfile


import gp



logger = logging.getLogger(setup_logger.LOGGER_NAME)

# Some notes on testing conventions (more in cuppers convention doc):
#    (1) Use "self.assert..." over "assert"
#        - self.assert* methods: https://docs.python.org/2.7/library/unittest.html#assert-methods
#       - This will ensure that if one assertion fails inside a test method,
#         exectution won't halt and the rest of the test method will be executed
#         and other assertions are also verified in the same run.
#     (2) For testing exceptions use:
#        with self.assertRaises(some_exception) as context:
#            [call method that should raise some_exception]
#        self.assertEqual(str(context.exception), "expected exception message")
#
#        self.assertAlmostEquals(...) for comparing floats
def random_of_input_file(name, dirs):
    #this method was supposed to randomize the file at path, I couldn't get it to work so it just copies the file 
    path = os.path.join("assets", "prep_heatmap_example_input_DGE_r10x10.txt")
    outputpath = os.path.join(dirs, name)

    shutil.copyfile(path, outputpath)

    return name

def create_mock_task(name, mocked_lsid):
    task = mock.Mock("mock of task")
    task.get_name = mock.Mock("mock of get_name of the task", return_value = str(name))
    task.name = str(name)
    task.lsid = mocked_lsid
    #a better mock may have task.lsid return something 
    return task
    
def create_mock_tasks_list(number):
    mock_task_list = []
    
    mock_task_list.append(create_mock_task("GSEAPreranked", 100))

    return mock_task_list


def create_genesetsdatabase_choices():
    choices = []
    choices.append({'label': "GSEAPrerankedlabel", 'value': "GSEAPrerankedvalue"})
    choices.append({'label': "c1.all.v7.1.symbols.gmt [Positional]", 'value': "ftp://gpftp.broadinstitute.org/module_support_files/msigdb/gmt/c1.all.v7.1.symbols.gmt"})
    choices.append({'label': "c2.all.v7.1.symbols.gmt [Curated]", 'value': "ftp://gpftp.broadinstitute.org/module_support_files/msigdb/gmt/c2.all.v7.1.symbols.gmt"})
    choices.append({'label': "c2.cgp.v7.1.symbols.gmt [Curated]", 'value': "ftp://gpftp.broadinstitute.org/module_support_files/msigdb/gmt/c2.cgp.v7.1.symbols.gmt"})
    choices.append({'label': "c2.cp.v7.1.symbols.gmt [Curated]", 'value': "ftp://gpftp.broadinstitute.org/module_support_files/msigdb/gmt/c2.cp.v7.1.symbols.gmt"})
    choices.append({'label': "c2.cp.biocarta.v7.1.symbols.gmt [Curated] ", 'value': "ftp://gpftp.broadinstitute.org/module_support_files/msigdb/gmt/c2.cp.biocarta.v7.1.symbols.gmt"})
    choices.append({'label': "c2.cp.kegg.v7.1.symbols.gmt [Curated]", 'value': "ftp://gpftp.broadinstitute.org/module_support_files/msigdb/gmt/c2.cp.kegg.v7.1.symbols.gmt"})
    choices.append({'label': "c2.cp.pid.v7.1.symbols.gmt [Curated]", 'value': "ftp://gpftp.broadinstitute.org/module_support_files/msigdb/gmt/c2.cp.pid.v7.1.symbols.gmt"})
    choices.append({'label': "c2.cp.reactome.v7.1.symbols.gmt [Curated]", 'value': "ftp://gpftp.broadinstitute.org/module_support_files/msigdb/gmt/c2.cp.reactome.v7.1.symbols.gmt"})
    choices.append({'label': "c3.all.v7.1.symbols.gmt [Motif]", 'value': "ftp://gpftp.broadinstitute.org/module_support_files/msigdb/gmt/c3.all.v7.1.symbols.gmt"})
    choices.append({'label': "c3.mir.v7.1.symbols.gmt [Motif]", 'value': "ftp://gpftp.broadinstitute.org/module_support_files/msigdb/gmt/c3.mir.v7.1.symbols.gmt"})
    choices.append({'label': "c3.tft.v7.1.symbols.gmt [Motif]", 'value': "ftp://gpftp.broadinstitute.org/module_support_files/msigdb/gmt/c3.tft.v7.1.symbols.gmt"})
    choices.append({'label': "c4.all.v7.1.symbols.gmt [Computational]", 'value': "ftp://gpftp.broadinstitute.org/module_support_files/msigdb/gmt/c4.all.v7.1.symbols.gmt"})
    choices.append({'label': "c4.cgn.v7.1.symbols.gmt [Computational]", 'value': "ftp://gpftp.broadinstitute.org/module_support_files/msigdb/gmt/c4.cgn.v7.1.symbols.gmt"})
    choices.append({'label': "c4.cm.v7.1.symbols.gmt [Computational]", 'value': "ftp://gpftp.broadinstitute.org/module_support_files/msigdb/gmt/c4.cm.v7.1.symbols.gmt"})
    choices.append({'label': "c5.all.v7.1.symbols.gmt [Gene Ontology]", 'value': "ftp://gpftp.broadinstitute.org/module_support_files/msigdb/gmt/c5.all.v7.1.symbols.gmt"})
    choices.append({'label': "c5.bp.v7.1.symbols.gmt [Gene Ontology]", 'value': "ftp://gpftp.broadinstitute.org/module_support_files/msigdb/gmt/c5.bp.v7.1.symbols.gmt"})
    choices.append({'label': "c5.cc.v7.1.symbols.gmt [Gene Ontology]", 'value': "ftp://gpftp.broadinstitute.org/module_support_files/msigdb/gmt/c5.cc.v7.1.symbols.gmt"})
    choices.append({'label': "c5.mf.v7.1.symbols.gmt [Gene Ontology]", 'value': "ftp://gpftp.broadinstitute.org/module_support_files/msigdb/gmt/c5.mf.v7.1.symbols.gmt"})
    choices.append({'label': "c6.all.v7.1.symbols.gmt [Oncogenic Signatures]", 'value': "ftp://gpftp.broadinstitute.org/module_support_files/msigdb/gmt/c6.all.v7.1.symbols.gmt"})
    choices.append({'label': "c7.all.v7.1.symbols.gmt [Immunologic signatures]", 'value': "ftp://gpftp.broadinstitute.org/module_support_files/msigdb/gmt/c7.all.v7.1.symbols.gmt"})
    choices.append({'label': "h.all.v7.1.symbols.gmt [Hallmarks]", 'value': "ftp://gpftp.broadinstitute.org/module_support_files/msigdb/gmt/h.all.v7.1.symbols.gmt"})
    return choices



def create_param(information):
    param = mock.Mock("mock of param")
    param.get_name = mock.Mock("mock of get name", return_value = information[0])
    param.get_type = mock.Mock("mock of get type", return_value = information[1])
    param.get_description = mock.Mock("mock of get description", return_value = information[2])
    param.get_default_value = mock.Mock("mock of get deault value", return_value = information[3])
    param.is_optional = mock.Mock("mock of is optional", return_value = information[4])
    param.is_choice_param = mock.Mock("mock of is choice param", return_value = information[5])
    if information[5]:
        param.get_choices = mock.Mock("mock of get choice", return_value = information[6])
        param.get_choice_selected_value = mock.Mock("mock of get choice seleced value", return_value = information[7])

    return param

def create_params_list_mock():
    mock_param_list = []

    genesetsdatabase = ["gene.sets.database", "file", "Gene sets database from GSEA website.", "None",False,  True,
    create_genesetsdatabase_choices() , "ftp://gpftp.broadinstitute.org/module_support_files/msigdb/gmt/c1.all.v7.1.symbols.gmt"]

    
    mock_param_list.append(create_param(genesetsdatabase))

    return mock_param_list

def job_params_list():
    job_list = [{'name': 'job.memory', 'values': ['4 Gb']},
    {'name': 'number.of.permutations', 'values': ['1000']},
    {'name': 'collapse.dataset', 'values': ['No_Collapse']},
    {'name': 'scoring.scheme', 'values': ['weighted']},
    {'name': 'max.gene.set.size', 'values': ['500']},
    {'name': 'min.gene.set.size', 'values': ['15']},
    {'name': 'collapsing.mode.for.probe.sets.with.more.than.one.match',
    'values': ['Max_probe']},
    {'name': 'normalization.mode', 'values': ['meandiv']},
    {'name': 'omit.features.with.no.symbol.match', 'values': ['true']},
    {'name': 'make.detailed.gene.set.report', 'values': ['true']},
    {'name': 'num.top.sets', 'values': ['20']},
    {'name': 'random.seed', 'values': ['timestamp']},
    {'name': 'create.svgs', 'values': ['false']},
    {'name': 'output.file.name', 'values': ['<ranked.list_basename>.zip']},
    {'name': 'create.zip', 'values': ['true']},
    {'name': 'dev.mode', 'values': ['false']},
    {'name': 'ranked.list',
    'values': ['https://cloud.genepattern.org/gp/users/dllahr/tmp/run5687728369687963663.tmp/H202SC20040591_FHT3794_921_QDx1_24h_Vehicle_921_QDx1_24h_logFC_r30144x2.rnk']},
    {'name': 'gene.sets.database',
    'values': ['ftp://gpftp.broadinstitute.org/module_support_files/msigdb/gmt/c1.all.v7.1.symbols.gmt',
    'ftp://gpftp.broadinstitute.org/module_support_files/msigdb/gmt/c2.all.v7.1.symbols.gmt',
    'ftp://gpftp.broadinstitute.org/module_support_files/msigdb/gmt/c3.all.v7.1.symbols.gmt',
    'ftp://gpftp.broadinstitute.org/module_support_files/msigdb/gmt/c5.all.v7.1.symbols.gmt',
    'ftp://gpftp.broadinstitute.org/module_support_files/msigdb/gmt/c6.all.v7.1.symbols.gmt',
    'ftp://gpftp.broadinstitute.org/module_support_files/msigdb/gmt/c7.all.v7.1.symbols.gmt',
    'ftp://gpftp.broadinstitute.org/module_support_files/msigdb/gmt/h.all.v7.1.symbols.gmt']}]

    return job_list



class TestRunGseaUsingGenepattern(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        global temp_wkdir_prefix 
        temp_wkdir_prefix = "test_run_gsea_using_genepattern"

        logger.debug("setUpClass")
        global gpserver_object 
        gpserver_object = mock.Mock("this mock of the gpserver object")

        global job_spec
        job_spec = mock.Mock("mock of job_spec")
        job_spec.set_parameter = mock.Mock("mock of set paramter of job spec")
        job_spec.params = mock.Mock("spec of params", return_value = job_params_list())

        
        gp.GPServer = mock.Mock("mock of gp.GPServer", return_value = gpserver_object)




        global gsea_preranked_module
        gsea_preranked_module = mock.Mock("mock of gp preanked modoule creaked from GPTask")
        gsea_preranked_module.param_load = mock.Mock("mock of params_load")
        gsea_preranked_module.get_parameters = mock.Mock("mock of get parameter", return_value = create_params_list_mock()) 

        gsea_preranked_module.make_job_spec = mock.Mock("mock of make job spec", return_value = job_spec)

        
        gp.GPTask = mock.Mock("mock of GPTask", return_value = gsea_preranked_module)
        
        global uploaded_gp_file
        uploaded_gp_file = mock.Mock("mock returned when .upload file is called")
        uploaded_gp_file.get_url = mock.Mock("mock of get url", return_value = "this is a placeholder hopefully your code doesn't rely on this for anything")

        gpserver_object.upload_file = mock.Mock("mock of upload file", return_value = uploaded_gp_file)

        gpserver_object.get_task_list = mock.Mock("mock of get task list", return_value = create_mock_tasks_list(1))


        opened_output_file = mock.Mock("mock of the open output file")
        opened_output_file.read = mock.Mock("mock of read the opened output file", return_value = b"hi")

        global output_file
        output_file = mock.Mock("mock of the output file returned when get output files is called")
        output_file.get_url = mock.Mock("mock of get url", return_value = "a url should be here")
        output_file.get_name = mock.Mock("mock of get name", return_value = "file.zip")
        output_file.open = mock.Mock("mock of open", return_value = opened_output_file)
       



        global job
        job = mock.Mock("mock of job")
        
        job.job_number = 1
        job.get_output_files = mock.Mock("mock of get outputfiles", return_value = [output_file])
        job.get_status_message = mock.Mock("mock of job get status message", return_value = "this is the staus message")
        job.is_finished = mock.Mock("mock of job is finished", return_value = True)
        job.wait_until_done = mock.Mock("mock of wait until done, does nothing when called")
        job.job_number = mock.Mock("mock of job number", return_value = "1")
        job.get_job_status_url = mock.Mock("mock of get staus url", return_value = "mockstatusurl")


        gpserver_object.run_job = mock.Mock("mock of run job", return_value = job)


        





    def test_prepare_output_directory(self):
        with tempfile.TemporaryDirectory(prefix=temp_wkdir_prefix) as wkdir:
            logger.debug("\n \n \n test_prepare_output_dir wkdir:  {}\n \n ".format(wkdir))

            # test_directory = os.path.join(wkdir, "output")
            # logger.debug("test_directory:  {}".format(test_directory))
            # self.assertFalse(os.path.exists(test_directory))

            # os.mkdir(test_directory)

            # run prepare_output_dir method
            gsea_dir, rnk_dir = rgug.prepare_output_dir(wkdir)

            # test that the output directories were created
            self.assertTrue(os.path.exists(gsea_dir))
            self.assertTrue(os.path.exists(rnk_dir))
            
            logger.debug("test that if we run the method and the directory exists, it is cleared out")
            test_file = os.path.join(gsea_dir, "test_file") #adding a file to that directory 
            f = open(test_file,"w")#opening the file in write mode
            f.write("1") #adding the number 1 to the file
            f.close()#closing the file
            rgug.prepare_output_dir(wkdir)
            self.assertTrue(os.path.exists(gsea_dir)) #making sure that the output directory was created
            self.assertFalse(os.path.exists(test_file))#making sure that this is a new directory and not the old one that had a file in it


    def test_find_DGE_files(self):
        with tempfile.TemporaryDirectory(prefix=temp_wkdir_prefix) as wkdir:
            logger.debug("\n \n \n test_find_DGE_files wkdir:  {}\n \n ".format(wkdir))
                
            #saving the test versions of source_dir and test_id to variables and also creating a test id that won't be tested
            source_dir = os.path.join(wkdir,"source_test")
            test_id ="H202SC20040591"
            notthistest_id = "rnauasf"
            dge_data_test = os.path.join(source_dir, "dge_data")

            #creating directories
            os.mkdir(source_dir)
            os.mkdir(dge_data_test)

            #creating files for the method to find and put into a list

            expectedbasename1 = random_of_input_file((test_id + "_FHT3794_921_QDx1_24h_Vehicle_921_QDx1_24h_DGE_r30500x10.txt"),dge_data_test)
            expectedbasename2 = random_of_input_file((test_id + "_FHT3794_921_QDx6_24h_Vehicle_921_QDx6_24h_DGE_r30500x10.txt"),dge_data_test)
            random_of_input_file((notthistest_id + "_FHT3794_921_QDx6_24h_Vehicle_921_QDx6_24h_DGE_r30500x10.txt"),dge_data_test)
            

            #running the method
            dge_file_list = rgug.find_DGE_files(source_dir, test_id)

            #create a strings to the path 
            #can create variable, os.path.basename of dge_file_list and check that the string is that 

            #assert that the list has what you want in it
            self.assertTrue(len(dge_file_list) == 2)
            expectedbasenameset = {expectedbasename1, expectedbasename2}
            r_basenameset = set([os.path.basename(x) for x in dge_file_list])
            self.assertEqual(expectedbasenameset, r_basenameset)

    def test_build_all_rnk_files(self):
        with tempfile.TemporaryDirectory(prefix=temp_wkdir_prefix) as wkdir:
            logger.debug("\n \n \n test_build_all_rnk_files wkdir:  {}\n \n ".format(wkdir))
            #creating testod and paths of the directories
            test_id ="H202SC20040591"
            source_dir = os.path.join(wkdir,"source_test")
            dge_data_test = os.path.join(source_dir, "dge_data")

            #creating directories
            os.mkdir(source_dir)
            os.mkdir(dge_data_test)

            random_of_input_file((test_id + "_FHT3794_921_QDx1_24h_Vehicle_921_QDx1_24h_DGE_r30500x10.txt"),dge_data_test)
            random_of_input_file((test_id + "_FHT3794_921_QDx6_24h_Vehicle_921_QDx6_24h_DGE_r30500x10.txt"),dge_data_test)

            gsea_dir = os.path.join(source_dir, "gsea")
            os.mkdir(gsea_dir)
            rnk_dir = os.path.join(gsea_dir, "rnk")
            os.mkdir(rnk_dir)
            
            dge_file_list = ['{}\\source_test\\dge_data\\H202SC20040591_FHT3794_921_QDx1_24h_Vehicle_921_QDx1_24h_DGE_r30500x10.txt'.format(wkdir), 
            '{}\\source_test\\dge_data\\H202SC20040591_FHT3794_921_QDx6_24h_Vehicle_921_QDx6_24h_DGE_r30500x10.txt'.format(wkdir)]

            #will fix this to not rely on other methods

            dge_stats_for_rnk_list = ["logFC", "t"]

            input_rnk_files_list = rgug.build_all_rnk_files(dge_file_list, dge_stats_for_rnk_list, rnk_dir)
            
            #could be better, check that the first part of the item on the list is the correct path
            self.assertEqual(len(input_rnk_files_list), 2)
            

            

    def test_build_rnk_file(self):
        with tempfile.TemporaryDirectory(prefix=temp_wkdir_prefix) as wkdir:
            logger.debug("\n \n \n test_build_rnk_file wkdir:  {}\n \n ".format(wkdir))
            #creating testod and paths of the directories
            test_id ="H202SC20040591"
            source_dir = os.path.join(wkdir,"source_test")
            dge_data_test = os.path.join(source_dir, "dge_data")

            #creating directories
            os.mkdir(source_dir)
            os.mkdir(dge_data_test)

            random_of_input_file((test_id + "_FHT3794_921_QDx1_24h_Vehicle_921_QDx1_24h_DGE_r30500x10.txt"),dge_data_test)
            random_of_input_file((test_id + "_FHT3794_921_QDx6_24h_Vehicle_921_QDx6_24h_DGE_r30500x10.txt"),dge_data_test)

            gsea_dir = os.path.join(source_dir, "gsea")
            os.mkdir(gsea_dir)
            rnk_dir = os.path.join(gsea_dir, "rnk")
            os.mkdir(rnk_dir)
            
            dge_file_list = ['{}\\source_test\\dge_data\\H202SC20040591_FHT3794_921_QDx1_24h_Vehicle_921_QDx1_24h_DGE_r30500x10.txt'.format(wkdir), 
            '{}\\source_test\\dge_data\\H202SC20040591_FHT3794_921_QDx6_24h_Vehicle_921_QDx6_24h_DGE_r30500x10.txt'.format(wkdir)]

            dge_file = dge_file_list[0]
            
            dge_df = pandas.read_csv(dge_file, sep="\t")

            base_dge_filename = os.path.splitext(os.path.basename(dge_file))[0]

            base_output_filename = "_".join(base_dge_filename.split("_")[:-2])

            dge_stat_for_rnk = "logFC"

            rnk_df, output_filepath = rgug.build_rnk_file(dge_df, dge_stat_for_rnk, base_output_filename, rnk_dir)

            expected_output_filepath = os.path.join(rnk_dir, "H202SC20040591_FHT3794_921_QDx1_24h_Vehicle_921_QDx1_24h_logFC_r10x2.rnk")

            #could also check the df to make sure it is correct
            self.assertEqual(expected_output_filepath, output_filepath)

    def test_create_gp_server(self):
        #create a mock
        #call the method, It will not actually create a server, just return whatever the method should return
        #assert that the server creation thing was called once

        logger.debug("\n \n \n test_create_gp_server \n \n ")

        #reset the mock calls 
        gp.GPServer.reset_mock()

        returned_gpserver = rgug.create_gp_server("place.com", "usename", "password")

        self.assertEqual(returned_gpserver, gpserver_object)
        self.assertEqual(gp.GPServer.call_count, 1)
        logger.debug("gp.GPServer.call_args {}".format(gp.GPServer.call_args))
        self.assertEqual(gp.GPServer.call_args_list[0][0],("place.com", "usename", "password") )

        


    def test_upload_input_gp_files(self):
        #check that for for every file in input_rnk_file_list, there is a url that has it's basename at the ending
        #something like this
        # for file in input_rnk_file_list
        #    self.assertEquasl("*" + os.path.basename(file), (someting fron url list)
        with tempfile.TemporaryDirectory(prefix=temp_wkdir_prefix) as wkdir:
            gpserver_object.upload_file.reset_mock()


            logger.debug("\n \n \n test_upload_input_gp_files wkdir:  {}\n \n ".format(wkdir))

            test_file_path = os.path.join(wkdir, "_FHT3794_921_QDx1_24h_Vehicle_921_QDx1_24h_DGE_r30500x10.txt")
            another_test_file_path = os.path.join(wkdir, "_FHT3794_921_QDx6_24h_Vehicle_921_QDx6_24h_DGE_r30500x10.txt")

            test_input_files = [test_file_path, another_test_file_path]

            rgug.upload_input_gp_files(test_input_files, gpserver_object)
            
            call_args_list = gpserver_object.upload_file.call_args_list

            self.assertEqual(call_args_list[0][0], (os.path.basename(test_file_path), test_file_path))
            self.assertEqual(call_args_list[1][0], (os.path.basename(another_test_file_path), another_test_file_path))
            
            

    def test_task_list(self):
        logger.debug("\n \n \n test_task_list\n \n ")

        gp.GPTask.reset_mock()

        rgug.task_list(gpserver_object)

        gp.GPTask.assert_called_once_with(gpserver_object, 100)

    def test_create_params_list(self):
        logger.debug("\n \n \n test_create_params_list\n \n ")

        gsea_preranked_module.param_load.reset_mock()
        gsea_preranked_module.get_parameters.reset_mock()


        rgug.create_params_list(gsea_preranked_module)

        gsea_preranked_module.param_load.assert_called_once

        gsea_preranked_module.get_parameters.assert_called_once


    def test_print_param_info(self):
        logger.debug("\n \n \n test_print_param_info \n \n ")

        params_list = create_params_list_mock()
        
        rgug.print_param_info(params_list)

        params_list[0].get_name.assert_called_once
        params_list[0].get_type.assert_called_once
        params_list[0].get_description.assert_called_once
        params_list[0].get_default_value.assert_called_once
        params_list[0].is_optional.assert_called_once


    def test_print_valid_param_choices(self):
        logger.debug("\n \n \n test_print_valid_param_choices\n \n ")

        params_list = create_params_list_mock()

        rgug.print_valid_param_choices(params_list)

        params_list[0].get_name.assert_called_once
        params_list[0].get_choice_selected_value.assert_called_once


    


    def test_create_reference_geneset_urls(self):
        logger.debug("\n \n \n test_create_reference_geneset_urls\n \n ")

        reference_genesets = [
        ("all", {"c1.all.v7.1.symbols.gmt [Positional]", "c2.all.v7.1.symbols.gmt [Curated]", "c3.all.v7.1.symbols.gmt [Motif]",
        "c5.all.v7.1.symbols.gmt [Gene Ontology]", "c6.all.v7.1.symbols.gmt [Oncogenic Signatures]",
        "c7.all.v7.1.symbols.gmt [Immunologic signatures]", "h.all.v7.1.symbols.gmt [Hallmarks]"}),
        ("just_hallmarks", {"h.all.v7.1.symbols.gmt [Hallmarks]"})
        ]

        reference_geneset_urls  = rgug.create_reference_geneset_urls(create_params_list_mock(), reference_genesets)

        logger.debug("reference_geneset_urls\n {}".format(reference_geneset_urls))

        self.assertEqual(len(reference_geneset_urls), 2)


    def test_create_all_job_spec_list(self):
        logger.debug("\n \n \n test_create_all_job_spec_list\n \n ")

        reference_geneset_urls = [('all', ['ftp://gpftp.broadinstitute.org/module_support_files/msigdb/gmt/c1.all.v7.1.symbols.gmt', 
        'ftp://gpftp.broadinstitute.org/module_support_files/msigdb/gmt/c2.all.v7.1.symbols.gmt', 
        'ftp://gpftp.broadinstitute.org/module_support_files/msigdb/gmt/c3.all.v7.1.symbols.gmt', 
        'ftp://gpftp.broadinstitute.org/module_support_files/msigdb/gmt/c5.all.v7.1.symbols.gmt', 
        'ftp://gpftp.broadinstitute.org/module_support_files/msigdb/gmt/c6.all.v7.1.symbols.gmt', 
        'ftp://gpftp.broadinstitute.org/module_support_files/msigdb/gmt/c7.all.v7.1.symbols.gmt', 
        'ftp://gpftp.broadinstitute.org/module_support_files/msigdb/gmt/h.all.v7.1.symbols.gmt']), 
        ('just_hallmarks', ['ftp://gpftp.broadinstitute.org/module_support_files/msigdb/gmt/h.all.v7.1.symbols.gmt'])]

        num_permutations = 1000

        job_memory = "4 Gb"

        input_gp_files_list = [uploaded_gp_file, uploaded_gp_file]

        all_job_spec_list = rgug.create_all_job_spec_list(num_permutations, job_memory, input_gp_files_list, reference_geneset_urls, gsea_preranked_module)

        self.assertEqual(len(all_job_spec_list), 4)


         
    def test_print_all_job_spec_list(self):
        logger.debug("\n \n \ntest_print_all_job_spec_list\n \n ")

        job_spec.params.reset_mock()

        all_job_spec_list =  [('all',job_spec), 
        ('just_hallmarks', job_spec), 
        ('all', job_spec), 
        ('just_hallmarks', job_spec)]

        rgug.print_all_job_spec_list(all_job_spec_list)

        job_spec.params.assert_called_once

    
    def test_create_job_list(self):
        logger.debug("\n \n \n test_create_job_list  \n \n ")

        all_job_spec_list =  [('all',job_spec), 
        ('just_hallmarks', job_spec), 
        ('all', job_spec), 
        ('just_hallmarks', job_spec)]

        job_list = rgug.create_job_list(all_job_spec_list, gpserver_object)
        logger.debug(job_list)

    
    def test_create_zip_dir(self):
        with tempfile.TemporaryDirectory(prefix=temp_wkdir_prefix) as wkdir:
            logger.debug("\n \n \n test_create_zip_dir wkdir:  {}\n \n ".format(wkdir))

            source_dir = os.path.join(wkdir,"source_test")

            #creating directories
            os.mkdir(source_dir)
            
            gsea_dir = os.path.join(source_dir, "gsea")
            os.mkdir(gsea_dir)

            zip_dir = rgug.create_zip_dir(gsea_dir)

    

            self.assertEqual(zip_dir, os.path.join(gsea_dir, "zip_files"))
            self.assertTrue(os.path.exists(zip_dir))



    def test_prepare_zip_files_list(self):
        #does not work atm
        with tempfile.TemporaryDirectory(prefix=temp_wkdir_prefix) as wkdir:
            logger.debug("\n \n \n test_prepare_zip_files_list wkdir:  {}\n \n ".format(wkdir))

            
            
            
            source_dir = os.path.join(wkdir,"source_test")

            #creating directories
            os.mkdir(source_dir)
            
            gsea_dir = os.path.join(source_dir, "gsea")
            os.mkdir(gsea_dir)

            zip_dir = os.path.join(gsea_dir, "zip_files")
            os.mkdir(zip_dir)

            job_list =  [('all',job), 
            ('just_hallmarks', job), 
            ('all', job), 
            ('just_hallmarks', job)]

            rgug.prepare_zip_files_list(job_list, zip_dir)

    def test_print_no_zip_files(self):
        with tempfile.TemporaryDirectory(prefix=temp_wkdir_prefix) as wkdir:
            logger.debug("\n \n \n test_print_no_zip_files wkdir:  {}\n \n ".format(wkdir))


            no_zip_files = [('all',job)]

            output_file.get_name = mock.Mock("mock of get name", return_value = os.path.join(wkdir, "file.txt"))
            

            rgug.print_no_zip_flies(no_zip_files)



    def test_zipping_zip_files(self):
        with tempfile.TemporaryDirectory(prefix=temp_wkdir_prefix) as wkdir:
            logger.debug("\n \n \n test_zipping_zip_files wkdir:  {}\n \n ".format(wkdir))

            my_zipfile = mock.Mock("mock of my zipfile")
            my_zipfile.extractall = mock.Mock("mock of extract all")
            zipfile.ZipFile = mock.Mock("mock of zip file", return_value = my_zipfile)

            source_dir = os.path.join(wkdir,"source_test")

            #creating directories
            os.mkdir(source_dir)
            
            gsea_dir = os.path.join(source_dir, "gsea")
            os.mkdir(gsea_dir)

            zip_dir = os.path.join(gsea_dir, "zip_files")
            os.mkdir(zip_dir)

            output_file.get_name = mock.Mock("mock of get name", return_value = os.path.join(wkdir, "file.zip"))


            t = [x for x in job.get_output_files() if x.get_name().endswith(".zip")]
            zip_output_file = t[0]
            dl_filename = os.path.splitext(zip_output_file.get_name())[0] + "_" + "all" + ".zip"
            dl_filepath = os.path.join(zip_dir, dl_filename)

            pathlib.Path(os.path.join(wkdir, "file_all.zip")).touch()
            #should make a zip file here, instead of just a regular file 


            zip_files_list = [dl_filepath]


            rgug.zipping_zip_files(zip_files_list, gsea_dir)

            self.assertEqual(len(zip_files_list), len(my_zipfile.extractall.call_args_list), len(zipfile.ZipFile.call_args_list))



    def test_main(self):
        with tempfile.TemporaryDirectory(prefix=temp_wkdir_prefix) as wkdir:
            logger.debug("\n \n \n test_main wkdir:  {}\n \n ".format(wkdir))

            my_zipfile = mock.Mock("mock of my zipfile")
            my_zipfile.extractall = mock.Mock("mock of extract all")
            zipfile.ZipFile = mock.Mock("mock of zip file", return_value = my_zipfile)

            source_dir = os.path.join(wkdir,"source_test")
            test_id = "12498123123"
            dge_stats_for_rnk_list = ["logFC", "t"]
            gpusername ="username"
            gppassword = "password"
            gpserver = "server"
            dge_data_test = os.path.join(source_dir, "dge_data")

            os.mkdir(source_dir)
            os.mkdir(dge_data_test)


            random_of_input_file((test_id + "_FHT3794_921_QDx1_24h_Vehicle_921_QDx1_24h_DGE_r30500x10.txt"),dge_data_test)
            random_of_input_file((test_id + "_FHT3794_921_QDx6_24h_Vehicle_921_QDx6_24h_DGE_r30500x10.txt"),dge_data_test)

            gp.GPServer.reset_mock()


            args = rgug.build_parser().parse_args(["-s", source_dir, "-e", test_id, "-d", dge_stats_for_rnk_list, "-gps", gpserver, "-gpu", gpusername, "-gpp", gppassword])

            rgug.main(args)

            self.assertEqual(4, len(my_zipfile.extractall.call_args_list), len(zipfile.ZipFile.call_args_list))
            gp.GPServer.assert_called_once








        
        




            

            



if __name__ == "__main__":
    setup_logger.setup(verbose=True)

    unittest.main()
