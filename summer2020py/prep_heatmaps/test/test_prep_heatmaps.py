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

        #one way is find a python touch method and use that to create an empty file 
        #if a file is not there touch creates it if the file is there it updates the timestame to the current timestamp
        #
                
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
                

    


class TestPrepHeatmaps(unittest.TestCase):
    def test_main(self):
        with tempfile.TemporaryDirectory(prefix=temp_wkdir_prefix) as wkdir:
            logger.debug("\n \n \n test_main:  {}\n \n ".format(wkdir))
            test_id = "MYTESTID1234567"
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
            random_of_input_file((test_id + "_FHT1234_CL1_TP1_PID_CL2_TP2_DGE_r30500x10.txt"),dge_data_test)
            random_of_input_file((test_id + "_FHT1234_CL3_TP3_PID2_CL4_TP4_DGE_r30500x10.txt"),dge_data_test)
        
            #simulate adding the commands on the command line using parser
            args = ph.build_parser().parse_args(["-s", source_dir, "-e", test_id, "-d", dgestatsforheatmaps, "-b", 
            base_path, "-r", relative_path, "-se", server])


            
            html = ph.main(args)

            expected_html = ("""<html>
    <body>
    <h1>MYTESTID1234567 links to interactive heatmaps of differential gene expression (DGE) statistics</h1>
    <ul><li><a href="http://fht.samba.data/fht_morpheus.html?gctData={}/MYTESTID1234567_heatmap_logFC_r10x2.gct"> heatmap of dge statistic:  logFC</a></li>
    <li><a href="http://fht.samba.data/fht_morpheus.html?gctData={}/MYTESTID1234567_heatmap_t_r10x2.gct"> heatmap of dge statistic:  t</a></li>
    </ul>
    </body>
    </html>""").format(os.path.join(args.basedatapath, args.experimentid, args.relativepath), os.path.join(args.basedatapath, args.experimentid, args.relativepath))

            self.maxDiff = None # add this line so when checking difference here with subsequent assert if there is a 
            # difference it will be displayed (not limited b/c of length)
            self.assertEqual(expected_html, html)

            




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
            logger.debug("\n \n \n test_find_DGE_files wkdir:  {}\n \n ".format(wkdir))
            
            #saving the test versions of source_dir and test_id to variables and also creating a test id that won't be tested
            source_dir = os.path.join(wkdir,"source_test")
            test_id ="MYTESTID1234567"
            notthistest_id = "rnauasf"
            dge_data_test = os.path.join(source_dir, "dge_data")

            #creating directories
            os.mkdir(source_dir)
            os.mkdir(dge_data_test)

            #creating files for the method to find and put into a list

            expectedbasename1 = random_of_input_file((test_id + "_FHT1234_CL1_TP1_PID_CL2_TP2_DGE_r30500x10.txt"),dge_data_test)
            expectedbasename2 = random_of_input_file((test_id + "_FHT1234_CL3_TP3_PID2_CL4_TP4_DGE_r30500x10.txt"),dge_data_test)
            random_of_input_file((notthistest_id + "_FHT1234_CL3_TP3_PID2_CL4_TP4_DGE_r30500x10.txt"),dge_data_test)
            


            #running the method
            dge_file_list = ph.find_DGE_files(source_dir, test_id)

            #create a strings to the path 
            #can create variable, os.path.basename of dge_file_list and check that the string is that 

            #assert that the list has what you want in it
            self.assertTrue(len(dge_file_list) == 2)
            expectedbasenameset = {expectedbasename1, expectedbasename2}
            r_basenameset = set([os.path.basename(x) for x in dge_file_list])
            self.assertEqual(expectedbasenameset, r_basenameset)

    
    def test_read_DGE_files(self):
        #test can be improved, right now it only test when there is one thing in dge_file_list, which while it shows
        #that the methods works the are ways that this test could pass but the code isn't working correctly 
        with tempfile.TemporaryDirectory(prefix=temp_wkdir_prefix) as wkdir:
            logger.debug("\n \n \n test_read_DGE_files wkdir:  {}\n \n ".format(wkdir))
            #creating testod and paths of the directories
            test_id ="MYTESTID1234567"
            source_dir = os.path.join(wkdir,"source_test")
            dge_data_test = os.path.join(source_dir, "dge_data")

            #creating directories
            os.mkdir(source_dir)
            os.mkdir(dge_data_test)

            random_of_input_file((test_id + "_FHT1234_CL1_TP1_PID_CL2_TP2_DGE_r30500x10.txt"),dge_data_test)
            random_of_input_file((test_id + "_FHT1234_CL3_TP3_PID2_CL4_TP4_DGE_r30500x10.txt"),dge_data_test)

            dge_file_list = ph.find_DGE_files(source_dir, test_id)

            dge_df_list = ph.read_DGE_files(dge_file_list)
            
            expected_columns_list = ['gene_symbol', 'logFC', 'CI_L', 'CI_R', 'AveExpr', 't', 'P_Value','adj_P_Val', 'B', 'neg_log_adj_P_Val']

            self.assertTrue(len(dge_df_list) == 2)
            for dge_df, dge_file in dge_df_list:
                self.assertListEqual(dge_df.columns.tolist(), expected_columns_list)
            

    def test_prepare_data_df(self):
        with tempfile.TemporaryDirectory(prefix=temp_wkdir_prefix) as wkdir:
            logger.debug("\n \n \n test_prepare_data_df: wkdir {}\n \n ".format(wkdir))
            #creating file and a list to pass into read DGE_files
            test_id ="MYTESTID1234567"
            source_dir = os.path.join(wkdir,"source_test")
            dge_data_test = os.path.join(source_dir, "dge_data")

            #creating directories
            os.mkdir(source_dir)
            os.mkdir(dge_data_test)

            random_of_input_file((test_id + "_FHT1234_CL1_TP1_PID_CL2_TP2_DGE_r30500x10.txt"),dge_data_test)
            random_of_input_file((test_id + "_FHT1234_CL3_TP3_PID2_CL4_TP4_DGE_r30500x10.txt"),dge_data_test)

            dge_file_list = ph.find_DGE_files(source_dir, test_id)

            dge_df_list = ph.read_DGE_files(dge_file_list)
            dge_stat =  "logFC"

            data_df = ph.prepare_data_df(dge_stat, dge_df_list)
            logger.debug("data_df\n{}".format(data_df))
            logger.debug("data_df.columns\n{}".format(data_df.columns.tolist()))
            
            
            for item in data_df.columns.tolist():
                list_ = item.split("_")
                self.assertEqual(list_[0], dge_stat)
 
            #something to test that it worked


    def test_prepare_col_metadata(self):
        with tempfile.TemporaryDirectory(prefix=temp_wkdir_prefix) as wkdir:
            logger.debug("\n \n \n test_prepare_col_metadata: wkdir {}\n \n ".format(wkdir))

            logger.debug("\n \n \n test_prepare_data_df: wkdir {}\n \n ".format(wkdir))
            #creating file and a list to pass into read DGE_files
            test_id ="MYTESTID1234567"
            source_dir = os.path.join(wkdir,"source_test")
            dge_data_test = os.path.join(source_dir, "dge_data")

            #creating directories
            os.mkdir(source_dir)
            os.mkdir(dge_data_test)

            random_of_input_file((test_id + "_FHT1234_CL1_TP1_PID_CL2_TP2_DGE_r30500x10.txt"),dge_data_test)
            random_of_input_file((test_id + "_FHT1234_CL3_TP3_PID2_CL4_TP4_DGE_r30500x10.txt"),dge_data_test)

            dge_file_list = ph.find_DGE_files(source_dir, test_id)

            dge_df_list = ph.read_DGE_files(dge_file_list)
            dge_stat =  "logFC" 

            data_df = ph.prepare_data_df(dge_stat, dge_df_list)
            
            col_metadata_df = ph.prepare_col_metadata(dge_stat, data_df.columns)

            for item in col_metadata_df.index.tolist():
                list_ = item.split("_")
                self.assertEqual(list_[0], dge_stat)


            for item in col_metadata_df.columns.tolist():
                if item == "dge_statistic":
                    dge_staritstic_there = True

            self.assertTrue(dge_staritstic_there)

            #something to test that the columns are correct  right now only check that one column is named dge_statistic


    
    def test_prepare_GCToo_object(self):     
        with tempfile.TemporaryDirectory(prefix=temp_wkdir_prefix) as wkdir:
            logger.debug("\n \n \n test_prepare_GCToo_object wkdir:  {}\n \n ".format(wkdir))
            #creating file and a list to pass into read DGE_files
            test_id ="MYTESTID1234567"
            source_dir = os.path.join(wkdir,"source_test")
            dge_data_test = os.path.join(source_dir, "dge_data")

            #creating directories
            os.mkdir(source_dir)
            os.mkdir(dge_data_test)

            random_of_input_file((test_id + "_FHT1234_CL1_TP1_PID_CL2_TP2_DGE_r30500x10.txt"),dge_data_test)
            random_of_input_file((test_id + "_FHT1234_CL3_TP3_PID2_CL4_TP4_DGE_r30500x10.txt"),dge_data_test)

            dge_file_list = ph.find_DGE_files(source_dir, test_id)

            dge_df_list = ph.read_DGE_files(dge_file_list)
            dge_stat = "logFC"
        
            heatmap_g = ph.prepare_GCToo_object(dge_stat, dge_df_list)

            logger.debug("heatmap_g: \n{}".format(heatmap_g))
        

            #something to test that it works

    def test_prepare_all_GCToo_objects(self):
        #test can be improved, right now it only test when there is one thing in dge_file_list, which while it shows
        #that the methods works the are ways that this test could pass but the code isn't working correctly 
        with tempfile.TemporaryDirectory(prefix=temp_wkdir_prefix) as wkdir:
            logger.debug("\n \n \n test_read_DGE_files wkdir:  {}\n \n ".format(wkdir))
            #creating file and a list to pass into read DGE_files
            test_id ="MYTESTID1234567"
            source_dir = os.path.join(wkdir,"source_test")
            dge_data_test = os.path.join(source_dir, "dge_data")

            #creating directories
            os.mkdir(source_dir)
            os.mkdir(dge_data_test)

            random_of_input_file((test_id + "_FHT1234_CL1_TP1_PID_CL2_TP2_DGE_r30500x10.txt"),dge_data_test)
            random_of_input_file((test_id + "_FHT1234_CL3_TP3_PID2_CL4_TP4_DGE_r30500x10.txt"),dge_data_test)

            dge_file_list = ph.find_DGE_files(source_dir, test_id)

            dge_df_list = ph.read_DGE_files(dge_file_list)
            dge_stats_for_heatmaps = ["logFC", "t"]

            heatmap_gct_list = ph.prepare_all_GCToo_objects(dge_stats_for_heatmaps, dge_df_list)

            self.assertEqual(len(heatmap_gct_list), 2)

            dge_stat_from_heatmap_gct_list = []
        
            for i in range(0, len(heatmap_gct_list)):
                dge_stat_from_heatmap_gct_list.append(heatmap_gct_list[i][0])

            self.assertListEqual(dge_stat_from_heatmap_gct_list, dge_stats_for_heatmaps)

            #only test that the stats for heamtamps are there, does not test the actual GCtToo object
                

            #can't think of a way to test this without having the code from the method

    def test_write_GCToo_objects_to_files(self):
        with tempfile.TemporaryDirectory(prefix=temp_wkdir_prefix) as wkdir:
            logger.debug("\n \n \n test_write_GCToo_objects_to_files wkdir:  {}\n \n ".format(wkdir))
            
            #creating file and a list to pass into read DGE_files
            test_id ="MYTESTID1234567"
            source_dir = os.path.join(wkdir,"source_test")
            dge_data_test = os.path.join(source_dir, "dge_data")

            #creating directories
            os.mkdir(source_dir)
            os.mkdir(dge_data_test)

            random_of_input_file((test_id + "_FHT1234_CL1_TP1_PID_CL2_TP2_DGE_r30500x10.txt"),dge_data_test)
            random_of_input_file((test_id + "_FHT1234_CL3_TP3_PID2_CL4_TP4_DGE_r30500x10.txt"),dge_data_test)

            dge_file_list = ph.find_DGE_files(source_dir, test_id)

            dge_df_list = ph.read_DGE_files(dge_file_list)
            dge_stats_for_heatmaps = ["logFC", "t"]
            dge_df_list = ph.read_DGE_files(dge_file_list)

            heatmap_gct_list = ph.prepare_all_GCToo_objects(dge_stats_for_heatmaps, dge_df_list)
            
            output_template = test_id + "_heatmap_{dge_stat}_r{rows}x{cols}.gct"
            heatmap_dir = source_dir

            ph.write_GCToo_objects_to_files(heatmap_gct_list, output_template, heatmap_dir)

            for dge_stat, heatmap_g in heatmap_gct_list:
                output_filename = output_template.format(
                dge_stat=dge_stat, rows=heatmap_g.data_df.shape[0], cols=heatmap_g.data_df.shape[1]
                )
                expectedsrc = output_filename
                self.assertEqual(expectedsrc, heatmap_g.src)
                

    def test_prepare_links(self):
        
        with tempfile.TemporaryDirectory(prefix=temp_wkdir_prefix) as wkdir:
            logger.debug("\n \n \n test_prepare_links: wkdir {}\n \n ".format(wkdir))
            #creating file and a list to pass into read DGE_files
            test_id ="MYTESTID1234567"
            source_dir = os.path.join(wkdir,"source_test")
            dge_data_test = os.path.join(source_dir, "dge_data")

            #creating directories
            os.mkdir(source_dir)
            os.mkdir(dge_data_test)

            random_of_input_file((test_id + "_FHT1234_CL1_TP1_PID_CL2_TP2_DGE_r30500x10.txt"),dge_data_test)
            random_of_input_file((test_id + "_FHT1234_CL3_TP3_PID2_CL4_TP4_DGE_r30500x10.txt"),dge_data_test)

            dge_file_list = ph.find_DGE_files(source_dir, test_id)

            dge_df_list = ph.read_DGE_files(dge_file_list)
            dge_stats_for_heatmaps = ["logFC", "t"]
            dge_df_list = ph.read_DGE_files(dge_file_list)

            heatmap_gct_list = ph.prepare_all_GCToo_objects(dge_stats_for_heatmaps, dge_df_list)
            
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
            logger.debug("\n \n \n test_write_to_html wkdir:  {}\n \n ".format(wkdir))
            #creating file and a list to pass into read DGE_files

            test_id ="MYTESTID1234567"
            source_dir = os.path.join(wkdir,"source_test")
            dge_data_test = os.path.join(source_dir, "dge_data")

            #creating directories
            os.mkdir(source_dir)
            os.mkdir(dge_data_test)

            url_list = [('logFC', 'http://fht.samba.data/fht_morpheus.html?gctData=C:{}\\MYTESTID1234567_heatmap_logFC_r10x2.gct'.format(wkdir)), 
            ('t', 'http://fht.samba.data/fht_morpheus.html?gctData=C:{}\\MYTESTID1234567_heatmap_t_r10x2.gct'.format(wkdir))]
            output_html_link_file = "{exp_id}_interactive_heatmap_links.html".format(exp_id= test_id)
            
            html = ph.write_to_html(source_dir, output_html_link_file, url_list, test_id)

            a_lines = ["""<li><a href="{url}"> heatmap of dge statistic:  {dge_stat}</a></li>
    """.format(url=url, dge_stat=dge_stat) for dge_stat, url in url_list]

            expected_html = ("""<html>
    <body>
    <h1>{exp_id} links to interactive heatmaps of differential gene expression (DGE) statistics</h1>
    <ul>""".format(exp_id=test_id)
    + "".join(a_lines)
    + """</ul>
    </body>
    </html>"""
    )
            self.assertEqual(html, expected_html)


            

    def test_write_html_to_file(self):
        with tempfile.TemporaryDirectory(prefix=temp_wkdir_prefix) as wkdir:
            logger.debug("\n \n \n test_write_html_to_file wkdir :  {}\n \n ".format(wkdir))

            test_id ="MYTESTID1234567"
            source_dir = os.path.join(wkdir,"source_test")
            dge_data_test = os.path.join(source_dir, "dge_data")

            #creating directories
            os.mkdir(source_dir)
            os.mkdir(dge_data_test)

            heatmap_dir = source_dir

            url_list = [('logFC', 'http://fht.samba.data/fht_morpheus.html?gctData=C:{}\\MYTESTID1234567_heatmap_logFC_r10x2.gct'.format(wkdir)), 
            ('t', 'http://fht.samba.data/fht_morpheus.html?gctData=C:{}\\MYTESTID1234567_heatmap_t_r10x2.gct'.format(wkdir))]

            a_lines = ["""<li><a href="{url}"> heatmap of dge statistic:  {dge_stat}</a></li>
            """.format(url=url, dge_stat=dge_stat) for dge_stat, url in url_list]

            output_html_link_file = "{exp_id}_interactive_heatmap_links.html".format(exp_id=test_id)

            html_filepath = os.path.join(heatmap_dir, output_html_link_file)

            html = ph.write_html_to_file(a_lines, test_id, html_filepath)

            expected_html = ("""<html>
    <body>
    <h1>{exp_id} links to interactive heatmaps of differential gene expression (DGE) statistics</h1>
    <ul>""".format(exp_id=test_id)
    + "".join(a_lines)
    + """</ul>
    </body>
    </html>"""
    )
            self.assertEqual(html, expected_html)
            
            







            
            
                  
                    
            
        


if __name__ == "__main__":
    setup_logger.setup(verbose=True)
    
    unittest.main()
    
