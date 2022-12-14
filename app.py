from fastapi import FastAPI, File, UploadFile
import requests
import shutil
from pathlib import Path
from fastapi import UploadFile
import pandas as pd
import json
from pydantic import BaseModel
from starlette.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware




path="https://random-data-api.com/api/cannabis/random_cannabis?size=5"
app = FastAPI()

#SepUp CORS
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


informacion=[]

#Basic model for the client
class Person:
    sn: str
    client: str
    olt:str
    olt_id:str
    board:str
    port:str
    zone_name: str
    zone_id: str
    address :str
    odb_name: str
    catv:str
    administrative_status:str
    signal:str
    onu_signal_1310 :str
    onu_signal_1490 :str
@app.get("/")
async def root():
    return {"message": "Welcome Servicable's API"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}

@app.get("/api")
async def getAPI():
    response =requests.get(path)
    if response.status_code:
        response=response.json()
        for data in response:
            informacion.append(data)
        return informacion


@app.get("/infoBySN/{sn}")
async  def getInfo(sn):
    url = "https://servicablegz.smartolt.com/api/onu/get_onus_details_by_sn/"+sn
    payload = {}
    headers = {'X-Token': 'ae287af051d349a68db0aec4b11cc933','Cookie': 'ci_session=cqh06bjsvo4iqumkin218e95rt57qku8'}
    try:
        response = requests.request("GET", url, headers=headers, data=payload)
        data = response.json()
        p1 = Person()

        if data is None:
            return {"Message": "SN not found"}
        else:
            p1.zone_id = data['onus'][0]['zone_id']
            p1.zone_name = data['onus'][0]['zone_name']
            p1.odb_name = data['onus'][0]['odb_name']
            p1.sn = data['onus'][0]['sn']
            p1.client = data['onus'][0]['name']
            p1.address = data['onus'][0]['address']
            print(data['onus'][0]['olt_id'])
            print(p1.__dict__)
            return p1
    except:
        return {"Message":"Invalid SN try again"}

@app.post("/uploadFile")
async  def save_file(file: UploadFile = File(...)):
    with open(file.filename,"wb") as buffer:
        shutil.copyfileobj(file.file,buffer)
    df = pd.read_csv(file.filename)
    print(df.head())

    informe = pd.DataFrame(columns=['sn', 'name', 'olt_name','olt_id', 'board', 'port', 'zone_name', 'zone_id',
                                    'address', 'odb_name', 'catv', 'administrative_status', 'onu_signal',
                                    'onu_signal_1310', 'onu_signal_1490'])




    #for index, i in enumerate(df['SN']):
    for i in range(15):
        print(df['SN'][i])

        #print("este es el cliente",p1.__dict__)

        payload = {}
        headers = {'X-Token': 'ae287af051d349a68db0aec4b11cc933',
                   'Cookie': 'ci_session=cqh06bjsvo4iqumkin218e95rt57qku8'}
        url = "https://servicablegz.smartolt.com/api/onu/get_onus_details_by_sn/" + df['SN'][i]

        try:
            # Response to get onu Information
            response = requests.request("GET", url, headers=headers, data=payload)
            data = response.json()

            if data is None:
                return {"Message": "SN not found"}
            else:
                p1 = Person()
                p1.sn = data['onus'][0]['sn']
                p1.client = data['onus'][0]['name']
                p1.olt = data['onus'][0]['olt_name']
                p1.olt_id= data['onus'][0]['olt_id']
                p1.board = data['onus'][0]['board']
                p1.port = data['onus'][0]['port']
                p1.zone_name = data['onus'][0]['zone_name']
                p1.zone_id = data['onus'][0]['zone_id']
                p1.address = data['onus'][0]['address']
                p1.odb_name = data['onus'][0]['odb_name']
                p1.catv = data['onus'][0]['catv']
                p1.administrative_status = data['onus'][0]['administrative_status']
                # Assignment of values for onu signals
                # p1.signal=data_signals['onu_signal']
                # p1.onu_signal_1310=data_signals['onu_signal_1310']
                # p1.onu_signal_1490=data_signals['onu_signal_1490']
                #print(p1.__dict__)
                # return p1.__dict__

        except:
            return {"Message": "Invalid SN ", "Check ": "algo"}

        signals = onu_Signal(df['SN'][i])

        print(signals[0], i)
        p1.signal=signals[0]
        p1.onu_signal_1310=signals[1]
        p1.onu_signal_1490=signals[2]

        print(p1.__dict__)

        informe = informe.append({'sn': p1.sn, 'name': p1.client, 'olt_name': p1.olt, 'olt_id':p1.olt_id , 'board': p1.board,
                                  'port': p1.port, 'zone_name': p1.zone_name, 'zone_id': p1.zone_id,
                                  'address': p1.address, 'odb_name': p1.odb_name, 'catv': p1.catv,
                                  'administrative_status': p1.administrative_status,
                                  'onu_signal': p1.signal, 'onu_signal_1310': p1.onu_signal_1310,
                                  'onu_signal_1490': p1.onu_signal_1490}, ignore_index=True)

    print("------------------------------------")
    print(informe.head())
    print("------------------------------------")

    informe.to_csv("Informe.csv",index=False)

    return FileResponse("Informe.csv", media_type='application/octet-stream',filename="Informe.csv")


def onu_Signal(sn):
    payload = {}
    headers = {'X-Token': 'ae287af051d349a68db0aec4b11cc933',
               'Cookie': 'ci_session=cqh06bjsvo4iqumkin218e95rt57qku8'}
    url = "https://servicablegz.smartolt.com/api/onu/get_onu_signal/"+sn

        # Response to get onu Signals
    response_signals = requests.request("GET", url, headers=headers, data=payload)
    data_signals = response_signals.json()
    print(data_signals)

    if(data_signals['status']==False):

        print("************INGRESO AL IF NEGATIVO**********")
        signalf="offline"
        onu_signal_1310f="offline"
        onu_signal_1490f="offline"

        return signalf,onu_signal_1310f,onu_signal_1490f
    else:
        print("************INGRESO AL IF POSITIVO**********")
        signal=data_signals['onu_signal']
        onu_signal_1310=data_signals['onu_signal_1310']
        onu_signal_1490=data_signals['onu_signal_1490']


        return signal,onu_signal_1310,onu_signal_1490



@app.get("/download")
async  def getInfo():
    return FileResponse("requirements.txt", media_type='application/octet-stream',filename="requirements.txt")
