import sys
import pandas as pd
import pickle

from sklearn.ensemble import AdaBoostClassifier

from analysis import *

# Loading the features into a dataframe
def create_data_frame(list_of_list):
    df = pd.DataFrame(list_of_list)
    columns = []
    for i in range(len(list_of_list[0])):
        columns.append('f'+str(i+1))
    df.columns = columns
    return df

# Reading the data and extracting the features
def read_data(segmentation_output_path, prefix_morpheme, suffix_morpheme):
    table = []
    dict = get_affix_features(segmentation_output_path, prefix_morpheme, suffix_morpheme)
    features = []
    for key1 in dict:
        for key2 in dict[key1]:
            features.append(dict[key1][key2])
    features.append(0)
    table.append(features)
    df = create_data_frame(table)
    return df

# Parameters
classification_model = sys.argv[1]
segmentation_output_path = sys.argv[2]
prefix_morpheme = sys.argv[3]
suffix_morpheme = sys.argv[4]

# Extract the features.
test_df = read_data(segmentation_output_path, prefix_morpheme, suffix_morpheme)
x_test = test_df.iloc[:, :-1].values
y_test = test_df['f' + str(len(x_test[0]) + 1)]
AB_model = None

# Run classification.
with open(classification_model, 'rb') as fin:
    AB_model = pickle.load(fin)
AB_prediction = AB_model.predict(x_test)
print('Standard' if AB_prediction[0] == 0 else 'Cascaded')
