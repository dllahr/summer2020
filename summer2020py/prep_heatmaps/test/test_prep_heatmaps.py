import unittest
import logging
import summer2020py.setup_logger as setup_logger
import summer2020py.prep_heatmaps.prep_heatmaps as ph
import tempfile
import os
import shutil
import glob
import pandas
import cmapPy.pandasGEXpress.GCToo as GCToo
import cmapPy.pandasGEXpress.write_gct as write_gct
import random

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

temp_wkdir_prefix = "test_prep_heatmaps"

   
def random_of_input_file(name, dirs):
    #do not believe this works as it should 
    path = os.path.join("assets", "prep_heatmap_example_input_DGE_r10x10.txt")
    outputpath = os.path.join(dirs, name)
    with open(path) as f_input:
        with open(outputpath, 'a') as f_output:
            for line in f_input:
                f_output.write(line)
        
        # first_line = f_input.readline()
        # with open(outputpath, 'w') as f_output:
        #         f_output.write(first_line)
        # for line in f_input:
        #     data = line.split("\t")
        #     for i in range(2,len(data)-1):
        #         data[i] = str(round((random.uniform(-10.0, 10.0)), 5)) + "\t"
        #     with open(outputpath, 'a') as f_output:
        #         f_output.write(' '.join(data))
        return name
                

    


class TestGeneralPythonScriptTemplate(unittest.TestCase):
    def test_main(self):
        pass
    def test_prepare_output_dir(self):
        with tempfile.TemporaryDirectory(prefix=temp_wkdir_prefix) as wkdir:
            logger.debug("test_prepare_output_dir wkdir:  {}".format(wkdir))

            heatmaps = os.path.join(wkdir, "heatmaps")
            # run prepare_output_dir method
            ph.prepare_output_dir(wkdir)

            # test that the output directory were created
            self.assertTrue(os.path.exists(heatmaps))  

            logger.debug("test that if we run the method and the directory exists, it is cleared out")
            test_file = os.path.join(heatmaps, "test_file") #adding a file to that directory 
            f = open(test_file,"w")#opening the file in write mode
            f.write("1") #adding the number 1 to the file
            f.close()#closing the file

            ph.prepare_output_dir(wkdir)
            self.assertTrue(os.path.exists(heatmaps)) #making sure that the output directory was created
            self.assertFalse(os.path.exists(test_file))#making sure that this is a new directory and not the old one that had a file in it
    
    
    def test_find_DGE_files(self):
         with tempfile.TemporaryDirectory(prefix=temp_wkdir_prefix) as wkdir:
            logger.debug("test_find_DGE_files:  {}".format(wkdir))
            
            #saving the test versions of source_dir and test_id to variables and also creating a test id that won't be tested
            source_dir = os.path.join(wkdir,"source_test")
            test_id ="H202SC20040591"
            notthistest_id = "rnauasf"
            dge_data_test = os.path.join(source_dir, "dge_data")

            #creating directories
            os.mkdir(source_dir)
            os.mkdir(dge_data_test)

            #creating files for the method to find and put into a list
            random_of_input_file((test_id + "_FHT3794_921_QDx1_24h_Vehicle_921_QDx1_24h_DGE_r30500x10.txt"),dge_data_test)
            random_of_input_file((test_id + "_FHT3794_921_QDx6_24h_Vehicle_921_QDx6_24h_DGE_r30500x10.txt"),dge_data_test)
            random_of_input_file((notthistest_id + "_FHT3794_921_QDx6_24h_Vehicle_921_QDx6_24h_DGE_r30500x10.txt"),dge_data_test)
            
            #running the method
            dge_file_list = ph.find_DGE_files(source_dir, test_id)

            #assert that the list has what you want in it
            self.assertTrue(len(dge_file_list) == 2)
    
    def test_read_DGE_files(self):
        #test can be improved, right now it only test when there is one thing in dge_file_list, which while it shows
        #that the methods works the are ways that this test could pass but the code isn't working correctly 
        with tempfile.TemporaryDirectory(prefix=temp_wkdir_prefix) as wkdir:
            logger.debug("test_read_DGE_files:  {}".format(wkdir))
            #creating testod and paths of the directories
            test_id ="H202SC20040591"
            source_dir = os.path.join(wkdir,"source_test")
            dge_data_test = os.path.join(source_dir, "dge_data")

            #creating directories
            os.mkdir(source_dir)
            os.mkdir(dge_data_test)

            random_of_input_file((test_id + "_FHT3794_921_QDx1_24h_Vehicle_921_QDx1_24h_DGE_r30500x10.txt"),dge_data_test)
            random_of_input_file((test_id + "_FHT3794_921_QDx6_24h_Vehicle_921_QDx6_24h_DGE_r30500x10.txt"),dge_data_test)

            dge_file_list = ph.find_DGE_files(source_dir, test_id)

            dge_df_list = ph.read_DGE_files(dge_file_list)
            
            for dge_df, dge_file in dge_df_list:
                    #test the test
                    self.assertTrue(len(dge_df_list)==2)
                    

    def test_prepare_GCToo_objects(self):
        #test can be improved, right now it only test when there is one thing in dge_file_list, which while it shows
        #that the methods works the are ways that this test could pass but the code isn't working correctly 
        with tempfile.TemporaryDirectory(prefix=temp_wkdir_prefix) as wkdir:
            logger.debug("test_read_DGE_files:  {}".format(wkdir))
            #creating file and a list to pass into read DGE_files
            test_id ="H202SC20040591"
            source_dir = os.path.join(wkdir,"source_test")
            dge_data_test = os.path.join(source_dir, "dge_data")

            #creating directories
            os.mkdir(source_dir)
            os.mkdir(dge_data_test)

            random_of_input_file((test_id + "_FHT3794_921_QDx1_24h_Vehicle_921_QDx1_24h_DGE_r30500x10.txt"),dge_data_test)
            random_of_input_file((test_id + "_FHT3794_921_QDx6_24h_Vehicle_921_QDx6_24h_DGE_r30500x10.txt"),dge_data_test)

            dge_file_list = ph.find_DGE_files(source_dir, test_id)

            dge_df_list = ph.read_DGE_files(dge_file_list)
            dge_stats_for_heatmaps = [["logFC", "t"]]
            dge_df_list = ph.read_DGE_files(dge_file_list)

            heatmap_gct_list = ph.prepare_GCToo_objects(dge_stats_for_heatmaps, dge_df_list)

    def write_GCToo_objects_to_files(self):
        with tempfile.TemporaryDirectory(prefix=temp_wkdir_prefix) as wkdir:
            logger.debug("test_write_GCToo_objects_to_files:  {}".format(wkdir))
            
            #creating file and a list to pass into read DGE_files
            test_id ="H202SC20040591"
            source_dir = os.path.join(wkdir,"source_test")
            dge_data_test = os.path.join(source_dir, "dge_data")

            #creating directories
            os.mkdir(source_dir)
            os.mkdir(dge_data_test)

            random_of_input_file((test_id + "_FHT3794_921_QDx1_24h_Vehicle_921_QDx1_24h_DGE_r30500x10.txt"),dge_data_test)
            random_of_input_file((test_id + "_FHT3794_921_QDx6_24h_Vehicle_921_QDx6_24h_DGE_r30500x10.txt"),dge_data_test)

            dge_file_list = ph.find_DGE_files(source_dir, test_id)

            dge_df_list = ph.read_DGE_files(dge_file_list)
            dge_stats_for_heatmaps = [["logFC", "t"]]
            dge_df_list = ph.read_DGE_files(dge_file_list)

            heatmap_gct_list = ph.prepare_GCToo_objects(dge_stats_for_heatmaps, dge_df_list)
            
            output_template = test_id + "_heatmap_{dge_stat}_r{rows}x{cols}.gct"
            heatmap_dir = source_dir

            ph.write_GCToo_objects_to_files(heatmap_gct_list, output_template, heatmap_dir)

            #run a test to see if it worked 


    def prepare_links(self):
        
        with tempfile.TemporaryDirectory(prefix=temp_wkdir_prefix) as wkdir:
            logger.debug("test_prepare_links:  {}".format(wkdir))
            #creating file and a list to pass into read DGE_files
            test_id ="H202SC20040591"
            source_dir = os.path.join(wkdir,"source_test")
            dge_data_test = os.path.join(source_dir, "dge_data")

            #creating directories
            os.mkdir(source_dir)
            os.mkdir(dge_data_test)

            random_of_input_file((test_id + "_FHT3794_921_QDx1_24h_Vehicle_921_QDx1_24h_DGE_r30500x10.txt"),dge_data_test)
            random_of_input_file((test_id + "_FHT3794_921_QDx6_24h_Vehicle_921_QDx6_24h_DGE_r30500x10.txt"),dge_data_test)

            dge_file_list = ph.find_DGE_files(source_dir, test_id)

            dge_df_list = ph.read_DGE_files(dge_file_list)
            dge_stats_for_heatmaps = [["logFC", "t"]]
            dge_df_list = ph.read_DGE_files(dge_file_list)

            heatmap_gct_list = ph.prepare_GCToo_objects(dge_stats_for_heatmaps, dge_df_list)
            
            base_data_path = ""

            url_template = "http://fht.samba.data/fht_morpheus.html?gctData={data_path}"

            ph.prepare_links(heatmap_gct_list, url_template, base_data_path)

            #run a test to see that it worked


            
            
                  
                    
            
        


if __name__ == "__main__":
    setup_logger.setup(verbose=True)
    
    unittest.main()
    
