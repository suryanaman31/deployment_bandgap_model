import pandas as pd
import numpy as np
from sklearn.metrics import r2_score
from sklearn.metrics import mean_absolute_error
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split
from sklearn.ensemble import ExtraTreesRegressor
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import cross_val_score
import joblib
import pickle

train_data = pd.read_csv("train.csv")

p=[]
for i in range(3,79):
    p.append(i)
X = train_data.iloc[:, p]  
y = train_data.iloc[:, 79]

model = ExtraTreesRegressor(bootstrap=False, ccp_alpha=0.0, criterion='mse',
                    max_depth=None, max_features='auto', max_leaf_nodes=None,
                    max_samples=None, min_impurity_decrease=0.0,
                    min_impurity_split=None, min_samples_leaf=1,
                    min_samples_split=2, min_weight_fraction_leaf=0.0,
                    n_estimators=100, n_jobs=-1, oob_score=False,
                    random_state=123, verbose=0, warm_start=False)

scaler = MinMaxScaler()
X = scaler.fit_transform(X)
scaler_filename = "scaler.save"
joblib.dump(scaler, scaler_filename) 
model.fit(X, y)
pickle_out = open("model.pkl","wb")
pickle.dump(model, pickle_out)
pickle_out.close()
