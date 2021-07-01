import unittest
import logging
import summer2020py.setup_logger as setup_logger
import summer2020py.make_genebody_coverage_graphs.make_genebody_coverage_graphs as mgcg

import pandas
import tempfile
import os
temp_wkdir_prefix = "TestMakeGeneBodyCoverageGraphs"


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


class TestMakeGeneBodyCoverageGraphs(unittest.TestCase):
    def test_main(self):
        with tempfile.TemporaryDirectory(prefix=temp_wkdir_prefix) as wkdir:
            logger.debug("\n \n \n test_main:  {}\n \n ".format(wkdir))
            args = mgcg.build_parser().parse_args([
                    #"-s", source_dir, 
                    "-i", "assets\\notebook_inputs\\output_gbdy_cov\\", 
                    "-o", wkdir,
                    "-of", "MYEXPERIMENTID"
                ])

            mgcg.main(args)
            
            #check that html files were outputted 
            self.assertTrue(os.path.exists(os.path.join(wkdir, "MYEXPERIMENTID_genebody_histogram_coverage_diff.html")))
            self.assertTrue(os.path.exists(os.path.join(wkdir, "MYEXPERIMENTID_genebody_histogram_cov_diff_pct.html")))
            self.assertTrue(os.path.exists(os.path.join(wkdir, "MYEXPERIMENTID_genebody_coverage_percentile.html")))
            self.assertTrue(os.path.exists(os.path.join(wkdir, "MYEXPERIMENTID_genebody_coverage_counts.html")))


            #check that the text files are the same as example outputss
            #doesn't work for html files
            outputted_files = [
            os.path.join(wkdir, "MYEXPERIMENTID_all_genebody_coverage_r1200x6.txt"),
            os.path.join(wkdir, "MYEXPERIMENTID_asymmetry_compare_80_20_r12x6.txt")
            ]

            expected_files = [
                "assets\\example_notebook_outputs\\MYEXPERIMENTID_all_genebody_coverage_r1200x6.txt",
                "assets\\example_notebook_outputs\\MYEXPERIMENTID_asymmetry_compare_80_20_r12x6.txt"
            ]

            for i in range(0, len(outputted_files)):
                opened_output = open(outputted_files[i], "r")
                opened_expected = open(expected_files[i], "r")
                logger.debug("checking {} against expected".format(outputted_files[i]))
                self.assertEqual(opened_output.read(), opened_expected.read())
                opened_output.close()
                opened_expected.close()



    def test_input_file_search(self):
        logger.debug("\n \n \n test_input_file_search\n \n ")
        input_dir = "assets\\notebook_inputs\\output_gbdy_cov\\"
        input_files = mgcg.input_file_search(input_dir)
        self.assertEqual(len(input_files), 12)

    def test_input_files_to_dfs(self):
        input_files = ["assets\\notebook_inputs\\output_gbdy_cov\\D121\\D121.geneBodyCoverage.txt", "assets\\notebook_inputs\\output_gbdy_cov\\D122\\D122.geneBodyCoverage.txt"]
        inp_df_list = mgcg.input_files_to_dfs(input_files)

        #check that there are two data frames
        self.assertEqual(len(inp_df_list), 2)

        #check that first df is the right shape
        self.assertEqual(inp_df_list[0].shape[0], 100)
        self.assertEqual(inp_df_list[0].shape[1], 2)

        #check that second df is the right shape
        self.assertEqual(inp_df_list[1].shape[0], 100)
        self.assertEqual(inp_df_list[1].shape[1], 2)

        #check that sample id are the right ones
        self.assertEqual(inp_df_list[0].sample_id[0], "D121")
        self.assertEqual(inp_df_list[1].sample_id[0], "D122")

    def test_merge_dfs_into_one(self):
        logger.debug("\n \n \n test_merge_dfs_into_one\n \n ")

        #create first fake data frame
        df = pandas.DataFrame({"coverage_counts":range(100000,500000, 4000), "sample_id":"FAKE"})
        df.index.name = "genebody_pct"
        df.index += 1 

        #create second fake data frame
        df2 = pandas.DataFrame({"coverage_counts":range(120000,520000, 4000), "sample_id":"FACE"})
        df2.index.name = "genebody_pct"
        df2.index += 1 

        counts_df = mgcg.merge_dfs_into_one([df, df2])

        logger.debug(counts_df)

        #check that df is the right shape
        self.assertEqual(counts_df.shape[0], 200)
        self.assertEqual(counts_df.shape[1], 3)

        #check that first sample id is fake and that 11th is face 
        self.assertEqual(counts_df.sample_id[0], "FAKE")
        self.assertEqual(counts_df.sample_id[100], "FACE")

    def test_sum_counts(self):
        logger.debug("\n \n \n test_sum_counts\n \n ")

        sample_ids =[]
        for i in range(0, 200):
            if i < 100:
                sample_ids.append("FAKE")
            else:
                sample_ids.append("FACE")

        #create fake data frame 
        counts_df = pandas.DataFrame({"coverage_counts":list(range(100000,500000, 4000)) + list(range(120000,520000, 4000)), "sample_id":sample_ids})

        sum_counts_df = mgcg.sum_counts(counts_df)

        logger.debug(counts_df)
        logger.debug(sum_counts_df)

        #check that df is the right shape
        self.assertEqual(sum_counts_df.shape[0], 2)
        self.assertEqual(sum_counts_df.shape[1], 1)

        #check that the sums are correct 
        self.assertEqual(sum_counts_df.total_coverage_counts[0], 31800000)
        self.assertEqual(sum_counts_df.total_coverage_counts[1], 29800000)


    def test_join_counts_sum(self):
        logger.debug("\n \n \n test_join_counts_sum\n \n ")

        sample_ids =[]
        for i in range(0, 200):
            if i < 100:
                sample_ids.append("FAKE")
            else:
                sample_ids.append("FACE")

        counts_df = pandas.DataFrame({"coverage_counts":list(range(100000,500000, 4000)) + list(range(120000,520000, 4000)), "sample_id":sample_ids})

        sum_counts_df = pandas.DataFrame(data = {"total_coverage_counts":[31800000, 29800000]}, index = ["FACE", "FAKE"])
        sum_counts_df.index.name = "sample_id"

        percentile_df = mgcg.join_counts_sum(counts_df, sum_counts_df)
        

        #check that df is the right shape
        self.assertEqual(percentile_df.shape[0], 200)
        self.assertEqual(percentile_df.shape[1], 4)

        #check that first sample id is fake and that 11th is face 
        self.assertEqual(percentile_df.sample_id[0], "FAKE")
        self.assertEqual(percentile_df.sample_id[100], "FACE")

        #check that FAKE coveragecounts are 2.8 mil and FACE are 3 mil
        self.assertEqual(percentile_df.total_coverage_counts[0], 29800000)
        self.assertEqual(percentile_df.total_coverage_counts[100], 31800000)


    def test_create_pct_df_list(self):
        logger.debug("\n \n \n test_create_pct_df_list\n \n ")
       
        sample_ids =[]
        for i in range(0, 200):
            if i < 100:
                sample_ids.append("FAKE")
            else:
                sample_ids.append("FACE")

        coverage_percentile = list(range(3356,16756,134)) + list(range(2726,16226, 135))
        for num in range(len(coverage_percentile)):
            coverage_percentile[num] = coverage_percentile[num] / 1000000

        percentile_df = pandas.DataFrame({"coverage_percentile":coverage_percentile, "sample_id":sample_ids, "genebody_pct":list(range(1,101))+ list(range(1,101))})

        pct_df_list = mgcg.create_pct_df_list(percentile_df)

        logger.debug(pct_df_list)

        #checking 20th
        self.assertEqual(pct_df_list[0].coverage_20pct[0],  0.005902)
        self.assertEqual(pct_df_list[0].coverage_20pct[1],  0.005291)

        #checking 50th
        self.assertEqual(pct_df_list[1].coverage_50pct[0], 0.009922)
        self.assertEqual(pct_df_list[1].coverage_50pct[1], 0.009341)

        #checking 80th
        self.assertEqual(pct_df_list[2].coverage_80pct[0],  0.013942)
        self.assertEqual(pct_df_list[2].coverage_80pct[1],  0.013391)

    def test_create_pct_comp_df(self):
        logger.debug("\n \n \n test_create_pct_comp_df\n \n ")
        
        df20 = pandas.DataFrame(data = {"coverage_20pct":[0.005902,0.005291]}, index = ["FAKE", "FACE"])
        df20.index.name = "sample_id"

        df50 = pandas.DataFrame(data = {"coverage_50pct":[0.009922,0.009341]}, index = ["FAKE", "FACE"])
        df50.index.name = "sample_id"

        df80 = pandas.DataFrame(data = {"coverage_80pct":[0.013942,0.013391]}, index = ["FAKE", "FACE"])
        df80.index.name = "sample_id"

        pct_comp_df = mgcg.create_pct_comp_df([df20, df50, df80])

        logger.debug(pct_comp_df)

        self.assertAlmostEqual(pct_comp_df.cov_diff_pct[0], 0.810320, places=5)
        self.assertAlmostEqual(pct_comp_df.cov_diff_pct[1], 0.867145, places=5)
        

    def test_add_label_col_to_pct(self):
        logger.debug("\n \n \n test_add_label_col_to_pct\n \n ")

        pct_comp_df = pandas.DataFrame(data = {"cov_diff_pct":[0.810320,0.867145]}, index = ["FAKE", "FACE"])
        pct_comp_df.index.name = "sample_id"

        pct_comp_df = mgcg.add_label_col_to_pct(pct_comp_df)

        logger.debug(pct_comp_df)

        self.assertEqual(pct_comp_df.label[0], "FAKE  0.81")
        self.assertEqual(pct_comp_df.label[1], "FACE  0.87")

    def test_add_label_col_to_percentile(self):
        logger.debug("\n \n \n test_add_label_col_to_percentile\n \n ")

        sample_ids =[]
        for i in range(0, 200):
            if i < 100:
                sample_ids.append("FAKE")
            else:
                sample_ids.append("FACE") 

        pct_comp_df = pandas.DataFrame(data = {"cov_diff_pct":[0.810320,0.867145], "label":["FAKE  0.81", "FACE  0.87"]}, index = ["FAKE", "FACE"])

        percentile_df = pandas.DataFrame({"sample_id":sample_ids})

        percentile_df = mgcg.add_label_col_to_percentile(percentile_df, pct_comp_df)

        self.assertEqual(percentile_df.label[0], "FAKE  0.81")
        self.assertEqual(percentile_df.label[100], "FACE  0.87")


        

    def test_save_to_tsv(self):
        with tempfile.TemporaryDirectory(prefix=temp_wkdir_prefix) as wkdir:
            logger.debug("\n \n \n test_save_to_tsv:  {}\n \n ".format(wkdir))

            output_all_pct_template = "{exp_id}_all_genebody_coverage_r{{}}x{{}}.txt".format(exp_id="MYEXPERIMENTID")
            logger.debug(output_all_pct_template)

            output_compare_80_20_template = "{exp_id}_asymmetry_compare_80_20_r{{}}x{{}}.txt".format(exp_id="MYEXPERIMENTID")
            logger.debug(output_compare_80_20_template)

            pct_comp_df = pandas.DataFrame(data = {"cov_diff_pct":[0.810320,0.867145], "label":["FAKE  0.81", "FACE  0.87"]}, index = ["FAKE", "FACE"])

            sample_ids =[]
            for i in range(0, 200):
                if i < 100:
                    sample_ids.append("FAKE")
                else:
                    sample_ids.append("FACE")

            coverage_percentile = list(range(3356,16756,134)) + list(range(2726,16226, 135))
            for num in range(len(coverage_percentile)):
                coverage_percentile[num] = coverage_percentile[num] / 1000000

            percentile_df = pandas.DataFrame({"coverage_percentile":coverage_percentile, "sample_id":sample_ids, "genebody_pct":list(range(1,101))+ list(range(1,101))})

            out_f_pct = mgcg.save_to_tsv(wkdir, output_compare_80_20_template, pct_comp_df)
            out_f_percentile = mgcg.save_to_tsv(wkdir, output_all_pct_template, percentile_df)

            logger.debug(out_f_pct)
            logger.debug(out_f_percentile)

            self.assertTrue(os.path.exists(out_f_pct))
            self.assertTrue(os.path.exists(out_f_percentile))


    def test_create_and_save_line_graph(self):
        with tempfile.TemporaryDirectory(prefix=temp_wkdir_prefix) as wkdir:
            logger.debug("\n \n \n test_create_and_save_line_graph:  {}\n \n ".format(wkdir))

            output_line_html_template = "{exp_id}_genebody_{{}}.html".format(exp_id="MYEXPERIMENTID")
            logger.debug(output_line_html_template)

            sample_ids =[]
            labels = []
            for i in range(0, 200):
                if i < 100:
                    sample_ids.append("FAKE")
                    labels.append("FAKE  0.81")
                else:
                    sample_ids.append("FACE")
                    labels.append("FAcE  0.87")

            coverage_percentile = list(range(3356,16756,134)) + list(range(2726,16226, 135))
            for num in range(len(coverage_percentile)):
                coverage_percentile[num] = coverage_percentile[num] / 1000000

            percentile_df = pandas.DataFrame({"coverage_percentile":coverage_percentile, "sample_id":sample_ids, "genebody_pct":list(range(1,101))+ list(range(1,101)), "label":labels})

            output_filepath = mgcg.create_and_save_line_graph("coverage_percentile", wkdir, percentile_df, output_line_html_template)

            self.assertTrue(os.path.exists(output_filepath))





    def test_create_and_save_histograms(self):
        with tempfile.TemporaryDirectory(prefix=temp_wkdir_prefix) as wkdir:
            logger.debug("\n \n \n test_create_and_save_histograms:  {}\n \n ".format(wkdir))

            output_histogram_html_template = "{exp_id}_genebody_histogram_{{}}.html".format(exp_id="MYEXPERIMENTID")
            logger.debug(output_histogram_html_template)

            pct_comp_df = pandas.DataFrame(data = {"cov_diff_pct":[0.810320,0.867145], "label":["FAKE  0.81", "FACE  0.87"]}, index = ["FAKE", "FACE"])

            output_filepath = mgcg.create_and_save_histograms("cov_diff_pct", wkdir, pct_comp_df, output_histogram_html_template)

            self.assertTrue(os.path.exists(output_filepath))




        


if __name__ == "__main__":
    setup_logger.setup(verbose=True)

    unittest.main()
