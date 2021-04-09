# modelo de la api que se consume para optener variables meteorologicas
from dataclasses import dataclass
from typing import Any, TypeVar, Type, cast

@dataclass
class meteorologicalData:
    #did: str
    fecha: str
    hora: str
    EtoD: float
    RainD: float
    Temax: float
    TeMin: float

    @staticmethod
    def from_dict(obj: Any) -> 'meteorologicalData':
        fecha=str( obj["observation_time"]).split(',')[0].split("on")[1]
        hora=str( obj["observation_time"]).split(',')[1]
        observation_davis= obj["davis_current_observation"]
        EToD=str(observation_davis["et_day"])
        RainD=str(observation_davis["rain_day_in"])
        TeMax=round((float(observation_davis["temp_day_high_f"])-32) * (5/9),2)
        TeMin=round((float(observation_davis["temp_day_low_f"])-32) * (5/9),2) 
        return meteorologicalData( fecha,hora ,EToD,RainD,TeMax,TeMin)
