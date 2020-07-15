import unittest
import logging
import summer2020py.setup_logger as setup_logger
import summer2020py.genebody_coverage_prep.genebody_coverage_prep as gcp
import os
import shutil

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


class TestGenebodyCoveragePrep(unittest.TestCase):
    def setup(self):
        pass
    
    
    def test_main(self):
        #gcp.main(None)
        pass
    def test_prepare_output_dir(self):
        test_directory = "testing"
        shutil.rmtree(test_directory)
        self.assertFalse(os.path.exists(test_directory))
        gcp.prepare_output_dir(test_directory)
        self.assertTrue(os.path.exists(test_directory))  #making sure that the output directory was created
        test_file = os.path.join(test_directory, "test_file") #adding a file to that directory 
        f = open(test_file,"w")#opening the file in write mode
        f.write("1") #adding the number 1 to the file
        f.close()#closing the file
        gcp.prepare_output_dir(test_directory)
        self.assertTrue(os.path.exists(test_directory)) #making sure that the output directory was created
        self.assertFalse(os.path.exists(test_file))#making sure that this is a new directory and not the old one that had a file in it
        shutil.rmtree(test_directory)#delete the test directory
    def test_make_sample_dir(self):
        test_directory = "testing"
        test_sample = "sample"
        gcp.prepare_output_dir(test_directory)
        new_dir = gcp.make_sample_dir(test_sample, test_directory)#call the make_sample_dir and save that directoy to new_dir
        self.assertTrue(os.path.exists(new_dir)) #see that the new directory has been created
        shutil.rmtree(new_dir) #delete the new directory 
        shutil.rmtree(test_directory)#delete the test directory
    def test_find_sample_input_files(self):
        pass
    def test_create_sample_symlink(self):
        pass




if __name__ == "__main__":
    setup_logger.setup(verbose=True)

    unittest.main()
