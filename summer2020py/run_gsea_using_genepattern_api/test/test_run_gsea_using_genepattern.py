import unittest
import logging
import summer2020py.setup_logger as setup_logger
import summer2020py.run_gsea_using_genepattern_api.run_gsea_using_genepattern as rgug
import os
import tempfile
import pandas


logger = logging.getLogger(setup_logger.LOGGER_NAME)

temp_wkdir_prefix = "test_run_gsea_using_genepattern"

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
    #do not believe this works as it should 
    path = os.path.join("assets", "prep_heatmap_example_input_DGE_r10x10.txt")
    outputpath = os.path.join(dirs, name)
    
    with open(path) as f_input:
        with open(outputpath, 'a') as f_output:
            for line in f_input:
                f_output.write(line)
        return name




class TestRunGseaUsingGenepattern(unittest.TestCase):
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

            gsea_dir, rnk_dir = rgug.prepare_output_dir(source_dir)
            
            dge_file_list = rgug.find_DGE_files(source_dir, test_id)

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

            gsea_dir, rnk_dir = rgug.prepare_output_dir(source_dir)
            
            dge_file_list = rgug.find_DGE_files(source_dir, test_id)

            dge_file = dge_file_list[0]
            
            dge_df = pandas.read_csv(dge_file, sep="\t")

            base_dge_filename = os.path.splitext(os.path.basename(dge_file))[0]

            base_output_filename = "_".join(base_dge_filename.split("_")[:-2])

            dge_stat_for_rnk = "logFC"

            rnk_df, output_filepath = rgug.build_rnk_file(dge_df, dge_stat_for_rnk, base_output_filename, rnk_dir)

            expected_output_filepath = os.path.join(rnk_dir, "H202SC20040591_FHT3794_921_QDx1_24h_Vehicle_921_QDx1_24h_logFC_r10x2.rnk")

            #could also check the df to make sure it is correct
            self.assertEqual(expected_output_filepath, output_filepath)
            

            



if __name__ == "__main__":
    setup_logger.setup(verbose=True)

    unittest.main()
