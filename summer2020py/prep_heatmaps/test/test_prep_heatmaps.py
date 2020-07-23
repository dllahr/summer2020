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
from random import randint

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
def randoms():
    return random.uniform(-10.0, 10.0)

def create_file_for_testing(name, dirs):
    
    files = os.path.join(dirs, name)

    f = open(files,"w")#opening the file in write mode
    f.write("numbers\tlogFC\tt\n1\t{}\t{}\n2\t{}\t{}".format(randoms(),randoms(),randoms(),randoms())) #adding some stuff to the file
    f.close()#closing the file
    return files
   
def random_of_input_file(name, dirs):
    logger.debug("is this working")
    path = os.path.join("assets", "prep_heatmap_example_input_DGE_r10x10.txt")
    with open(path) as f_input:
        first_line = f_input.readline()
        with open(name, 'w') as f_output:
                f_output.write(first_line)
        for line in f_input:
            data = line.split("\t")
            for i in range(2,10):
                data[i] = str(randint(10, 99))
            with open(name, 'a') as f_output:
                f_output.write(' '.join(data))
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
            test_id ="124rqtga"
            notthistest_id = "rnauasf"
            dge_data_test = os.path.join(source_dir, "dge_data")

            #creating directories
            os.mkdir(source_dir)
            os.mkdir(dge_data_test)

            #creating files for the method to find and put into a list
            create_file_for_testing((test_id + "_one_DGE_rtwo.txt"),dge_data_test)
            create_file_for_testing((test_id + "_three_DGE_rtwo.txt"),dge_data_test)
            create_file_for_testing((notthistest_id + "_one_DGE_rtwo.txt"),dge_data_test)
            
            #running the method
            dge_file_list = ph.find_DGE_files(source_dir, test_id)

            #assert that the list has what you want in it
            self.assertTrue(len(dge_file_list) == 2)
    
    def test_read_DGE_files(self):
        #test can be improved, right now it only test when there is one thing in dge_file_list, which while it shows
        #that the methods works the are ways that this test could pass but the code isn't working correctly 
        with tempfile.TemporaryDirectory(prefix=temp_wkdir_prefix) as wkdir:
            logger.debug("test_read_DGE_files:  {}".format(wkdir))
            #creating file and a list to pass into read DGE_files
            onetwo = create_file_for_testing("onetwo", wkdir)
            dge_file_list = [onetwo]

            dge_df_list = ph.read_DGE_files(dge_file_list)
            
            for dge_df, dge_file in dge_df_list:
                    #breaking the test to try something out
                    pass 

    def prepare_GCToo_objects(self):
        #test can be improved, right now it only test when there is one thing in dge_file_list, which while it shows
        #that the methods works the are ways that this test could pass but the code isn't working correctly 
        with tempfile.TemporaryDirectory(prefix=temp_wkdir_prefix) as wkdir:
            logger.debug("test_read_DGE_files:  {}".format(wkdir))
            #creating file and a list to pass into read DGE_files
            onetwo = create_file_for_testing("onetwo", wkdir)
            dge_file_list = [onetwo]
            dge_stats_for_heatmaps = [["logFC", "t"]]
            dge_df_list = ph.read_DGE_files(dge_file_list)
            heatmap_gct_list = ph.prepare_GCToo_objects(dge_stats_for_heatmaps, dge_df_list)

    def test_random(self):
            files = random_of_input_file("test", "test")
            with open(files) as f:
                for line in f:
                    logger.debug(line)

            
            
                  
                    
            
        


if __name__ == "__main__":
    setup_logger.setup(verbose=True)
    
    unittest.main()
    
