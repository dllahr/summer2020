import logging
import summer2020py
import summer2020py.setup_logger as setup_logger
import argparse
import sys

import cmapPy.pandasGEXpress.parse
from scipy.cluster.hierarchy import dendrogram
import scipy
import sklearn.cluster
import pandas as pd
import numpy
import json
import os

logger = logging.getLogger(setup_logger.LOGGER_NAME)


def build_parser():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--verbose", "-v", help="Whether to logger.debug a bunch of output.", action="store_true", default=False)

    parser.add_argument("--template_path", "-t", help = "directory where the template file is", type = str, required = True)

    parser.add_argument("--gctx_path", "-g", help = "path to the gctx file", type = str, required = True)

    parser.add_argument("--output_path", "-o", help = "directory where outputs will go", type = str)

    parser.add_argument("--row_or_col", "-r", help = "row creates dendro and grops row, col does the same for col, both does both", type = str)

    parser.add_argument("--num_row", "-n", help = "number of rows to get from data, is all if not given", type = int, default = -1)


    parser.add_argument("--config_filepath", help="path to config file containing information about how to connect to CDD API, ArxLab API etc.",
        type=str, default=summer2020py.default_config_filepath)
    parser.add_argument("--config_section", help="section of config file to use for information about how to connect to CDD API, ArxLab API etc.",
        type=str, default=summer2020py.default_config_section)

    return parser


def load_data(num_rows, path):
    gctoo = cmapPy.pandasGEXpress.parse.parse(path)

    if num_rows == -1:
        num_rows = len(gctoo.data_df.index)

    logger.debug("gctoo{}".format(gctoo))
    data_df_rows_chopped = gctoo.data_df.head(num_rows)

    return data_df_rows_chopped, gctoo

def run_AffinityProp(row_or_col, data_df):
    if row_or_col == "col":
        data_df = data_df.transpose()

    Affinity_prop = sklearn.cluster.AffinityPropagation(affinity = "euclidean", random_state = 0).fit(data_df.to_numpy())

    return Affinity_prop

def sort_and_drop(name_col, name_row, data_df):

    sorted_df = data_df.sort_values(name_col)
    sorted_df = sorted_df.sort_values(name_row, axis = 1)

    logger.debug("sorted_df with labels: {}".format(sorted_df))

    sorted_df = sorted_df.drop(name_row, axis = 0)
    sorted_df = sorted_df.drop(name_col, axis = 1)

    logger.debug("sorted_df: {}".format(sorted_df))

    return sorted_df

def sort_by_label_list(df_to_sort, row_labels, col_labels):

    num_col = len(df_to_sort.columns)
    num_row = len(df_to_sort.index)

    logger.debug("num_col: {}".format(num_col))
    logger.debug("num_row: {}".format(num_row))
    
    logger.debug(row_labels)
    

    col_labels_df = pd.DataFrame(col_labels)
    col_labels_df.rename(columns = {0:num_row}, inplace = True)
    col_labels_df.index = df_to_sort.columns
    col_labels_df = col_labels_df.transpose()

    row_labels_df = pd.DataFrame(row_labels)
    row_labels_df.rename(columns = {0:num_col}, inplace = True)
    row_labels_df.index = df_to_sort.index

    col_labels_df.insert( num_col, num_col, 20000)

    logger.debug("df_to_sort: {}".format(df_to_sort))
    logger.debug("col_labels_df: {}".format(col_labels_df))
    logger.debug("row_labels_df: {}".format(row_labels_df))


    label_df = df_to_sort.join(row_labels_df)

    label_df = label_df.append(col_labels_df)

    logger.debug("label_df: {}".format(label_df))

    sorted_df = sort_and_drop(num_col, num_row, label_df)

    return sorted_df, label_df

def get_cluster_centers(data_df, AffinityProp_cluster_centers_indices):
    
    cluster_centers = []
    

    logger.debug("AffinityProp_cluster_centers_indices: {}".format(AffinityProp_cluster_centers_indices))
    logger.debug("len(AffinityProp_cluster_centers_indices): {}".format(len(AffinityProp_cluster_centers_indices)))
    for i in range (0, len(AffinityProp_cluster_centers_indices)):
        logger.debug("AffinityProp_cluster_centers_indices[i]:{}".format(AffinityProp_cluster_centers_indices[i]))
        logger.debug("data_df.iloc[:, AffinityProp_cluster_centers_indices[i]]:{}".format(data_df.iloc[:, AffinityProp_cluster_centers_indices[i]]))
        logger.debug("(data_df.iloc[:, AffinityProp_cluster_centers_indices[i]]).to_numpy():{}".format((data_df.iloc[:, AffinityProp_cluster_centers_indices[i]]).to_numpy()))

        cluster_column = (data_df.iloc[:, AffinityProp_cluster_centers_indices[i]]).to_numpy()
        cluster_centers.append(cluster_column)

    return cluster_centers

def get_child_counts(linkage_matrix):
    childs = []

    for i in range(0, len(linkage_matrix)):
        childs.append((int(linkage_matrix.loc[i, 0]), int(linkage_matrix.loc[i, 1])))

     # create the counts of samples under each node
    counts = numpy.zeros(len(childs))
    n_samples = len(linkage_matrix) + 1
    for i, merge in enumerate(childs):
        current_count = 0
        for child_idx in merge:
            if child_idx < n_samples:
                current_count += 1  # leaf node
            else:
                current_count += counts[child_idx - n_samples]
        counts[i] = current_count

    counts_df = pd.DataFrame(counts)
    counts_df.columns = [3]

    linkage_matrix.update(counts_df)

    return linkage_matrix

def run_scipy_cluster_dendrogram(linkage_matrix):
    r_dict = dendrogram(linkage_matrix, distance_sort = "ascending")
    return r_dict

def super_cluster(cluster_centers):
    #run and get ward_super_clusters
    #modify matrix to pass into
    ward_super_clusters = sklearn.cluster.AgglomerativeClustering(affinity = "euclidean", n_clusters = len(cluster_centers), linkage = "average", compute_full_tree = True, compute_distances = True).fit(cluster_centers)

    children_df = pd.DataFrame(ward_super_clusters.children_)
    children_df[2] = ward_super_clusters.distances_
    children_df[3] = numpy.NaN

    super_linkage_matrix_with_counts = get_child_counts(children_df)

    logger.debug("super_linkage_matrix_with_counts: \n{}".format(super_linkage_matrix_with_counts))

    super_r_dict = run_scipy_cluster_dendrogram(super_linkage_matrix_with_counts)

    return super_linkage_matrix_with_counts, super_r_dict

def change_labels(label):
    #given labels such as [0, 2, 5, 1, 3, 4]
    #change it so index is the number, and value is where it would go 
    #so [0, 3, 1, 4, 5, 2]
    label_index = []

    for i in range(0, len(label)):
        label_index.append(label.index(i))



    return label_index

def reorder_super_cluster(label_df, super_dendro_labels_index):
    num_col = len(label_df.columns) - 1
    num_row = len(label_df.index) - 1
    
    logger.debug("num_col, num_row")
    
    logger.debug(num_col)
    logger.debug(num_row)

    for i in range(0, num_col + 1):
        val = int(label_df.iloc[num_row, i])
        if val != 20000 and val != numpy.NaN:
            label_df.iloc[num_row, (i)] = super_dendro_labels_index[val]
            #label_df.iloc[i, num_col] = super_dendro_labels_index[val]
            
    logger.debug("label_df: {}".format(label_df))

    return label_df

def update_super_matrix(super_linkage_matrix_with_counts, super_dendro_labels_index):
    while super_linkage_matrix_with_counts[2][len(super_linkage_matrix_with_counts) - 1] > 4:
        super_linkage_matrix_with_counts[2] = super_linkage_matrix_with_counts[2] / 2
    
    for i in range(0, len(super_linkage_matrix_with_counts)):
        zero_leaf = super_linkage_matrix_with_counts.iloc[i, 0]
        one_leaf = super_linkage_matrix_with_counts.iloc[i, 1]
        if zero_leaf < len(super_dendro_labels_index):
            super_linkage_matrix_with_counts.at[i, 0] = super_dendro_labels_index[int(zero_leaf)]
        if one_leaf < len(super_dendro_labels_index):
            super_linkage_matrix_with_counts.at[i, 1] = super_dendro_labels_index[int(one_leaf)]

    super_linkage_matrix_with_counts[4] = numpy.NaN
    super_linkage_matrix_with_counts[5] = numpy.NaN

    #adding 5 to dist values of app super matrix 
    super_linkage_matrix_with_counts[2] = super_linkage_matrix_with_counts[2] + 5

    return super_linkage_matrix_with_counts

def prepare_where(df_super_linkage_matrix, current_sub):
    try:
        where = df_super_linkage_matrix.loc[df_super_linkage_matrix[0] == current_sub]
        if where.shape[0] != 1:
            where = where.loc[where[4] == numpy.NaN]
            if where.shape[0] != 1:
                where = where.loc[where[5] == numpy.NaN]
        where_col = 0
        not_where = 1
        where.index[0]
        
    except IndexError:
        where = df_super_linkage_matrix.loc[df_super_linkage_matrix[1] == current_sub]
        if where.shape[0] != 1:
            where = where.loc[where[4] == numpy.NaN]
            if where.shape[0] != 1:
                where = where.loc[where[5] == numpy.NaN]
        where_col = 1
        not_where = 0
        
        
    return where, where_col, not_where

def prepare_sub_matrix( df_sub_linkage_matrix, handy_values, data_df, sub_cluster):
    for i in range(0, handy_values['len_sub']):
        zero_leaf = df_sub_linkage_matrix.loc[i, 0]
        one_leaf = df_sub_linkage_matrix.loc[i, 1]
        if zero_leaf >= handy_values['n_sub_samples']:
            df_sub_linkage_matrix.at[i, 0] = zero_leaf + handy_values['len_super']  + handy_values['new_location']

        else:       
            df_sub_linkage_matrix.at[i, 4] = data_df.columns.get_loc(sub_cluster.index[int(zero_leaf)])       
            df_sub_linkage_matrix.at[i, 0] = handy_values['new_cluster']
            handy_values['new_cluster'] += 1

        if one_leaf >= handy_values['n_sub_samples']:
            df_sub_linkage_matrix.at[i, 1] = one_leaf  + handy_values['len_super'] + handy_values['new_location']


        else:
            df_sub_linkage_matrix.at[i, 5]  = data_df.columns.get_loc(sub_cluster.index[int(one_leaf)])
            df_sub_linkage_matrix.at[i, 1] = handy_values['new_cluster']
            handy_values['new_cluster'] += 1

    #set the greatest value = to 1
    #that is the sample name that was replaced so this is done to aviod dupes
    
    for i in range(0, len(df_sub_linkage_matrix)):
        if df_sub_linkage_matrix.loc[i, 0] == handy_values['len_super']:
            df_sub_linkage_matrix.at[i, 0] = handy_values['current_sub']
            

        if df_sub_linkage_matrix.loc[i, 1] == handy_values['len_super']:
            df_sub_linkage_matrix.at[i, 1] = handy_values['current_sub']
        
    #change index to be index of where it is going
    df_sub_linkage_matrix.index = df_sub_linkage_matrix.index + handy_values['new_location']
    
    
    return df_sub_linkage_matrix

def prepare_super(df_super_linkage_matrix, handy_values):
        #change super cluster so sub cluster can be added 
    for i in range(0, handy_values['len_super']):
        
        zero_leaf = df_super_linkage_matrix.loc[i, 0]
        one_leaf = df_super_linkage_matrix.loc[i, 1]

        if zero_leaf >= handy_values['n_super_samples']:
            if zero_leaf - handy_values['n_super_samples'] < handy_values['new_location']:
                df_super_linkage_matrix.at[i, 0] = df_super_linkage_matrix.loc[i, 0] + handy_values['len_sub']
            else:
                df_super_linkage_matrix.at[i, 0] = df_super_linkage_matrix.loc[i, 0] + (2 * handy_values['len_sub']) 

        if one_leaf >= handy_values['n_super_samples']:
            if one_leaf - handy_values['n_super_samples'] < handy_values['new_location']:
                df_super_linkage_matrix.at[i, 1] = df_super_linkage_matrix.loc[i, 1] + handy_values['len_sub']
            else:
                df_super_linkage_matrix.at[i, 1] = df_super_linkage_matrix.loc[i, 1] + (2 * handy_values['len_sub']) 
                
    #drop where row and change indexs to prepare for append 
    df_super_linkage_matrix.drop(handy_values['new_location'], inplace = True)
    
    
    return df_super_linkage_matrix

def loop_through_clusters(total_linkage_matrix, label_df, num_row, super_dendro_labels_index, data_df):
    transposed_label_df = label_df.transpose()

    #commented out the logger.debug statements as printing out anything 1000+ times adds up

    for current_sub in range(0, len(super_dendro_labels_index)):
    #get all the values in the current sub cluster
    
        logger.debug("CURRENT SUB")
        logger.debug(current_sub)
        
        sub_cluster = (transposed_label_df.loc[transposed_label_df[num_row] == current_sub])
        
        df_super_linkage_matrix = total_linkage_matrix 

        #get where the sub cluster in in the super cluster matrix
        where_col = 5
        not_where = 5

        where, where_col, not_where = prepare_where(df_super_linkage_matrix, current_sub)

        #logger.debug("WHERE")
        #logger.debug(where)
        
        if sub_cluster.shape[0] != 1:

            # run ward
            ward_sub_cluster = sklearn.cluster.AgglomerativeClustering(affinity = "euclidean", n_clusters = len(sub_cluster)-1, linkage = "average", compute_full_tree = True, compute_distances = True).fit(sub_cluster)

            sub_children_df = pd.DataFrame(ward_sub_cluster.children_)
            sub_children_df[2] = ward_sub_cluster.distances_
            sub_children_df[3] = numpy.NaN

            sub_linkage_matrix = get_child_counts(sub_children_df)

            #make them dataframes since they are better to work with
            df_sub_linkage_matrix = pd.DataFrame(sub_linkage_matrix) 

            #n_samples 
            n_super_samples = len(df_super_linkage_matrix) + 1
            n_sub_samples = len(df_sub_linkage_matrix) + 1

            len_super = len(df_super_linkage_matrix)
            len_sub = len(df_sub_linkage_matrix)

            new_location = where.index[0]
            new_cluster = len_super

            #changing values in sub cluster matrix so it can be merged into super cluster 
            df_sub_linkage_matrix[4] = numpy.NaN
            df_sub_linkage_matrix[5] = numpy.NaN

            #making the dist values less then 4 so it looks nice
            while df_sub_linkage_matrix[2][len(df_sub_linkage_matrix) - 1] > 4:
                df_sub_linkage_matrix[2] = df_sub_linkage_matrix[2] / 2
            
            handy_values = {
                'new_location':new_location,
                'new_cluster':new_cluster,
                'current_sub':current_sub,
                'len_super':len_super,
                'len_sub':len_sub,
                'n_sub_samples':n_sub_samples,
                'n_super_samples':n_super_samples
            }


            df_sub_linkage_matrix = prepare_sub_matrix(df_sub_linkage_matrix, handy_values, data_df, sub_cluster)
            
            #modify where line and add it to end of sub cluster matrix 
            where.at[new_location, where_col] =  new_location + len_super +  (2 * len_sub) 

            #logger.debug("n_super_samples")
            #logger.debug(n_super_samples)

            if where.loc[new_location, not_where] >= n_super_samples:
                    if where.loc[new_location, not_where] - n_super_samples < new_location:
                        where.at[new_location, not_where] = where.loc[new_location, not_where] +len_sub
                    else:
                        where.at[new_location, not_where] = where.loc[new_location, not_where] + (2 * len_sub) 

            where.at[new_location, 3] =  where.loc[new_location, 3] + n_sub_samples

            #logger.debug("WHERE")
            #logger.debug(where)

            #a really dumb way to rename the index
            #.setindex needs a col to set as the index 
            total_sub = pd.DataFrame(where.to_numpy(), index = [where.index[0] + n_sub_samples-1])
            total_sub = df_sub_linkage_matrix.append(total_sub)

            df_super_linkage_matrix = prepare_super(df_super_linkage_matrix, handy_values)

            #logger.debug("REMOVING")
            #logger.debug(new_location)
            #logger.debug("TOTAL SUB")
            #logger.debug(total_sub)
            #logger.debug("NEW LOCATION")
            #logger.debug(new_location)
            #logger.debug("N_SUB_SAMPLES")
            #logger.debug(n_sub_samples)
            #logger.debug("len_sub")
            #logger.debug(len_sub)
            #logger.debug("len_super")
            #logger.debug(len_super)

            df_super_linkage_matrix.index = list(range(0, new_location)) + list(range(new_location + len_sub + 1 , len_super + len_sub))

            #merge then sort by index 
            new_linkage_matrix = df_super_linkage_matrix.append(total_sub)
            new_linkage_matrix.sort_index(inplace = True)

            total_linkage_matrix = new_linkage_matrix
            
        else:
            total_linkage_matrix[where_col + 4][where.index[0]] = data_df.columns.get_loc(sub_cluster.index[0])    
            

    logger.debug(new_linkage_matrix)
    
    logger.debug("data_df.columns")
    logger.debug(data_df.columns)
    
    return new_linkage_matrix

def col_4_5_updating_1_2(new_linkage_matrix):
    #a strange way to get all the values that are not null
    no_nan_4 = new_linkage_matrix.loc[new_linkage_matrix[4] > -1]
    new_0 = pd.DataFrame(no_nan_4[4])
    new_0.columns = [0]

    #a strange way to get all the values that are not null
    no_nan_5 = new_linkage_matrix.loc[new_linkage_matrix[5] > -1]
    new_1 = pd.DataFrame(no_nan_5[5])
    new_1.columns = [1]

    new_linkage_matrix.update(new_0)
    new_linkage_matrix.update(new_1)

    new_linkage_matrix = new_linkage_matrix.drop(4, axis = 1)
    new_linkage_matrix = new_linkage_matrix.drop(5, axis = 1)
    
    return new_linkage_matrix

def fix_linkage_matrix(df_sub_and_super_linkage_matrix):
    #put the non NaN values from 4 and 5 into 1 and 2
    #fix counts column
    df_sub_and_super_linkage_matrix = col_4_5_updating_1_2(df_sub_and_super_linkage_matrix)

    df_sub_and_super_linkage_matrix = get_child_counts(df_sub_and_super_linkage_matrix)

    return df_sub_and_super_linkage_matrix

#from https://stackoverflow.com/questions/28222179/save-dendrogram-to-newick-format/31878514#31878514 
def getNewick(node, newick, parentdist, leaf_names):
    if node.is_leaf():
        return "%s:%.2f%s" % (leaf_names[node.id], parentdist - node.dist, newick)
    else:
        if len(newick) > 0:
            newick = "):%.2f%s" % (parentdist - node.dist, newick)
        else:
            newick = ");"
        newick = getNewick(node.get_left(), newick, node.dist, leaf_names)
        newick = getNewick(node.get_right(), ",%s" % (newick), node.dist, leaf_names)
        newick = "(%s" % (newick)
        return newick

def create_dendrogram_from_df(row_or_col, data_df):
    #calling above methods in some order that it creates the dendrogram
    AffinityProp = run_AffinityProp(row_or_col, data_df)

    if row_or_col == "row":
        data_df = data_df.transpose()
        col_labels = AffinityProp.labels_
        row_labels = range(0, (len(data_df.index)))
        
        
    if row_or_col == "col":
        
        col_labels = AffinityProp.labels_
        row_labels = range(0, (len(data_df.index)))


    sorted_df, label_df = sort_by_label_list(data_df, row_labels, col_labels)

    cluster_centers = get_cluster_centers(data_df, AffinityProp.cluster_centers_indices_)

    super_linkage_matrix, super_r_dict = super_cluster(cluster_centers)

    super_dendro_labels_index = change_labels(super_r_dict["leaves"])
    
    logger.debug("(label_df): {}".format((label_df)))

    label_df = reorder_super_cluster(label_df, super_dendro_labels_index)

    super_linkage_matrix = update_super_matrix(super_linkage_matrix, super_dendro_labels_index)

    num_col = len(data_df.columns)
    num_row = len(data_df.index)

    sub_and_super_linkage_matrix = loop_through_clusters(super_linkage_matrix, label_df, num_row, super_dendro_labels_index, data_df) 
    
    sub_and_super_linkage_matrix = fix_linkage_matrix(sub_and_super_linkage_matrix)

    r_dict2 = run_scipy_cluster_dendrogram(sub_and_super_linkage_matrix)

    df_r_dict2_labels = r_dict2["leaves"]

    super_and_sub_dendro_labels_index = change_labels(df_r_dict2_labels)

    sas_sorted_df, sas_label_df = sort_by_label_list(data_df, row_labels, super_and_sub_dendro_labels_index)

    tree = scipy.cluster.hierarchy.to_tree(sub_and_super_linkage_matrix,False)
    newick = getNewick(tree, "", tree.dist, r_dict2["leaves"])

    if row_or_col == "row":
        sas_sorted_df = sas_sorted_df.transpose()


    return newick, sas_sorted_df, super_and_sub_dendro_labels_index

def create_col_and_row_template(isstring, field):
    col_and_row_template = {
            "squished": False,
            "inlineTooltip": False,
            "tooltip": True,
            "highlightMatchingValues": False,
            "colorBarSize": 12,
            "stackedBar": False,
            "display": [
                "text"
            ],
            "selectionColor": "rgb(182,213,253)",
            "colorByField": None,
            "fontField": None,
            "barColor": "#bdbdbd",
            "barSize": 40,
            "autoscaleAlways": False,
            "minMaxReversed": False,
            "field": field,
            "size": {
                "height": 10
            }
        }
    if isstring:
        col_and_row_template["maxTextWidth"] = 0
        
    return col_and_row_template

def create_col_and_row_metadata_template(isstring, field, array):
    col_and_row_metadata_template = {
        "properties": {"morpheus.dataType": "number"},
            "name": field,
            "array": array
          }
    if isstring:
        col_and_row_metadata_template["properties"]["morpheus.dataType"] = "string"
        
    return col_and_row_metadata_template

def prepare_metadata(gctoo, data_df, super_and_sub_dendro_labels_index, row_labels, num_row, num_col):
    row_metadata = gctoo.row_metadata_df

    flipped_row_labels = [len(row_labels) - x for x in row_labels]

    flip_row_metadata_names_df = pd.DataFrame(flipped_row_labels)

    flip_row_metadata_names_df.index = data_df.index

    row_metadata = row_metadata.join(flip_row_metadata_names_df)

    logger.debug("row_metadata: {}".format(row_metadata))

    sorted_row_metadata_df = row_metadata.sort_values(0)

    sorted_row_metadata_df.drop(0, axis = 1, inplace = True)

    col_metadata = gctoo.col_metadata_df
    flipped_super_and_sub_dendro_labels_index = [len(super_and_sub_dendro_labels_index) - x for x in super_and_sub_dendro_labels_index]

    flip_col_metadata_names_df = pd.DataFrame(flipped_super_and_sub_dendro_labels_index)
    flip_col_metadata_names_df.index = data_df.columns

    col_metadata[num_col] = flip_col_metadata_names_df

    sorted_col_metadata_df = col_metadata.sort_values(num_col)

    sorted_col_metadata_df.drop(num_col, axis = 1, inplace = True)

    logger.debug("sorted_col_metadata_df: {}".format(sorted_col_metadata_df))

    none_sorted_col_metadata_df = sorted_col_metadata_df.where(sorted_col_metadata_df.notnull(), None)

    logger.debug("none_sorted_col_metadata_df: {}".format(none_sorted_col_metadata_df))

    return none_sorted_col_metadata_df, sorted_row_metadata_df

def create_json(template_path, output_path, sas_sorted_df, col_metadata_df, row_metadata_df, col_newick, row_newick):
    final_sorted_df_numpy =  sas_sorted_df.to_numpy()
    flipped = numpy.flip(final_sorted_df_numpy)

    template_file = open(template_path, "r")
    json_object = json.load(template_file)
    template_file.close()

    json_object["columnDendrogram"] = col_newick
    json_object["rowDendrogram"] = row_newick

    dataset = json_object["dataset"]

    dataset["rows"] = len(flipped)
    dataset["columns"] = len(flipped[0])

    dataset["seriesArrays"] = [flipped.tolist()]

    #reset columns and rows only necessary for now will change template so it is not later
    json_object["columns"] = []
    json_object["rows"] = []

    json_object["columns"].append(create_col_and_row_template(True, "cid"))
    json_object["rows"].append(create_col_and_row_template(True, "rid"))


    dataset["rowMetadataModel"]["vectors"] = []
    dataset["columnMetadataModel"]["vectors"] = []


    sas_flipped_index = numpy.flip(list(sas_sorted_df.index))
    sas_flipped_col = numpy.flip(list(sas_sorted_df.columns))
                                                                                                        
    dataset["rowMetadataModel"]["vectors"].append(create_col_and_row_metadata_template(True, "rid", sas_flipped_index.tolist())) 
    dataset["columnMetadataModel"]["vectors"].append(create_col_and_row_metadata_template(True, "cid", sas_flipped_col.tolist()))


    for col in col_metadata_df.iteritems():
        json_object["columns"].append(create_col_and_row_template(True, col[0]))
        dataset["columnMetadataModel"]["vectors"].append(create_col_and_row_metadata_template(True, col[0], col[1].to_list())) 

    for row in row_metadata_df.iteritems(): 
        json_object["rows"].append(create_col_and_row_template(True, row[0]))
        dataset["rowMetadataModel"]["vectors"].append(create_col_and_row_metadata_template(True, row[0], row[1].to_list()))

    output_file = open(output_path, "w")
    json.dump(json_object, output_file)
    output_file.close()
    return output_path

def main(args):
    #gctx_path = os.path.join("2020_Q3_Achilles_CCLE_expression_r19144x1305.gctx")
    #template_path = os.path.join("template.json")
    #output_path = os.path.join("super_and_sub_file.json")


    gctx_path = args.gctx_path
    template_path = args.template_path
    output_path = args.output_path


    data_df_rows_chopped, gctoo = load_data(args.num_row, gctx_path)
    
    num_col = len(data_df_rows_chopped.columns)
    num_row = len(data_df_rows_chopped.index)

    if args.row_or_col == "col":
        col_newick, sas_sorted_df, col_super_and_sub_dendro_labels_index = create_dendrogram_from_df("col", data_df_rows_chopped)
        row_super_and_sub_dendro_labels_index = list(range(0, (len(data_df_rows_chopped.index))))
        row_newick = None

    elif args.row_or_col == "row":
        row_newick, sas_sorted_df, row_super_and_sub_dendro_labels_index = create_dendrogram_from_df("row", sas_sorted_df)
        col_super_and_sub_dendro_labels_index = list(range(0, (len(data_df_rows_chopped.columns))))
        col_newick = None

    elif args.row_or_col == "both":
        col_newick, sas_sorted_df, col_super_and_sub_dendro_labels_index = create_dendrogram_from_df("col", data_df_rows_chopped)
        row_newick, sas_sorted_df, row_super_and_sub_dendro_labels_index = create_dendrogram_from_df("row", sas_sorted_df)
    
    col_metadata_df, row_metadata_df = prepare_metadata(gctoo, data_df_rows_chopped, col_super_and_sub_dendro_labels_index,  row_super_and_sub_dendro_labels_index, num_row, num_col)

    create_json(template_path, output_path, sas_sorted_df, col_metadata_df, row_metadata_df, col_newick, row_newick)

    return output_path


if __name__ == "__main__":
    args = build_parser().parse_args(sys.argv[1:])

    setup_logger.setup(verbose=args.verbose)

    logger.debug("args:  {}".format(args))

    main(args)
