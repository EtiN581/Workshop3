import pickle
import numpy as np
from flask import Flask, request, render_template
import json

modelNames = ['linearRegression', 'randomForest', 'XGBClassifier']


models = [pickle.load(open(f"./models/{name}.pkl", "rb")) for name in modelNames]
modelsData = json.load(open("./models/models.json", "r"))

def resetModelsData():
    inv = [1/modelsData[name]['MSE'] for name in modelNames]
    total = sum(inv) #to normalize
    for i,name in enumerate(modelNames):
        modelsData[name]['weight']=inv[i]/total
        modelsData[name]['deposit']=1000
    json.dump(modelsData, open('./models/models.json', 'w'), indent=4)

def normalizeWeights():
    s=sum(modelsData[name]['weight'] for name in modelNames)
    for name in modelNames:
        modelsData[name]['weight']=min(max(modelsData[name]['weight']/s, 0.1), 0.9) #to normalize and get 0.1 < new weight < 0.9
    
def updateModelsData(predictions, consensus):
    for i, name in enumerate(modelNames):
        if predictions[i]==consensus:
            modelsData[name]['weight']*=1.1
            modelsData[name]['deposit']+=90
        else:
            modelsData[name]['weight']*=0.9
            modelsData[name]['deposit']-=100
    normalizeWeights()
    json.dump(modelsData, open('./models/models.json', 'w'), indent=4) #save model

def predict(data):
    try:
        predictions = [round(models[i].predict(data)[0]) for i in range(len(models))] #round() since linear regression gives float predictions
        concensus = round(sum(modelsData[name]['weight']* predictions[i] for i, name in enumerate(modelNames))) #round() to prevent round error on weights (sum weights!=1)
        updateModelsData(predictions, concensus)
        if concensus==1: 
            return "Survived"
        else:
            return "Died"
    except:
        return -1
    

app = Flask(__name__)
#resetModelsData() #to set the weights based on their MSE and set the deposit to 1000

@app.route('/')
def hello_world():
    return render_template('index.html')

@app.route('/predict', methods=['GET'])
def get_predict():
    args = request.args.to_dict()
    pclass = int(args['pclass'])
    sex = int(args['sex'])
    age = float(args['age'])
    sibsp = int(args['sibsp'])
    parch = int(args['parch'])
    fare = float(args['fare'])
    alone = int(args['alone'])
    port = args['port']
    l = [pclass, sex, age, sibsp, parch, fare, alone]
    if port=='C':
        l.extend([1,0,0])
    elif port=='Q':
        l.extend([0,1,0])
    else:
        l.extend([0,0,1])
    data = np.array(l).reshape(1,-1)
    pred = predict(data)
    return {"prediction" : pred}

app.run(host="0.0.0.0", port=8080)

#to use ngrok :
#command : ngrok http http://localhost:8080
#example url : https://8595-46-193-4-133.ngrok-free.app