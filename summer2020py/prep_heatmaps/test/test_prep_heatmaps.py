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
import pathlib

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
    #this method was supposed to randomize the file at path, I couldn't get it to work so it just copies the file 
    path = os.path.join("assets", "prep_heatmap_example_input_DGE_r10x10.txt")
    outputpath = os.path.join(dirs, name)
    
    shutil.copyfile(path, outputpath)

    return name


class TestPrepHeatmaps(unittest.TestCase):
    def test_main(self):
        with tempfile.TemporaryDirectory(prefix=temp_wkdir_prefix) as wkdir:
            logger.debug("\n \n \n test_main:  {}\n \n ".format(wkdir))
            test_id = "MYEXPID98765"
            base_path = wkdir
            relative_path = "heatmaps"
            base_url = "http://fht.samba.data/fht_morpheus.html?gctData="
            source_dir = os.path.join(wkdir,"source_test")
            dge_stats_for_heatmaps = ["logFC", "t"]
            dge_data_test = os.path.join(source_dir, "dge_data")

            #creating directories
            os.mkdir(source_dir)
            os.mkdir(dge_data_test)  

            #making directories so that base_data_path won't throw an error when called
            os.mkdir(os.path.join(wkdir, test_id))
            os.mkdir(os.path.join(wkdir, test_id, relative_path))     
            
            #adding some samples
            random_of_input_file((test_id + "_FHT1234_A549_tp1_24h_Vehicle_A549_tp1_24h_DGE_r30500x10.txt"),dge_data_test)
            random_of_input_file((test_id + "_FHT1234_A549_tp2_24h_Vehicle_A549_tp2_24h_DGE_r30500x10.txt"),dge_data_test)
        
            #simulate adding the commands on the command line using parser
            args = ph.build_parser().parse_args(["-s", source_dir, "-e", test_id, "-d", dge_stats_for_heatmaps, "-b", 
            base_path, "-r", relative_path, "-u", base_url])

            html = ph.main(args)

            expected_html = ("""<html>
    <body>
    <h1>MYEXPID98765 links to interactive heatmaps of differential gene expression (DGE) statistics</h1>
    <ul><li><a href="http://fht.samba.data/fht_morpheus.html?gctData={}/MYEXPID98765_heatmap_logFC_r10x2.gct"> heatmap of dge statistic:  logFC</a></li>
    <li><a href="http://fht.samba.data/fht_morpheus.html?gctData={}/MYEXPID98765_heatmap_t_r10x2.gct"> heatmap of dge statistic:  t</a></li>
    </ul>
    </body>
    </html>""").format(os.path.join(args.base_data_path, args.experiment_id, args.relative_path), os.path.join(args.base_data_path, args.experiment_id, args.relative_path))

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

            test_file = os.path.join(heatmaps, "test_file")
            
            pathlib.Path(test_file).touch()

            ph.prepare_output_dir(wkdir)
            self.assertTrue(os.path.exists(heatmaps)) #making sure that the output directory was created
            self.assertFalse(os.path.exists(test_file))#making sure that this is a new directory and not the old one that had a file in it
    
    
    def test_find_DGE_files(self):
         with tempfile.TemporaryDirectory(prefix=temp_wkdir_prefix) as wkdir:
            logger.debug("\n \n \n test_find_DGE_files wkdir:  {}\n \n ".format(wkdir))
            
            #saving the test versions of source_dir and test_id to variables and also creating a test id that won't be tested
            source_dir = os.path.join(wkdir,"source_test")
            test_id ="MYEXPID98765"
            notthistest_id = "rnauasf"
            dge_data_test = os.path.join(source_dir, "dge_data")

            #creating directories
            os.mkdir(source_dir)
            os.mkdir(dge_data_test)

            #creating files for the method to find and put into a list
            test_file_path = os.path.join(dge_data_test, (test_id + "_FHT1234_A549_tp1_24h_Vehicle_A549_tp1_24h_DGE_r30500x10.txt"))
            another_test_file_path = os.path.join(dge_data_test, (test_id + "_FHT1234_A549_tp1_24h_Vehicle_A549_tp1_24h_DGE_r30500x10_another.txt"))
            not_test_file_path = os.path.join(dge_data_test, (notthistest_id + "_FHT1234_A549_tp2_24h_Vehicle_A549_tp2_24h_DGE_r30500x10.txt"))

            pathlib.Path(test_file_path).touch()
            pathlib.Path(another_test_file_path).touch()
            pathlib.Path(not_test_file_path).touch()

            #running the method
            dge_file_list = ph.find_DGE_files(source_dir, test_id)

            #create a strings to the path 
            #can create variable, os.path.basename of dge_file_list and check that the string is that 

            #assert that the list has what you want in it
            self.assertTrue(len(dge_file_list) == 2)
            expectedbasenameset = {os.path.basename(test_file_path), os.path.basename(another_test_file_path)}
            r_basenameset = set([os.path.basename(x) for x in dge_file_list])
            self.assertEqual(expectedbasenameset, r_basenameset)

    
    def test_read_DGE_files(self):
        #test can be improved, right now it only test when there is one thing in dge_file_list, which while it shows
        #that the methods works the are ways that this test could pass but the code isn't working correctly 
        with tempfile.TemporaryDirectory(prefix=temp_wkdir_prefix) as wkdir:
            logger.debug("\n \n \n test_read_DGE_files wkdir:  {}\n \n ".format(wkdir))
            #creating testod and paths of the directories
            test_id ="MYEXPID98765"
            source_dir = os.path.join(wkdir,"source_test")
            dge_data_test = os.path.join(source_dir, "dge_data")

            #creating directories
            os.mkdir(source_dir)
            os.mkdir(dge_data_test)

            random_of_input_file((test_id + "_FHT1234_A549_tp1_24h_Vehicle_A549_tp1_24h_DGE_r30500x10.txt"),dge_data_test)
            random_of_input_file((test_id + "_FHT1234_A549_tp2_24h_Vehicle_A549_tp2_24h_DGE_r30500x10.txt"),dge_data_test)

            dge_file_list = ['{}/source_test/dge_data/MYEXPID98765_FHT1234_A549_tp1_24h_Vehicle_A549_tp1_24h_DGE_r30500x10.txt'.format(wkdir), 
            '{}/source_test/dge_data/MYEXPID98765_FHT1234_A549_tp2_24h_Vehicle_A549_tp2_24h_DGE_r30500x10.txt'.format(wkdir)]

            dge_df_list = ph.read_DGE_files(dge_file_list)
            
            expected_columns_list = ['gene_symbol', 'logFC', 'CI_L', 'CI_R', 'AveExpr', 't', 'P_Value','adj_P_Val', 'B', 'neg_log_adj_P_Val']

            self.assertTrue(len(dge_df_list) == 2)
            for dge_df, dge_file in dge_df_list:
                self.assertListEqual(dge_df.columns.tolist(), expected_columns_list)
                self.assertEqual((10,10), dge_df.shape)
            

    def test_prepare_data_df(self):
        logger.debug("\n \n \n test_prepare_data_df\n \n ")
        
        dge_df_list = [
            (pandas.DataFrame({"logFC":range(10), "unused_column":range(10,20)}), "ignore1_my_first_dge_df_ign3_ign4.txt"),
            (pandas.DataFrame({"another_unused_column":range(30,40), "logFC":range(40,50)}), "ignore2_my_2nd_dge_df_ign5_ign6.txt")
        ]
        dge_stat =  "logFC"

        data_df = ph.prepare_data_df(dge_stat, dge_df_list)
        logger.debug("data_df\n{}".format(data_df.values.tolist()))
        logger.debug("data_df.columns\n{}".format(data_df.columns.tolist()))
        
        for item in data_df.columns.tolist():
            list_ = item.split("_")
            self.assertEqual(list_[0], dge_stat)
        
        self.assertEqual(data_df.columns.tolist(), ["logFC_my_first_dge_df", "logFC_my_2nd_dge_df"])
 

    def test_prepare_col_metadata(self):
        logger.debug("\n \n \n test_prepare_col_metadata\n \n ")
        
        dge_stat =  "logFC" 

        data_df_columns = ["logFC_FHT1234_A549_tp1_24h_Vehicle_A549_tp1_24h","logFC_FHT1234_A549_tp2_24h_Vehicle_A549_tp2_24h"]
        
        col_metadata_df = ph.prepare_col_metadata(dge_stat, data_df_columns)
        logger.debug("col_metadata_df:\n{}".format(col_metadata_df))

        self.assertTrue(all(data_df_columns == col_metadata_df.index))

        self.assertIn("dge_statistic", col_metadata_df.columns)

        # this is really good
        col_df_without_dge_stat = col_metadata_df.drop("dge_statistic", axis=1)
        self.assertEqual(col_df_without_dge_stat.values.tolist(), [x.split("_") for x in data_df_columns])


    def test_prepare_GCToo_object(self):     
        with tempfile.TemporaryDirectory(prefix=temp_wkdir_prefix) as wkdir:
            logger.debug("\n \n \n test_prepare_GCToo_object wkdir:  {}\n \n ".format(wkdir))
            #creating file and a list to pass into read DGE_files
            test_id ="MYEXPID98765"
            source_dir = os.path.join(wkdir,"source_test")
            dge_data_test = os.path.join(source_dir, "dge_data")

            #creating directories
            os.mkdir(source_dir)
            os.mkdir(dge_data_test)

            random_of_input_file((test_id + "_FHT1234_A549_tp1_24h_Vehicle_A549_tp1_24h_DGE_r30500x10.txt"),dge_data_test)
            random_of_input_file((test_id + "_FHT1234_A549_tp2_24h_Vehicle_A549_tp2_24h_DGE_r30500x10.txt"),dge_data_test)

            dge_file_list = ['{}/source_test/dge_data/MYEXPID98765_FHT1234_A549_tp1_24h_Vehicle_A549_tp1_24h_DGE_r30500x10.txt'.format(wkdir), 
            '{}/source_test/dge_data/MYEXPID98765_FHT1234_A549_tp2_24h_Vehicle_A549_tp2_24h_DGE_r30500x10.txt'.format(wkdir)] 

            dge_df_list = [
            (
            pandas.read_csv(dge_file, sep="\t", index_col=0),
            os.path.basename(dge_file)
            )
            for dge_file in dge_file_list
            ]
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
            test_id ="MYEXPID98765"
            source_dir = os.path.join(wkdir,"source_test")
            dge_data_test = os.path.join(source_dir, "dge_data")

            #creating directories
            os.mkdir(source_dir)
            os.mkdir(dge_data_test)

            random_of_input_file((test_id + "_FHT1234_A549_tp1_24h_Vehicle_A549_tp1_24h_DGE_r30500x10.txt"),dge_data_test)
            random_of_input_file((test_id + "_FHT1234_A549_tp2_24h_Vehicle_A549_tp2_24h_DGE_r30500x10.txt"),dge_data_test)

            dge_file_list = ['{}/source_test/dge_data/MYEXPID98765_FHT1234_A549_tp1_24h_Vehicle_A549_tp1_24h_DGE_r30500x10.txt'.format(wkdir), 
            '{}/source_test/dge_data/MYEXPID98765_FHT1234_A549_tp2_24h_Vehicle_A549_tp2_24h_DGE_r30500x10.txt'.format(wkdir)] 

            dge_df_list = [
            (
            pandas.read_csv(dge_file, sep="\t", index_col=0),
            os.path.basename(dge_file)
            )
            for dge_file in dge_file_list
            ]
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
            test_id ="MYEXPID98765"
            source_dir = os.path.join(wkdir,"source_test")
            dge_data_test = os.path.join(source_dir, "dge_data")

            #creating directories
            os.mkdir(source_dir)
            os.mkdir(dge_data_test)

            random_of_input_file((test_id + "_FHT1234_A549_tp1_24h_Vehicle_A549_tp1_24h_DGE_r30500x10.txt"),dge_data_test)
            random_of_input_file((test_id + "_FHT1234_A549_tp2_24h_Vehicle_A549_tp2_24h_DGE_r30500x10.txt"),dge_data_test)

            dge_file_list = ['{}/source_test/dge_data/MYEXPID98765_FHT1234_A549_tp1_24h_Vehicle_A549_tp1_24h_DGE_r30500x10.txt'.format(wkdir), 
            '{}/source_test/dge_data/MYEXPID98765_FHT1234_A549_tp2_24h_Vehicle_A549_tp2_24h_DGE_r30500x10.txt'.format(wkdir)] 

            dge_df_list = [
            (
            pandas.read_csv(dge_file, sep="\t", index_col=0),
            os.path.basename(dge_file)
            )
            for dge_file in dge_file_list
            ]
            
            test_dge_stat = "logFC"
            
            output_template = test_id + "_heatmap_{dge_stat}_r{rows}x{cols}.gct"
            heatmap_dir = source_dir


            data_df_vaules = [[0.0776354686633181, 0.0776354686633181], [-0.581704751304994, -0.581704751304994], [-0.6736706335046471, -0.6736706335046471], 
            [-0.6983420979505, -0.6983420979505], [0.17469165710934198, 0.17469165710934198], [0.00627185142921816, 0.00627185142921816], 
            [-0.368901439453788, -0.368901439453788], [0.144740264311605, 0.144740264311605], [1.03902293388003, 1.03902293388003], [-0.243853638780661, -0.243853638780661]]

            data_columns = ['logFC_FHT1234_A549_tp1_24h_Vehicle_A549_tp1_24h', 'logFC_FHT1234_A549_tp2_24h_Vehicle_A549_tp2_24h']

            data_index = ['ENSG00000236389', 'ENSG00000115355', 'ENSG00000162613', 'ENSG00000189143', 'ENSG00000204044', 
            'ENSG00000259051', 'ENSG00000126467', 'ENSG00000276408', 'ENSG00000136842', 'ENSG00000239559']

            data_df = pandas.DataFrame(data_df_vaules, columns = data_columns, index = data_index)

            col_meta_list = [x.split("_") for x in data_columns]
            col_metadata_df = pandas.DataFrame(col_meta_list)
            col_metadata_df.columns = ["annot{}".format(c) for c in col_metadata_df.columns]
            col_metadata_df["dge_statistic"] = test_dge_stat
            col_metadata_df.index = data_df.columns

            row_metadata_df = dge_df_list[0][0][["gene_symbol"]]

            test_heatmap_gct_list = [("logFC", GCToo.GCToo(data_df, col_metadata_df=col_metadata_df, row_metadata_df=row_metadata_df))]

            ph.write_GCToo_objects_to_files(test_heatmap_gct_list, output_template, heatmap_dir)

            for dge_stat, heatmap_g in test_heatmap_gct_list:
                output_filename = output_template.format(
                dge_stat=dge_stat, rows=heatmap_g.data_df.shape[0], cols=heatmap_g.data_df.shape[1]
                )
                expectedsrc = output_filename
                self.assertEqual(expectedsrc, heatmap_g.src)
                

    def test_prepare_links(self):
        
        with tempfile.TemporaryDirectory(prefix=temp_wkdir_prefix) as wkdir:
            logger.debug("\n \n \n test_prepare_links: wkdir {}\n \n ".format(wkdir))
            #creating file and a list to pass into read DGE_files
            test_id ="MYEXPID98765"
            source_dir = os.path.join(wkdir,"source_test")
            dge_data_test = os.path.join(source_dir, "dge_data")

            #creating directories
            os.mkdir(source_dir)
            os.mkdir(dge_data_test)

            random_of_input_file((test_id + "_FHT1234_A549_tp1_24h_Vehicle_A549_tp1_24h_DGE_r30500x10.txt"),dge_data_test)
            random_of_input_file((test_id + "_FHT1234_A549_tp2_24h_Vehicle_A549_tp2_24h_DGE_r30500x10.txt"),dge_data_test)

            dge_file_list = ['{}/source_test/dge_data/MYEXPID98765_FHT1234_A549_tp1_24h_Vehicle_A549_tp1_24h_DGE_r30500x10.txt'.format(wkdir), 
            '{}/source_test/dge_data/MYEXPID98765_FHT1234_A549_tp2_24h_Vehicle_A549_tp2_24h_DGE_r30500x10.txt'.format(wkdir)] 

            dge_df_list = [
            (
            pandas.read_csv(dge_file, sep="\t", index_col=0),
            os.path.basename(dge_file)
            )
            for dge_file in dge_file_list
            ]
            test_dge_stat = "logFC"

            output_template = test_id + "_heatmap_{dge_stat}_r{rows}x{cols}.gct"
    

            data_df_vaules = [[0.0776354686633181, 0.0776354686633181], [-0.581704751304994, -0.581704751304994], [-0.6736706335046471, -0.6736706335046471], 
            [-0.6983420979505, -0.6983420979505], [0.17469165710934198, 0.17469165710934198], [0.00627185142921816, 0.00627185142921816], 
            [-0.368901439453788, -0.368901439453788], [0.144740264311605, 0.144740264311605], [1.03902293388003, 1.03902293388003], [-0.243853638780661, -0.243853638780661]]

            data_columns = ['logFC_FHT1234_A549_tp1_24h_Vehicle_A549_tp1_24h', 'logFC_FHT1234_A549_tp2_24h_Vehicle_A549_tp2_24h']

            data_index = ['ENSG00000236389', 'ENSG00000115355', 'ENSG00000162613', 'ENSG00000189143', 'ENSG00000204044', 
            'ENSG00000259051', 'ENSG00000126467', 'ENSG00000276408', 'ENSG00000136842', 'ENSG00000239559']

            data_df = pandas.DataFrame(data_df_vaules, columns = data_columns, index = data_index)

            col_meta_list = [x.split("_") for x in data_columns]
            col_metadata_df = pandas.DataFrame(col_meta_list)
            col_metadata_df.columns = ["annot{}".format(c) for c in col_metadata_df.columns]
            col_metadata_df["dge_statistic"] = test_dge_stat
            col_metadata_df.index = data_df.columns

            row_metadata_df = dge_df_list[0][0][["gene_symbol"]]

            test_heatmap_gct_list = [("logFC", GCToo.GCToo(data_df, col_metadata_df=col_metadata_df, row_metadata_df=row_metadata_df))]
            
            base_data_path = wkdir

            output_template = test_id + "_heatmap_{dge_stat}_r{rows}x{cols}.gct"

            url_template = "http://fht.samba.data/fht_morpheus.html?gctData={data_path}"


            for dge_stat, heatmap_g in test_heatmap_gct_list:
                output_filename = output_template.format(
                    dge_stat=dge_stat, rows=heatmap_g.data_df.shape[0], cols=heatmap_g.data_df.shape[1]
                )
                heatmap_g.src = output_filename

            url_list = ph.prepare_links(test_heatmap_gct_list, url_template, base_data_path)

            i = 0
            for dge_stat, heatmap_g in test_heatmap_gct_list:
                data_path = os.path.join(base_data_path, heatmap_g.src)
                cur_url = url_template.format(data_path=data_path)
                self.assertTrue(url_list[i] == (dge_stat, cur_url))
                i += 1

            
    def test_prepare_html(self):
        with tempfile.TemporaryDirectory(prefix=temp_wkdir_prefix) as wkdir:
            logger.debug("\n \n \n test_prepare_html wkdir :  {}\n \n ".format(wkdir))

            test_id = "MYEXPID98765"

            url_list = [('logFC', 'http://fht.samba.data/fht_morpheus.html?gctData=C:{}/MYEXPID98765_heatmap_logFC_r10x2.gct'.format(wkdir)), 
            ('t', 'http://fht.samba.data/fht_morpheus.html?gctData=C:{}/MYEXPID98765_heatmap_t_r10x2.gct'.format(wkdir))]
            

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
        
        html = ph.prepare_html(url_list, test_id)

        self.assertEqual(html, expected_html)


    def test_determine_html_filepath(self):
        with tempfile.TemporaryDirectory(prefix=temp_wkdir_prefix) as wkdir:
            logger.debug("\n \n \n test_determine_html_filepath wkdir :  {}\n \n ".format(wkdir))

            html_file_name = "html_file"

            html_filepath = ph.determine_html_filepath(wkdir, html_file_name)

            self.assertEqual(html_filepath, os.path.join(wkdir, html_file_name))

            #determine_html_filepath is just a join statment


    def test_write_html_to_file(self):
        with tempfile.TemporaryDirectory(prefix=temp_wkdir_prefix) as wkdir:
            logger.debug("\n \n \n test_write_html_to_file wkdir :  {}\n \n ".format(wkdir))

            html_filepath = os.path.join(wkdir, "html_file")

            ph.write_html_to_file("hi", html_filepath)

            self.assertTrue(os.path.exists(html_filepath))

            with open(html_filepath) as html_file:
                self.assertTrue("hi" in html_file)


if __name__ == "__main__":
    setup_logger.setup(verbose=True)
    
    unittest.main()
    
