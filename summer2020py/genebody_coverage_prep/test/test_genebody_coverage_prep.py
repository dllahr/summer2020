import unittest
import logging
import summer2020py.setup_logger as setup_logger
import summer2020py.genebody_coverage_prep.genebody_coverage_prep as gcp
import os
import shutil
import tempfile


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


temp_wkdir_prefix = "test_genebody_coverage_prep"


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
   
    def test_main_sample(self):
        with tempfile.TemporaryDirectory(prefix=temp_wkdir_prefix) as wkdir:
          
            #variable names to be used during this test
            main_test_output = os.path.join(wkdir,"main_test_output")
            main_test_input = os.path.join(wkdir,"main_test_input")
            symlinkplace = "input_gbdy_cov"
            sample = "sample"
            s1ample = "s1ample"
            

            os.mkdir(main_test_input)#make a directory to hold the inputs files

            #create samples to be used during this test
            create_samples_for_testing(sample,"123",main_test_input)
            create_samples_for_testing(sample,"456",main_test_input)
            create_samples_for_testing(sample,"789",main_test_input)#
            create_samples_for_testing(s1ample,"thing",main_test_input)
            
            #simulate adding the commands on the command line using parser
            args = gcp.build_parser().parse_args(["-o", main_test_output, "-i", main_test_input, "-s", sample])
            gcp.main(args)

            #seeing if the symlinks are where they should be
            self.assertTrue(os.path.islink((os.path.join(main_test_output, symlinkplace, sample, "sample123"))))
            self.assertTrue(os.path.islink((os.path.join(main_test_output, symlinkplace ,sample, "sample456"))))
            self.assertTrue(os.path.islink((os.path.join(main_test_output, symlinkplace ,sample, "sample789"))))
        


    def test_main_sampleFile(self):
        with tempfile.TemporaryDirectory(prefix=temp_wkdir_prefix) as wkdir:
            
            #variable names to be used during this test
            main_test_output = os.path.join(wkdir,"main_test_output")
            main_test_input = os.path.join(wkdir,"main_test_input")
            filename = os.path.join(wkdir,"sample_main_file_test")
            symlinkplace = "input_gbdy_cov"
            sample = "sample"
            s1ample = "s1ample"
            anothersample ="anothersample"
            

            f = open(filename,"w")#opening the file in write mode
            f.write("sample\ns1ample \nanothersample") #adding the start of the samples 
            f.close()#closing the file

            os.mkdir(main_test_input)#make a directory to hold the inputs files
            
            #create some samples for the testing
            create_samples_for_testing(sample,"123",main_test_input)
            create_samples_for_testing(sample,"456",main_test_input)
            create_samples_for_testing(s1ample,"thing",main_test_input)
            create_samples_for_testing(s1ample,"thingy",main_test_input)
            create_samples_for_testing(anothersample,"AAAAAA",main_test_input)
            create_samples_for_testing(anothersample,"BBBBBB",main_test_input)
            
            #simulate adding the commands on the command line using parser
            args = gcp.build_parser().parse_args(["-o", main_test_output, "-i", main_test_input, "-sf", filename])
            gcp.main(args)

            #seeing if the symlinks are where they should be 
            self.assertTrue(os.path.islink((os.path.join(main_test_output,  symlinkplace ,sample, "sample123"))))
            self.assertTrue(os.path.islink((os.path.join(main_test_output,  symlinkplace ,sample, "sample456"))))
            self.assertTrue(os.path.islink((os.path.join(main_test_output,  symlinkplace ,s1ample, "s1amplething"))))
            self.assertTrue(os.path.islink((os.path.join(main_test_output,  symlinkplace ,s1ample, "s1amplethingy"))))
            self.assertTrue(os.path.islink((os.path.join(main_test_output,  symlinkplace ,anothersample, "anothersampleAAAAAA"))))
            self.assertTrue(os.path.islink((os.path.join(main_test_output,  symlinkplace ,anothersample, "anothersampleAAAAAA"))))
            

        

    def test_load_sample(self):
        with tempfile.TemporaryDirectory(prefix=temp_wkdir_prefix) as test_dir:
            load_test = os.path.join(test_dir, "load_test")
            
            f = open(load_test,"w")#opening the file in write mode
            f.write("1\n2 \n3 \n4 \n5") #adding numbers to the file
            f.close()#closing the file

            sample_list = gcp.load_sample(load_test)
            self.assertTrue(sample_list == ['1','2','3','4','5'])
            #this is what the output should be, so it should be equal to the result of the method call


    def test_create_samples_for_testing(self):
        with tempfile.TemporaryDirectory(prefix=temp_wkdir_prefix) as test_dir:
            testend = "july_first"
            create_samples_for_testing("sample_", testend, test_dir)
            #confirming that the files in the directory are sample_june_first and june_first

            self.assertTrue(os.path.isfile(os.path.join(test_dir, testend)))
            self.assertTrue(os.path.isfile(os.path.join(test_dir, "sample_" + testend)))


    def test_prepare_output_dir(self):
        with tempfile.TemporaryDirectory(prefix=temp_wkdir_prefix) as wkdir:
            logger.debug("test_prepare_output_dir wkdir:  {}".format(wkdir))

            test_directory = os.path.join(wkdir, "output")
            logger.debug("test_directory:  {}".format(test_directory))
            self.assertFalse(os.path.exists(test_directory))

            # run prepare_output_dir method
            my_symlinks, my_calcs = gcp.prepare_output_dir(test_directory, "my_symlinks", "my_calcs")
            logger.debug("results my_symlinks:  {}".format(my_symlinks))
            logger.debug("my_calcs:  {}".format(my_calcs))

            self.assertEqual(os.path.join(test_directory, "my_symlinks"), my_symlinks)
            self.assertEqual(os.path.join(test_directory, "my_calcs"), my_calcs)

            # test that the output directories were created
            self.assertTrue(os.path.exists(test_directory))  
            self.assertTrue(os.path.exists(my_symlinks))
            self.assertTrue(os.path.exists(my_calcs))

            logger.debug("test that if we run the method and the directory exists, it is cleared out")
            test_file = os.path.join(test_directory, "test_file") #adding a file to that directory 
            f = open(test_file,"w")#opening the file in write mode
            f.write("1") #adding the number 1 to the file
            f.close()#closing the file
            gcp.prepare_output_dir(test_directory, "my_symlinks", "my_calcs")
            self.assertTrue(os.path.exists(test_directory)) #making sure that the output directory was created
            self.assertFalse(os.path.exists(test_file))#making sure that this is a new directory and not the old one that had a file in it
   
    def test_make_sample_dir(self):
        with tempfile.TemporaryDirectory(prefix=temp_wkdir_prefix) as wkdir:
            test_directory = os.path.join(wkdir,"testing")
            test_sample = "sample"

            gcp.prepare_output_dir(test_directory, "my_symlinks", "my_calcs")
            new_dir = gcp.make_sample_dir(test_sample, test_directory)#call the make_sample_dir and save that directoy to new_dir
            
            self.assertTrue(os.path.exists(new_dir)) #see that the new directory has been created
            

    
    def test_find_sample_input_files(self):
        with tempfile.TemporaryDirectory(prefix=temp_wkdir_prefix) as wkdir:
            input_directory = os.path.join(wkdir,"input_test")
            test_sample ="sample"
        
            os.mkdir(input_directory)
            
            create_samples_for_testing("sample", "1",input_directory)
            create_samples_for_testing("sample","2",input_directory)
            create_samples_for_testing("sample","3",input_directory)
            
            file_list = gcp.find_sample_input_files(test_sample, input_directory)
            
            self.assertTrue(file_list)
            

    def test_create_sample_symlink(self):
        with tempfile.TemporaryDirectory(prefix=temp_wkdir_prefix) as wkdir:
            
            #create variable names to be used for the testing
            super_test_directory = os.path.join(wkdir,"symtesting")
            test_sample = "symsample"
            input_directory = os.path.join(wkdir,"inputs")
            sample = "sample"
            anothersample = "anothersample"
            

            test_directory, _ = gcp.prepare_output_dir(super_test_directory, "test_symlinks_dir", "test_calc_dir")
            # create a test directory that holds all the outputs 

            new_dir = gcp.make_sample_dir(test_sample, test_directory)#create a directory to hold the output
            os.mkdir(input_directory) #creating a directory to hold the inputs

            create_samples_for_testing(sample, "1",input_directory) 
            create_samples_for_testing(sample, "2",input_directory)
            create_samples_for_testing(anothersample, "july_16",input_directory)
            create_samples_for_testing(anothersample, "july_17",input_directory)
            #creating sammples in the input_directory

            file_list = gcp.find_sample_input_files(sample, input_directory)#get the files that start with sample and put them in file list
            for input_file in file_list:
                gcp.create_sample_symlink(input_file, new_dir)#create a symlink pointing to the file in the new_dir
            
            anotherfile_list = gcp.find_sample_input_files(anothersample, input_directory)#get the files that start with anothersample and put them in file list
            for input_file in anotherfile_list:
                gcp.create_sample_symlink(input_file, new_dir)#create a symlink pointing to the file in the new_dir

            #testing to see if the sym links are where they should be
            self.assertTrue(os.path.islink((os.path.join(test_directory, test_sample, "sample1"))))
            self.assertTrue(os.path.islink((os.path.join(test_directory, test_sample, "sample2"))))
            self.assertTrue(os.path.islink((os.path.join(test_directory, test_sample, "anothersamplejuly_16"))))
            self.assertTrue(os.path.islink((os.path.join(test_directory, test_sample, "anothersamplejuly_17"))))
            


    def test_prepare_sample_symlinks_dir(self):
        with tempfile.TemporaryDirectory(prefix=temp_wkdir_prefix) as wkdir:
            #variable names that will be used for the testing
            inputs = os.path.join(wkdir,"thiscanbewhateverIwant")
            samplename = "my_samples"
            output_dir = os.path.join(wkdir,"outputs")
            
            #create the directory inputs, and the output directories
            os.mkdir(inputs)
            output_symlinks_dir, output_calc_dir = gcp.prepare_output_dir(output_dir,"sym", "calc")
            logger.debug("prepare output dir saved to {}{}".format(output_symlinks_dir,output_calc_dir))

            #populate the inputs directory with some samples
            create_samples_for_testing(samplename, "1",inputs)
            create_samples_for_testing(samplename,"2",inputs)
            create_samples_for_testing(samplename,"3",inputs)


            gcp.prepare_sample_symlinks_dir(samplename, inputs, output_symlinks_dir)
            #call the method that is going to be tested 

            #check to see that the symlinks are thre
            self.assertTrue(os.path.islink((os.path.join(output_symlinks_dir, samplename, "my_samples1"))))
            self.assertTrue(os.path.islink((os.path.join(output_symlinks_dir, samplename, "my_samples2"))))
            self.assertTrue(os.path.islink((os.path.join(output_symlinks_dir, samplename, "my_samples3"))))

        

    def test_prepare_sample_output_calc_dir(self):
        with tempfile.TemporaryDirectory(prefix=temp_wkdir_prefix) as wkdir:
            logger.debug("test_prepare_sample_output_calc_dir wkdir:  {}".format(wkdir))

            r = gcp.prepare_sample_output_calc_dir("my_sample13", wkdir)
            logger.debug("r:  {}".format(r))
            self.assertEqual(os.path.join(wkdir, "my_sample13"), r)

            self.assertTrue(os.path.exists(r))


if __name__ == "__main__":
    setup_logger.setup(verbose=True)

    unittest.main()
