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
        #     for i in range(2,len(data)-2):
        #         data[i] = str(random.uniform(-10.0, 10.0)) + "\t"
        #     with open(outputpath, 'a') as f_output:
        #         f_output.write(''.join(data))

        return name
                

    


class TestGeneralPythonScriptTemplate(unittest.TestCase):
    def test_main(self):
        with tempfile.TemporaryDirectory(prefix=temp_wkdir_prefix) as wkdir:
            logger.debug("\n \n \n test_main:  {}\n \n ".format(wkdir))
            test_id = "H202SC20040591"
            base_path = wkdir
            relative_path = "heatmaps"
            server = "http://fht.samba.data/fht_morpheus.html?gctData="
            source_dir = os.path.join(wkdir,"source_test")
            dgestatsforheatmaps = ["logFC", "t"]
            dge_data_test = os.path.join(source_dir, "dge_data")

            #creating directories
            os.mkdir(source_dir)
            os.mkdir(dge_data_test)  

            #making directories so that base_data_path won't throw an error when called
            os.mkdir(os.path.join(wkdir, test_id))
            os.mkdir(os.path.join(wkdir, test_id, relative_path))     
            
            #adding some samples
            random_of_input_file((test_id + "_FHT3794_921_QDx1_24h_Vehicle_921_QDx1_24h_DGE_r30500x10.txt"),dge_data_test)
            random_of_input_file((test_id + "_FHT3794_921_QDx6_24h_Vehicle_921_QDx6_24h_DGE_r30500x10.txt"),dge_data_test)
        
            #simulate adding the commands on the command line using parser
            args = ph.build_parser().parse_args(["-s", source_dir, "-e", test_id, "-d", dgestatsforheatmaps, "-b", 
            base_path, "-r", relative_path, "-se", server])
        

            ph.main(args)

            #whatever way I tested write_to_html will go here modifed to work here



    def test_prepare_output_dir(self):
        with tempfile.TemporaryDirectory(prefix=temp_wkdir_prefix) as wkdir:
            logger.debug("\n \n \n test_prepare_output_dir wkdir:  {}\n \n ".format(wkdir))

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
            logger.debug("\n \n \n test_find_DGE_files:  {}\n \n ".format(wkdir))
            
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
            logger.debug("\n \n \n test_read_DGE_files:  {}\n \n ".format(wkdir))
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
            
            i = 0
            for dge_df, dge_file in dge_df_list:
                self.assertTrue(dge_df.equals(pandas.read_csv(dge_file_list[i], sep="\t", index_col=0))) 
                i += 1
                    

    def test_prepare_GCToo_objects(self):
        #test can be improved, right now it only test when there is one thing in dge_file_list, which while it shows
        #that the methods works the are ways that this test could pass but the code isn't working correctly 
        with tempfile.TemporaryDirectory(prefix=temp_wkdir_prefix) as wkdir:
            logger.debug("\n \n \n test_read_DGE_files:  {}\n \n ".format(wkdir))
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
            dge_stats_for_heatmaps = ["logFC", "t"]

            heatmap_gct_list = ph.prepare_GCToo_objects(dge_stats_for_heatmaps, dge_df_list)

            self.assertEqual(len(heatmap_gct_list), 2)

            #can't think of a way to test this without having the code from the method

    def test_write_GCToo_objects_to_files(self):
        with tempfile.TemporaryDirectory(prefix=temp_wkdir_prefix) as wkdir:
            logger.debug("\n \n \n test_write_GCToo_objects_to_files:  {}\n \n ".format(wkdir))
            
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
            dge_stats_for_heatmaps = ["logFC", "t"]
            dge_df_list = ph.read_DGE_files(dge_file_list)

            heatmap_gct_list = ph.prepare_GCToo_objects(dge_stats_for_heatmaps, dge_df_list)
            
            output_template = test_id + "_heatmap_{dge_stat}_r{rows}x{cols}.gct"
            heatmap_dir = source_dir

            ph.write_GCToo_objects_to_files(heatmap_gct_list, output_template, heatmap_dir)

            #can't think of a way to test this without having the code from the method


    def test_prepare_links(self):
        
        with tempfile.TemporaryDirectory(prefix=temp_wkdir_prefix) as wkdir:
            logger.debug("\n \n \n test_prepare_links:  {}\n \n ".format(wkdir))
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
            dge_stats_for_heatmaps = ["logFC", "t"]
            dge_df_list = ph.read_DGE_files(dge_file_list)

            heatmap_gct_list = ph.prepare_GCToo_objects(dge_stats_for_heatmaps, dge_df_list)
            
            heatmap_dir = source_dir

            #should not be this, will fix later
            base_data_path = wkdir

            output_template = test_id + "_heatmap_{dge_stat}_r{rows}x{cols}.gct"

            url_template = "http://fht.samba.data/fht_morpheus.html?gctData={data_path}"

            ph.write_GCToo_objects_to_files(heatmap_gct_list, output_template, heatmap_dir)

            url_list = ph.prepare_links(heatmap_gct_list, url_template, base_data_path)

            i = 0
            for dge_stat, heatmap_g in heatmap_gct_list:
                data_path = os.path.join(base_data_path, heatmap_g.src)
                cur_url = url_template.format(data_path=data_path)
                self.assertTrue(url_list[i] == (dge_stat, cur_url))
                i += 1


            
    

    def test_write_to_html(self):
        with tempfile.TemporaryDirectory(prefix=temp_wkdir_prefix) as wkdir:
            logger.debug("\n \n \n test_write_to_html:  {}\n \n ".format(wkdir))
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
            dge_stats_for_heatmaps = ["logFC", "t"]
            dge_df_list = ph.read_DGE_files(dge_file_list)

            heatmap_gct_list = ph.prepare_GCToo_objects(dge_stats_for_heatmaps, dge_df_list)
            
            heatmap_dir = source_dir

            base_data_path = wkdir

            output_template = test_id + "_heatmap_{dge_stat}_r{rows}x{cols}.gct"

            url_template = "http://fht.samba.data/fht_morpheus.html?gctData={data_path}"

            ph.write_GCToo_objects_to_files(heatmap_gct_list, output_template, heatmap_dir)

            url_list = ph.prepare_links(heatmap_gct_list, url_template, base_data_path)

            output_html_link_file = "{exp_id}_interactive_heatmap_links.html".format(exp_id= test_id)
            
            ph.write_to_html(source_dir, output_html_link_file, url_list, test_id)

            #can't think of a way to test this without having the code from the method




            
            
                  
                    
            
        


if __name__ == "__main__":
    setup_logger.setup(verbose=True)
    
    unittest.main()
    
