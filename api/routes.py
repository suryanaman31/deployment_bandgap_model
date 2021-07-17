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
    temp = ""
    el = []
    val = []
    #Accessing the atomic numbers

    datno = {}
    norm_data = pd.read_excel("api/element_properties.xlsx", sheet_name = "Element_prop")  
    o1 = open("api/ele_brac_out.txt", "w")
    o2 = open("api/ele_out.txt", "w")

    col = ["At no.","At wt.","At Rad","Cov Rad","Ion Rad","No of val e-","s e-","p e-","d e-","outer shell e-","first IE","polarizability","MP","BP","density","specific heat","heat fusion","heat vap","ther cond"]
    col_name = ""
    for i in col:
        col_name = col_name + i+"_"+ "sum" + ";" +  i+"_"+ "wt_avg" + ";" +  i+"_"+ "maximum" + ";" +  i+"_"+ "minimum" + ";" 
    line1 =  "Compound" + ";" + "Number of Elements" + ";" + "Elements+Coeff" + ";" + col_name + "\n"
    o2.write(line1)
    file = request.files.get("input_file")
    with open('compounds_for_prediction.txt', 'wb') as f:
        f.write(file.getbuffer())
    with open('compounds_for_prediction.txt') as o:
        for line in o:
            string=line.split("\n")[0]
            nflag=0
            j=0
            el = []
            val = []
            temp = ""
            while j < len(string):
                if ord(string[j]) == 41 or ord(string[j]) == 40 or ord(string[j]) == 44:
                    o1.write(string+"\n")
                    #o1.close()
                    nflag=1
                    break
                j+=1
            if nflag==0:
                j=0
                p = 0
                c=0
                while j < len(string):
                    if ord(string[j]) >= 65 and ord(string[j]) <= 90:
                        c = 0
                    elif ord(string[j]) >= 97 and  ord(string[j]) <=122:
                        c = 1
                    elif (ord(string[j]) >= 48 and ord(string[j]) <=57) or ord(string[j]) == 46:
                        c = 2 

                    if c == 0 and (p == 0 or p == 1):
                        if temp != "":
                            el.append(temp)
                            val.append(1)
                        temp=string[j]
                        p = c

                    elif c == 0 and p == 2:
                        val.append(temp)
                        temp = string[j]
                        p=c

                    elif c==1 and p==0:
                        temp=temp+string[j]
                        #temp = string[j]
                        p=c
                    elif c==2 and (p==1 or p==0):
                        el.append(temp)
                        temp=string[j]
                        p=c
                    elif c==2 and p==2:
                        temp=temp+string[j]
                    j+=1
                if c==0 or c==1:
                    val.append(1)
                    el.append(temp)
                else:
                    val.append(temp)
                a = []
                for k in range(0,  len(el)):
                    a.append([])
                    a[k].append(el[k])
                    a[k].append(val[k])
                b = ''
                for j in range(1,20):      #j will vary so that with each j our dictionary contains a different property
                    for i in range(0,81):
                            props = float(norm_data.iloc[i,j])  #property as a value
                            elem = str(norm_data.iloc[i,0])    #element name as a key
                            datno[elem] = props
                    maxim = -1       #defining initial values of the descriptors. Since normalized values are in range [0,1] 
                    minim = 15000
                    mol = 0
                    avg_den = 0
                    avg_num = 0
                    wt_avg = 0
                    for e in range(0,  len(el)):        #starting loop over each element and coeff of each compound to calculate descriptors 
                        mol += datno[el[e]]
                        avg_den += float(val[e])
                        avg_num += (datno[el[e]]*float(val[e]))
                        if(datno[el[e]] > maxim):
                            maxim = datno[el[e]]
                        if(datno[el[e]] < minim):
                            minim = datno[el[e]]
                        wt_avg = (avg_num)/(avg_den)
                    b = b + str(mol)+';'+str(wt_avg)+';'+str(maxim)+';'+str(minim)+';'
                var = string + ';' + str(len(a)) + ';' + str(a) + ';' + b + "\n"
                o2.write(var)
        o2.close()

    o1.close()

    data_infer = pd.read_csv("api/ele_out.txt", sep = ";")
    compounds_infer = data_infer['Compound'].tolist()
    p=[]
    for i in range(3,79):
        p.append(i)
    X_infer = data_infer.iloc[:,p]
    from sklearn.preprocessing import MinMaxScaler
    scaler = MinMaxScaler()
    X_infer = scaler.fit_transform(X_infer)
    y_infer_pred = bg_model.predict(X_infer)
    bandgap_dict = dict(zip(compounds_infer, y_infer_pred))
    print("The predicted values of Eg are:\n")
    return bandgap_dict