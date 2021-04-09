from data.ApiServiceEstacionMet import ApiServiceEstacionMet 
from model.ModelVarMeTereologica import meteorologicalData as DatMet

import sys
import requests
import json
import urllib
import json

if __name__ == "__main__":
    ApiService = ApiServiceEstacionMet()
    response = ApiService.request_station()
    print(response["credit"])
    datmet = DatMet.from_dict(response)
    print(datmet)

