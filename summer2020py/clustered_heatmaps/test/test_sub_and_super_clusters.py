import unittest
import logging
import summer2020py.setup_logger as setup_logger
import summer2020py.clustered_heatmaps.sub_and_super_clusters as sasc

import os.path
import pandas as pd
import numpy


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


class TestSubandSuperClusters(unittest.TestCase):
    def test_load_data(self):
        logger.debug("\n \n \n test_load_data:  \n \n ")
        gctx_path = os.path.join("2020_Q3_Achilles_CCLE_expression_r19144x1305.gctx")

        data_df_rows_chopped, gctoo = sasc.load_data(20, gctx_path)

        self.assertEqual(data_df_rows_chopped.shape, (20, 1305))

    def test_run_AffinityProp(self):
        logger.debug("\n \n \n test_run_AffinityProp:  \n \n ")

        tiny_test_data_df = pd.DataFrame([[1, 2, 3, 3], [1, 4, 5, 4], [1, 0, 5, 0],[4, 2, 3, 2], [4, 4, 5, 4], [4, 0, 3, 0]])

        Affinity_prop_row = sasc.run_AffinityProp("row", tiny_test_data_df)
        Affinity_prop_col = sasc.run_AffinityProp("col", tiny_test_data_df)

        expected_labels_row = [0, 0, 1, 1, 0, 1]
        expected_labels_col = [0, 0, 1, 0]

        #check that labels are as expected
        self.assertTrue((Affinity_prop_row.labels_ == expected_labels_row).all())
        self.assertTrue((Affinity_prop_col.labels_ == expected_labels_col).all())

    def test_get_cluster_centers(self):
        logger.debug("\n \n \n test_get_cluster_centers:  \n \n ")

        tiny_test_data_df = pd.DataFrame([[1, 2, 3, 3], [1, 4, 5, 4], [1, 0, 5, 0],[4, 2, 3, 2], [4, 4, 5, 4], [4, 0, 3, 0]])

        cluster_centers_indices_col = [1, 2]
        cluster_centers_indices_row = [1, 5]
        

        expected_col_cluster_centers = [[2, 4, 0, 2, 4, 0], [3, 5, 5, 3, 5, 3]]
        expected_row_cluster_centers = [[1, 4, 5, 4], [4, 0, 3, 0]]

 
        col_cluster_centers = sasc.get_cluster_centers("col",  tiny_test_data_df, cluster_centers_indices_col)
        logger.debug("col_cluster_centers: {}".format(col_cluster_centers))

        row_cluster_centers = sasc.get_cluster_centers("row",  tiny_test_data_df, cluster_centers_indices_row)
        logger.debug("row_cluster_centers: {}".format(row_cluster_centers))

        #checking that the arrays are equal
        for i in range(0, 2):
            self.assertTrue((col_cluster_centers[i] == expected_col_cluster_centers[i]).all())
            self.assertTrue((row_cluster_centers[i] == expected_row_cluster_centers[i]).all())


    def test_sort_and_drop(self):
        logger.debug("\n \n \n test_sort_and_drop:  \n \n ")    
        test_label_df = pd.DataFrame([[1,  2,  3,  3,      0],[1,  4,  5,  4,      0],[1,  0,  5,  0,      1],[4,  2,  3,  2,      1],[4,  4,  5,  4,      0],[4,  0,  3,  0,      1],[0,  0,  1,  0,  20000]])
        name_col = 4
        name_row = 6

        print("test_label_df: {}".format(test_label_df))

        sorted_df = sasc.sort_and_drop(name_col, name_row, test_label_df)

        #check that the column names are reordered as they should be 
        self.assertTrue((sorted_df.columns == [0, 1, 3, 2]).all())
        self.assertTrue((sorted_df.index == [0, 1, 4, 2, 3, 5]).all())
    
    def test_sort_by_label_list(self):
        logger.debug("\n \n \n test_sort_by_label_list:  \n \n ")

        tiny_test_data_df = pd.DataFrame([[1, 2, 3, 3], [1, 4, 5, 4], [1, 0, 5, 0],[4, 2, 3, 2], [4, 4, 5, 4], [4, 0, 3, 0]])

        expected_labels_row = [0, 0, 1, 1, 0, 1]
        expected_labels_col = [0, 0, 1, 0]

        sorted_df, label_df = sasc.sort_by_label_list(tiny_test_data_df, expected_labels_row, expected_labels_col)

        #check that the column names are reordered as they should be 
        self.assertTrue((sorted_df.columns == [0, 1, 3, 2]).all())
        self.assertTrue((sorted_df.index == [0, 1, 4, 2, 3, 5]).all())


    def test_get_child_counts(self):
                
        test_linkage_matrix = pd.DataFrame([[1,  2,  1.000000,  numpy.NaN],[0,  3,  6.436309,  numpy.NaN]])

        returned_linkage_matrix = sasc.get_child_counts( test_linkage_matrix)

        self.assertEqual(returned_linkage_matrix.loc[0, 3], 2.0)
        self.assertEqual(returned_linkage_matrix.loc[1, 3], 3.0)


    def test_super_cluster(self):
        logger.debug("\n \n \n test_super_cluster:  \n \n ")

        col_cluster_centers = [[2, 4, 0, 2, 4, 0], [3, 5, 5, 3, 5, 3], [3, 5, 5, 3, 5, 4]]

        super_linkage_matrix_with_counts, super_r_dict = sasc.super_cluster(col_cluster_centers)

        expected_linkage = pd.DataFrame([[1,  2,  1.000000,  2.0],[0,  3, 6.436308967734172,  3.0]])
        logger.debug(" expected_linkage: \n{}".format( expected_linkage))

        equal_linkage_matrix = (super_linkage_matrix_with_counts.eq(expected_linkage))

        self.assertTrue((super_r_dict['leaves'] == [0, 1, 2]))
        self.assertTrue((equal_linkage_matrix.all()).all())

    def test_run_scipy_cluster_dendrogram(self):
        logger.debug("\n \n \n test_run_scipy_cluster_dendrogram:  \n \n ")

        test_linkage_matrix = pd.DataFrame([[1,  2,  1.000000,  2.0],[0,  3,  6.436309,  3.0]])

        super_r_dict = sasc.run_scipy_cluster_dendrogram(test_linkage_matrix)

        self.assertTrue((super_r_dict['leaves'] == [0, 1, 2]))

    def test_change_labels(self):
        logger.debug("\n \n \n test_change_labels:  \n \n ")

        label_index = sasc.change_labels([0, 2, 5, 1, 3, 4])

        self.assertTrue((label_index == [0, 3, 1, 4, 5, 2]))

    def test_create_dendrogram_from_df(self):
        logger.debug("\n \n \n test_create_dendrogram_from_df:  \n \n ")

        gctx_path = os.path.join("2020_Q3_Achilles_CCLE_expression_r19144x1305.gctx")

        data_df_rows_chopped, gctoo = sasc.load_data(3000, gctx_path)

        newick, sas_sorted_df, super_and_sub_dendro_labels_index = sasc.create_dendrogram_from_df("col", data_df_rows_chopped)

        logger.debug("sas_sorted_df: \n {}".format(sas_sorted_df))


    def test_main(self):
        logger.debug("\n \n \n test_main:  \n \n ")

        #no need to create fake args as everything is hardcoded in right now
        #will change
        args = sasc.build_parser().parse_args([])

        output_path = sasc.main(args)

        logger.debug(output_path)



    

if __name__ == "__main__":
    setup_logger.setup(verbose=True)

    unittest.main()
