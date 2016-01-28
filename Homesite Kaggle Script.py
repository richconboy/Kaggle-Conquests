# -*- coding: utf-8 -*-
"""
Homesite Kaggle Compeition
Rich conboy
"""

#%% Import Packages
import pandas as pd
from sklearn import preprocessing
from sklearn import cross_validation
from sklearn import metrics
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier

#%% Read Data Sets
training_data = pd.read_csv('C:/Users/Rich/OneDrive/Documents/Independent Projects/Kaggle/Homesite/train.csv', index_col = 'QuoteNumber')
test_data = pd.read_csv('C:/Users/Rich/OneDrive/Documents/Independent Projects/Kaggle/Homesite/test.csv', index_col = 'QuoteNumber')

#%% Fix Dates
def fix_dates(df):
    df['Date'] = pd.to_datetime(pd.Series(df['Original_Quote_Date']))
    df = df.drop('Original_Quote_Date', axis=1)
    
    df['Year'] = df['Date'].dt.year
    df['Month'] = df['Date'].dt.month
    df['Weekday'] = df['Date'].dt.dayofweek
    
    df = df.drop('Date', axis=1)
    return df
    
training_data = fix_dates(training_data)
test_data = fix_dates(test_data)

#%% Convert Categorical Variables to Numeric
def convert_to_num(df):
    for f in df.columns:
        if df[f].dtype=='object':
            lbl = preprocessing.LabelEncoder()
            lbl.fit(list(df[f].values))
            df[f] = lbl.transform(list(df[f].values))
    return df

training_data = convert_to_num(training_data)
test_data = convert_to_num(test_data)

#%% Fill in Blanks
def fill_blanks(df):
    df = df.fillna(-1)
    return df
    
training_data = fill_blanks(training_data)
test_data = fill_blanks(test_data)
        
#%% Split into Feature Matrix and Target Variable Array
y = training_data['QuoteConversion_Flag']
X = training_data.drop('QuoteConversion_Flag', axis=1)

#%% Split Training Data Into Training and Validation
X_train, X_validation, y_train, y_validation = cross_validation.train_test_split(X, y, test_size = 0.25, random_state = 5)

#%% Logistic Regression - All features

#Fit the Model
logreg = LogisticRegression()
logreg.fit(X_train, y_train)

#Make Predictions (Validation Set)
logreg_pred = logreg.predict(X_validation)
print 'Log Reg Classification Accuracy: ' + str(metrics.accuracy_score(y_validation, logreg_pred))
logreg_pred_probs = logreg.predict_proba(X_validation)
print 'Log Reg Area Under the Curve: ' + str(metrics.roc_auc_score(y_validation, logreg_pred_probs[:,1]))

#%% Random Forest - All features

#Fit the Model
forest = RandomForestClassifier()
forest.fit(X_train, y_train)

#Make Predictions (Validation Set)
forest_pred = forest.predict(X_validation)
print 'Forest Classification Accuracy: ' + str(metrics.accuracy_score(y_validation, forest_pred))
forest_pred_probs = forest.predict_proba(X_validation)
print 'Forest Area Under the Curve: ' + str(metrics.roc_auc_score(y_validation, forest_pred_probs[:,1]))
