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
    def test_main(self):
        #gcp.main(None)
        pass
    def test_prepare_output_dir(self):
        test_directory = "testing"
        self.assertFalse(os.path.exists(test_directory))
        gcp.prepare_output_dir(test_directory)
        self.assertTrue(os.path.exists(test_directory))
        test_file = os.path.join(test_directory, "test_file")
        f = open(test_file,"w")
        f.write("1")
        f.close()
        gcp.prepare_output_dir(test_directory)
        self.assertTrue(os.path.exists(test_directory))
        self.assertFalse(os.path.exists(test_file))
        shutil.rmtree(test_directory)
    def test_make_sample_dir(self):
        pass
    def test_find_sample_input_files(self):
        pass
    def test_create_sample_symlink(self):
        pass




if __name__ == "__main__":
    setup_logger.setup(verbose=True)

    unittest.main()
