import unittest
import logging
import summer2020py.setup_logger as setup_logger
import summer2020py.clustered_heatmaps.sub_and_super_clusters as sasc

import os.path
import pandas as pd
import numpy
import scipy


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

    def test_get_cluster_centers(self):
        logger.debug("\n \n \n test_get_cluster_centers:  \n \n ")

        tiny_test_data_df = pd.DataFrame([[1, 2, 3, 3], [1, 4, 5, 4], [1, 0, 5, 0],[4, 2, 3, 2], [4, 4, 5, 4], [4, 0, 3, 0]])

        cluster_centers_indices_col = [1, 2]
        cluster_centers_indices_row = [1, 5]
        

        expected_col_cluster_centers = [[2, 4, 0, 2, 4, 0], [3, 5, 5, 3, 5, 3]]
        expected_row_cluster_centers = [[1, 4, 5, 4], [4, 0, 3, 0]]

 
        col_cluster_centers = sasc.get_cluster_centers(tiny_test_data_df, cluster_centers_indices_col)
        logger.debug("col_cluster_centers: {}".format(col_cluster_centers))

        row_cluster_centers = sasc.get_cluster_centers(tiny_test_data_df, cluster_centers_indices_row)
        logger.debug("row_cluster_centers: {}".format(row_cluster_centers))

        #checking that the arrays are equal
        for i in range(0, 2):
            self.assertTrue((col_cluster_centers[i] == expected_col_cluster_centers[i]).all())
            self.assertTrue((row_cluster_centers[i] == expected_row_cluster_centers[i]).all())


    def test_get_child_counts(self):
                
        test_linkage_matrix = pd.DataFrame([[1,  2,  1.000000,  numpy.NaN],[0,  3,  6.436309,  numpy.NaN]])

        returned_linkage_matrix = sasc.get_child_counts( test_linkage_matrix)

        self.assertEqual(returned_linkage_matrix.loc[0, 3], 2.0)
        self.assertEqual(returned_linkage_matrix.loc[1, 3], 3.0)
    
    def test_run_scipy_cluster_dendrogram(self):
        logger.debug("\n \n \n test_run_scipy_cluster_dendrogram:  \n \n ")

        test_linkage_matrix = pd.DataFrame([[1,  2,  1.000000,  2.0],[0,  3,  6.436309,  3.0]])

        super_r_dict = sasc.run_scipy_cluster_dendrogram(test_linkage_matrix)

        self.assertTrue((super_r_dict['leaves'] == [0, 1, 2]))


    def test_super_cluster(self):
        logger.debug("\n \n \n test_super_cluster:  \n \n ")

        col_cluster_centers = [[2, 4, 0, 2, 4, 0], [3, 5, 5, 3, 5, 3], [3, 5, 5, 3, 5, 4]]

        super_linkage_matrix_with_counts, super_r_dict = sasc.super_cluster(col_cluster_centers)

        expected_linkage = pd.DataFrame([[1,  2,  1.000000,  2.0],[0,  3, 6.436308967734172,  3.0]])
        logger.debug(" expected_linkage: \n{}".format( expected_linkage))

        equal_linkage_matrix = (super_linkage_matrix_with_counts.eq(expected_linkage))

        self.assertTrue((super_r_dict['leaves'] == [0, 1, 2]))
        self.assertTrue((equal_linkage_matrix.all()).all())


    def test_change_labels(self):
        logger.debug("\n \n \n test_change_labels:  \n \n ")

        label_index = sasc.change_labels([0, 2, 5, 1, 3, 4])

        self.assertTrue((label_index == [0, 3, 1, 4, 5, 2]))

    def test_reorder_super_cluster(self):
        logger.debug("\n \n \n test_reorder_super_cluster:  \n \n ")

        label_df =  pd.DataFrame([[1,2,3,3,0],[1,4,4,5,0],[4,4,4,5,0],[1,0,0,5,1],[4,2,2,3,1],[4,0,0,3,1],[0,0,0,1,20000]])

        logger.debug("label_df: {}".format(label_df))

        super_dendro_labels_index = [1, 0]

        label_df = sasc.reorder_super_cluster(label_df, super_dendro_labels_index)

        self.assertTrue((label_df.loc[6] == [1, 1, 1, 0, 20000]).all())


    def test_update_super_matrix(self):
        logger.debug("\n \n \n test_update_super_matrix:  \n \n ")

        linkage_matrix = pd.DataFrame([[1,  2,  1.000000,  2.0],[0,  3, 6.436308967734172,  3.0]])
        labels_index = [2, 1, 0]

        super_linkage_matrix = sasc.update_super_matrix(linkage_matrix, labels_index)

        logger.debug("super_linkage_matrix: {}".format(super_linkage_matrix))

        #check that locations were changed as they should be
        self.assertEqual(super_linkage_matrix.loc[0, 0], 1)
        self.assertEqual(super_linkage_matrix.loc[1, 0], 2)
        self.assertEqual(super_linkage_matrix.loc[0, 1], 0)

        #check that distance were changed as they should be
        #which is divided until they are less then 4
        #then have 5 added to them
        self.assertAlmostEqual(super_linkage_matrix.loc[0, 2], 5.500000)
        self.assertAlmostEqual(super_linkage_matrix.loc[1, 2], 8.218154483867085)


    def test_prepare_where(self):
        logger.debug("\n \n \n test_prepare_where:  \n \n ")

        linkage_matrix = pd.DataFrame([[1,  2,  1.000000,  2.0],[0,  3, 6.436308967734172,  3.0]])

        where, where_col, not_where = sasc.prepare_where(linkage_matrix, 0)

        logger.debug("where: {}".format(where))
        logger.debug("linkae_matrix: {}".format(linkage_matrix))

        #check that where is the correct row and that where_col and not_where are correct
        self.assertTrue((where == linkage_matrix.loc[1]).all().all())
        self.assertEqual(where_col,  0)
        self.assertEqual(not_where,  1)


    def test_prepare_sub_matrix(self):
        logger.debug("\n \n \n test_prepare_sub_matrix:  \n \n ")

        tiny_test_data_df = pd.DataFrame([[1, 2, 3, 3], [1, 4, 5, 4], [1, 0, 5, 0],[4, 2, 3, 2], [4, 4, 5, 4], [4, 0, 3, 0]])
        linkage_matrix = pd.DataFrame([[1,  2,  1.000000,  2.0],[0,  3, 6.436308967734172,  3.0]])

        sub_cluster = pd.DataFrame([[1, 2, 3], [1, 4, 5], [1, 0, 5],[4, 2, 3], [4, 4, 5], [4, 0, 3]])

        handy_values = {
                'new_location':1,
                'new_cluster':4,
                'current_sub':0,
                'len_super':4,
                'len_sub':2,
                'n_sub_samples':3,
                'n_super_samples':5
            }
        
        df_sub_linkage_matrix = sasc.prepare_sub_matrix(linkage_matrix, handy_values, tiny_test_data_df, sub_cluster)

        logger.debug("df_sub_linkage_matrix: {}".format(df_sub_linkage_matrix))

        #check that locations were changed as they should be
        self.assertEqual(df_sub_linkage_matrix.loc[1, 0], 0)
        self.assertEqual(df_sub_linkage_matrix.loc[2, 0], 6)
        self.assertEqual(df_sub_linkage_matrix.loc[1, 1], 5)
        self.assertEqual(df_sub_linkage_matrix.loc[1, 4], 1)
        self.assertEqual(df_sub_linkage_matrix.loc[2, 4], 0)
        self.assertEqual(df_sub_linkage_matrix.loc[1, 5], 2)

    def test_prepare_super(self):
        logger.debug("\n \n \n test_prepare_super:  \n \n ")

        handy_values = {
                'new_location':1,
                'new_cluster':4,
                'current_sub':0,
                'len_super':4,
                'len_sub':2,
                'n_sub_samples':3,
                'n_super_samples':5
            }


        linkage_matrix = pd.DataFrame([[1,  2,  5.500000,  2.0],[0,  5, 6.436308967734172,  3.0], [3,  6, 7.0,  4.0], [4,  7, 8.0,  4.0]])

        df_super_linkage_matrix = sasc.prepare_super(linkage_matrix, handy_values)

        logger.debug("df_super_linkage_matrix: {}".format(df_super_linkage_matrix))

        #check that linkage shape was chnaged
        self.assertTrue(df_super_linkage_matrix.shape == (3, 4))


    def test_col_4_5_updating_1_2(self):
        logger.debug("\n \n \n test_col_4_5_updating_1_2:  \n \n ")

        linkage = pd.DataFrame([[1,  2,  1.000000,  2.0, 1000, 1001],[0,  3, 6.436308967734172,  3.0, 999, numpy.NaN]])

        linkage_matrix = sasc.col_4_5_updating_1_2(linkage)

        logger.debug("linkage_matrix: {}".format(linkage_matrix))

        #check that locations were changed as they should be
        self.assertEqual(linkage_matrix.loc[0, 0], 1000)
        self.assertEqual(linkage_matrix.loc[1, 0], 999)
        self.assertEqual(linkage_matrix.loc[0, 1], 1001)


    def test_fix_linkage_matrix(self):
        logger.debug("\n \n \n test_fix_linkage_matrix:  \n \n ")
        
        linkage = pd.DataFrame([[1123,  2124,  1.000000,  12.0, 1, 2],[124,  3, 6.436308967734172,  14.0, 0, numpy.NaN]])
        
        
        linkage_matrix = sasc.fix_linkage_matrix(linkage)

        #check that locations were changed as they should be
        self.assertEqual(linkage_matrix.loc[0, 0], 1)
        self.assertEqual(linkage_matrix.loc[1, 0], 0)
        self.assertEqual(linkage_matrix.loc[0, 1], 2)
        self.assertEqual(linkage_matrix.loc[0, 3], 2.0)
        self.assertEqual(linkage_matrix.loc[1, 3], 3.0)



    def test_get_newick(self):
        logger.debug("\n \n \n test_get_newick:  \n \n ")

        linkage_matrix = pd.DataFrame([[1,  2,  1.000000,  2.0],[0,  3, 6.436308967734172,  3.0]])
        labels_index = [2, 1, 0]


        tree = scipy.cluster.hierarchy.to_tree(linkage_matrix,False)

        newick = sasc.getNewick(tree, "", tree.dist, labels_index)

        logger.debug('newick: {}'.format(newick))

        self.assertEqual(newick,  "((0:1.00,1:1.00):5.44,2:6.44);")



    def test_create_dendrogram_from_df(self):
        logger.debug("\n \n \n test_create_dendrogram_from_df:  \n \n ")

        tiny_test_data_df = pd.DataFrame([[1, 2, 3, 3], [1, 4, 5, 4], [1, 0, 5, 0],[4, 2, 3, 2], [4, 4, 5, 4], [4, 0, 3, 0]])


        newick, sas_sorted_df, super_and_sub_dendro_labels_index = sasc.create_dendrogram_from_df("row", tiny_test_data_df)

        logger.debug("newick:{}".format(newick))
        logger.debug("sas_sorted_df:{}".format(sas_sorted_df))
        logger.debug("super_and_sub_dendro_labels_index:{}".format(super_and_sub_dendro_labels_index))

        expected_output = pd.DataFrame([[1,  0,  5,  0],[4,  2,  3,  2],[4,  0,  3,  0],[4,  4,  5,  4],[1,  2,  3,  3],[1,  4,  5,  4]])

        self.assertTrue(((sas_sorted_df.to_numpy() == expected_output.to_numpy()).all()).all())


    def test_create_col_and_row_template(self):
        logger.debug("\n \n \n test_create_col_and_row_template:  \n \n ")

        col_and_row_template =  sasc.create_col_and_row_template(True, "Hi")
        self.assertEqual(col_and_row_template['field'], "Hi")
        self.assertEqual(col_and_row_template['maxTextWidth'], 0)


    def test_create_col_and_row_metadata_template(self):
        logger.debug("\n \n \n test_create_col_and_row_metadata_template:  \n \n ")

        col_and_row_metadata = sasc.create_col_and_row_metadata_template(True, "Hi", [0])
        self.assertEqual(col_and_row_metadata['name'], "Hi")
        self.assertEqual(col_and_row_metadata['array'], [0])
        self.assertEqual(col_and_row_metadata["properties"]["morpheus.dataType"], "string")

    
    def test_loop_through_clusters(self):

        total_linkage_matrix = pd.DataFrame([0,  1,  8.354102,  2.0, numpy.NaN, numpy.NaN])
        total_linkage_matrix = total_linkage_matrix.transpose()
        label_df =  pd.DataFrame([[1,2,3,3,0],[1,4,4,5,0],[1,0,0,5,1],[4,2,2,3,1],[4,4,4,5,0],[4,0,0,3,1],[0,1,2,3,20000]])
        label_df = label_df.transpose()
        num_row = 4
        super_dendro_labels_index = [0, 1]
        data_df = pd.DataFrame([[1,2,3,3],[1,4,4,5],[4,4,4,5],[1,0,0,5],[4,2,2,3],[4,0,0,3],[0,0,0,1]])
        data_df = data_df.transpose()

        new_linkage_matrix = sasc.loop_through_clusters(total_linkage_matrix, label_df, num_row, super_dendro_labels_index, data_df)

        logger.debug("new_linkage_matrix:{}".format(new_linkage_matrix))

        expected_linkage = pd.DataFrame([[0.0, 2.0, 3.000000, 2.0, 0.0, 1.0], [3.0, 6.0, 3.6213203435596424, 3.0, 4.0, numpy.NaN], [1.0, 4.0, 1.4142135623730951, 2.0, 3.0, 5.0], [5.0, 8.0, 2.047031742604957, 3.0, 2.0, numpy.NaN], [7.0, 9.0, 8.354102, 8.0, numpy.NaN, numpy.NaN]])

        self.assertTrue(expected_linkage.equals(new_linkage_matrix))


    def test_prepare_metadata(self):
        #wondering about how to test this
        #prepare_metadata(gctoo, data_df, super_and_sub_dendro_labels_index, row_labels, num_row, num_col)
        #here are the inputs
        #gctoo, data_df, num_row and num_col are easy to get
        #the problem is the other two
        #which would be arrays of len 1305 and I don't feel like manually typing those out
        #best thing would be to create a fake gctoo for testing but I am not sure how to do that
        pass

    def test_create_json(self):

        template_path = "template.json"
        output_path = "super_and_sub_file.json"
        sas_sorted_df = pd.DataFrame([[1,  0,  5,  0],[4,  2,  3,  2],[4,  0,  3,  0],[4,  4,  5,  4],[1,  2,  3,  3],[1,  4,  5,  4]])
        col_metadata_df = pd.DataFrame([[0, 1, 2, 3]])
        row_metadata_df = pd.DataFrame([[0, 1, 2, 3, 4, 5]])
        col_newick = "COLNEWICK"
        row_newick = "ROWNEWICK"

        returned_output_path = sasc.create_json(template_path, output_path, sas_sorted_df, col_metadata_df, row_metadata_df, col_newick, row_newick)

        self.assertEqual(returned_output_path, output_path)


    def test_main(self):
        logger.debug("\n \n \n test_main:  \n \n ")

        #no need to create fake args as everything is hardcoded in right now
        #will change
        args = sasc.build_parser().parse_args([
            "--template_path", "template.json", 
            "--gctx_path", "2020_Q3_Achilles_CCLE_expression_r19144x1305.gctx",
            "--output_path", "super_and_sub_file.json",
            "--row_or_col", "both",
            "--num_row", "1000"
        ])

        output_path = sasc.main(args)

        #check that there is a file and that it is json
        self.assertTrue(os.path.exists(output_path))
        self.assertEqual(os.path.splitext(output_path)[1], ".json")

        #the best test is loading the file into morpheous and seeing how it looks

        logger.debug(output_path)



    

if __name__ == "__main__":
    setup_logger.setup(verbose=True)

    unittest.main()
