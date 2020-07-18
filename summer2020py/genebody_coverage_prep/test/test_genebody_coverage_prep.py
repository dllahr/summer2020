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


def create_samples_for_testing(start, ending, dirs):
    name = start + ending
    sample = os.path.join(dirs, name)
    f = open(sample,"w")#opening the file in write mode
    f.write("1") #adding the number 1 to the file
    f.close()#closing the file
    not_sample = os.path.join(dirs,ending)
    f = open(not_sample,"w")#opening the file in write mode
    f.write("1") #adding the number 1 to the file
    f.close()#closing the file


class TestGenebodyCoveragePrep(unittest.TestCase):
    def setup(self):
        pass
   
    def test_main_sample(self):
        os.mkdir("main_test_input")#make a directory to hold the inputs files
        create_samples_for_testing("sample","123","main_test_input")#read the method name
        create_samples_for_testing("sample","456","main_test_input")#read the method name
        create_samples_for_testing("sample","789","main_test_input")#read the method name
        create_samples_for_testing("s1ample_","thing","main_test_input")#read the method name
        args = gcp.build_parser().parse_args(["-o", "main_test_output", "-i", "main_test_input", "-s", "sample"])#simulate adding the commands on the command line using parser
        gcp.main(args)
        self.assertTrue(os.path.islink((os.path.join("main_test_output", "sample", "sample123"))))#see that the symlink is where it should be and that it exists
        self.assertTrue(os.path.islink((os.path.join("main_test_output", "sample", "sample456"))))#see that the symlink is where it should be and that it exists
        self.assertTrue(os.path.islink((os.path.join("main_test_output", "sample", "sample789"))))#see that the symlink is where it should be and that it exists
        shutil.rmtree("main_test_input")#delete the directory as if it's sill there and you run the code again it will fail 
        shutil.rmtree("main_test_output")#delete this one so there is no trace the test ran 

    def test_main_sampleFile(self):
        f = open("sample_main_file_test","w")#opening the file in write mode
        f.write("sample\ns1ample \nanothersample") #adding the start of the samples 
        f.close()#closing the file
        os.mkdir("main_test_input")#make a directory to hold the inputs files
        create_samples_for_testing("sample","123","main_test_input")#read the method name
        create_samples_for_testing("sample","456","main_test_input")#read the method name
        create_samples_for_testing("s1ample_","thing","main_test_input")#read the method name
        create_samples_for_testing("s1ample_","thingy","main_test_input")#read the method name
        create_samples_for_testing("anothersample","AAAAAA","main_test_input")#read the method name
        create_samples_for_testing("anothersample","BBBBBB","main_test_input")#read the method name
        args = gcp.build_parser().parse_args(["-o", "main_test_output", "-i", "main_test_input", "-sf", "sample_main_file_test"])#simulate adding the commands on the command line using parser
        gcp.main(args)
        self.assertTrue(os.path.islink((os.path.join("main_test_output", "sample", "sample123"))))#see that the symlink is where it should be and that it exists
        self.assertTrue(os.path.islink((os.path.join("main_test_output", "sample", "sample456"))))#see that the symlink is where it should be and that it exists
        self.assertTrue(os.path.islink((os.path.join("main_test_output", "s1ample", "s1ample_thing"))))#see that the symlink is where it should be and that it exists
        self.assertTrue(os.path.islink((os.path.join("main_test_output", "s1ample", "s1ample_thingy"))))#see that the symlink is where it should be and that it exists
        self.assertTrue(os.path.islink((os.path.join("main_test_output", "anothersample", "anothersampleAAAAAA"))))#see that the symlink is where it should be and that it exists
        self.assertTrue(os.path.islink((os.path.join("main_test_output", "anothersample", "anothersampleAAAAAA"))))#see that the symlink is where it should be and that it exists
        shutil.rmtree("main_test_input")#delete the directory as if it's sill there and you run the code again it will fail 
        shutil.rmtree("main_test_output")#delete this one so there is no trace the test ran 
        os.remove("sample_main_file_test")

    def test_load_sample(self):
        f = open("load_test","w")#opening the file in write mode
        f.write("1\n2 \n3 \n4 \n5") #adding numbers to the file
        f.close()#closing the file
        sample_list = gcp.load_sample("load_test")
        self.assertTrue(sample_list == ['1','2','3','4','5'])#this is what the output should be, so it should be equal to the result of the method call
        os.remove("load_test")

    def test_create_samples_for_testing(self):
        testend = "july_first"
        test_dir = "creationtesting"
        os.mkdir(test_dir)
        create_samples_for_testing("sample_", testend, test_dir)
        #confirming that the files in the directory are sample_june_first and june_first
        self.assertTrue(os.path.isfile(os.path.join(test_dir, testend)))
        self.assertTrue(os.path.isfile(os.path.join(test_dir, "sample_" + testend)))
        shutil.rmtree(test_dir)

    def test_prepare_output_dir(self):
        test_directory = "testing"
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
        input_directory = "input_test"
        test_sample ="sample"
        os.mkdir(input_directory)
        create_samples_for_testing("sample", "1",input_directory)
        create_samples_for_testing("sample","2",input_directory)
        create_samples_for_testing("sample","3",input_directory)
        file_list = gcp.find_sample_input_files(test_sample, input_directory)
        self.assertTrue(file_list)
        shutil.rmtree(input_directory)

    def test_create_sample_symlink(self):
        test_directory = "symtesting"
        test_sample = "symsample"
        input_directory = "inputs"
        gcp.prepare_output_dir(test_directory)#create a test directory to hold everything that will be created
        new_dir = gcp.make_sample_dir(test_sample, test_directory)#create a directory to hold the output
        os.mkdir(input_directory) #creating a directory to hold the inputs
        create_samples_for_testing("sample", "1",input_directory) #creating two files in input_directory sample1 and 1
        create_samples_for_testing("sample", "2",input_directory)#creating two files in input_directory sample2 and 2
        create_samples_for_testing("anothersample", "july_16",input_directory)#creating two files in input_directory anothersamplejuly_16 and july_16
        create_samples_for_testing("anothersample", "july_17",input_directory)#creating two files in input_directory anothersamplejuly_1 and july_17
        file_list = gcp.find_sample_input_files("sample", input_directory)#get the files that start with sample and put them in file list
        for input_file in file_list:
            gcp.create_sample_symlink(input_file, new_dir)#create a symlink pointing to the file in the new_dir
        anotherfile_list = gcp.find_sample_input_files("anothersample", input_directory)#get the files that start with anothersample and put them in file list
        for input_file in anotherfile_list:
            gcp.create_sample_symlink(input_file, new_dir)#create a symlink pointing to the file in the new_dir
        #testing to see if the sym links are where they should be
        self.assertTrue(os.path.islink((os.path.join(test_directory, test_sample, "sample1"))))
        self.assertTrue(os.path.islink((os.path.join(test_directory, test_sample, "sample2"))))
        self.assertTrue(os.path.islink((os.path.join(test_directory, test_sample, "anothersamplejuly_16"))))
        self.assertTrue(os.path.islink((os.path.join(test_directory, test_sample, "anothersamplejuly_17"))))
        #deleting the directory so that there are no files left over from this running 
        shutil.rmtree(input_directory)
        shutil.rmtree(test_directory)


if __name__ == "__main__":
    setup_logger.setup(verbose=True)

    unittest.main()
