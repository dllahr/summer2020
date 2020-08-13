import unittest
import logging
import summer2020py.setup_logger as setup_logger
import summer2020py.run_gsea_using_genepattern_api.run_gsea_using_genepattern as rgug
import os
import tempfile
import pandas
import mock
from unittest.mock import MagicMock
import shutil
import pathlib


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
    
def return_file_basename(file_name):
    return os.path.basename(file_name)



class TestRunGseaUsingGenepattern(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        global temp_wkdir_prefix 
        temp_wkdir_prefix = "test_run_gsea_using_genepattern"

        logger.debug("setUpClass")
        global gpserver_object 
        gpserver_object = mock.Mock("this mock of the gpserver object")
        
        gp.GPServer = MagicMock("mock of gp.GPServer", return_value = gpserver_object)

        

        


    def test_main(self):
        pass

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
        with tempfile.TemporaryDirectory(prefix=temp_wkdir_prefix) as wkdir:
            logger.debug("\n \n \n test_create_gp_server wkdir:  {}\n \n ".format(wkdir))

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
            logger.debug("\n \n \n test_upload_input_gp_files wkdir:  {}\n \n ".format(wkdir))

            

            test_file_path = os.path.join(wkdir, "_FHT3794_921_QDx1_24h_Vehicle_921_QDx1_24h_DGE_r30500x10.txt")
            another_test_file_path = os.path.join(wkdir, "_FHT3794_921_QDx1_24h_Vehicle_921_QDx1_24h_DGE_r30500x10_another.txt")

            test_input_files = [test_file_path, another_test_file_path]

            rgug.upload_input_gp_files(test_input_files, gpserver_object)

            logger.debug(logger.debug("gp.GPServer.call_args {}".format(gp.GPServer.call_args)))

    def test_task_list(self):
        # check that gsea_preranked_module is as it should be / has expected things in it
        pass

    def test_create_params_list(self):
        #should be simple as it's three lines of code as test that the mock is called once and that's that
        pass
            

            



if __name__ == "__main__":
    setup_logger.setup(verbose=True)

    unittest.main()
