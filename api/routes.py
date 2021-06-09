from flask import jsonify, request
from flasgger.utils import  swag_from
import os
from flask import Blueprint
import pandas as pd
import numpy as np
import pickle
import pathlib

api_routes = Blueprint('routes_api',__name__)

swagger_config_dir = str(pathlib.Path(__file__).resolve().parent.parent)
pickle_in = open("model.pkl","rb")
bg_model=pickle.load(pickle_in)

@api_routes.route('/predict_file',methods=["POST"])
@swag_from(os.path.join(swagger_config_dir, 'swagger_configs', 'swagger_config_1.yml'))
def predict_bandgap_file():
    data_infer=pd.read_csv(request.files.get("input_file"))
    compounds_infer = data_infer['composition'].tolist()
    p=[]
    for i in range(6,82):
        p.append(i)
    X_infer = data_infer.iloc[:,p]
    y_infer = data_infer.iloc[1]
    y_infer_pred = bg_model.predict(X_infer)
    bandgap_dict = dict(zip(compounds_infer, y_infer_pred))
    print("The predicted values of Eg are:\n")
    return bandgap_dict
