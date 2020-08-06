import unittest
import logging
import summer2020py.setup_logger as setup_logger
import summer2020py.run_gsea_using_genepattern_api.run_gsea_using_genepattern as rgug
import os
import tempfile


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


class TestRunGseaUsingGenepattern(unittest.TestCase):
    def test_main(self):
        pass

    def test_prepare_output_directory(self):
        with tempfile.TemporaryDirectory(prefix=temp_wkdir_prefix) as wkdir:
            logger.debug("test_prepare_output_dir wkdir:  {}".format(wkdir))

            test_directory = os.path.join(wkdir, "output")
            logger.debug("test_directory:  {}".format(test_directory))
            self.assertFalse(os.path.exists(test_directory))

            # run prepare_output_dir method
            rgug.prepare_output_dir(test_directory)

            # test that the output directories were created
            self.assertTrue(os.path.exists(os.path.join(test_directory, "gsea")))
            self.assertTrue(os.path.exists(os.path.join(test_directory, "gsea", "rnk")))
            
            logger.debug("test that if we run the method and the directory exists, it is cleared out")
            test_file = os.path.join(test_directory, "test_file") #adding a file to that directory 
            f = open(test_file,"w")#opening the file in write mode
            f.write("1") #adding the number 1 to the file
            f.close()#closing the file
            rgug.prepare_output_dir(test_directory)
            self.assertTrue(os.path.exists(test_directory)) #making sure that the output directory was created
            self.assertFalse(os.path.exists(test_file))#making sure that this is a new directory and not the old one that had a file in it


if __name__ == "__main__":
    setup_logger.setup(verbose=True)

    unittest.main()
