# modelo de la api que se consume para optener variables meteorologicas
from dataclasses import dataclass
from typing import Any, TypeVar, Type, cast

@dataclass
class meteorologicalData:
    #did: str
    date: str
    hour: str
    EToD: float
    RainD: float
    TeMax: float
    TeMin: float

    @staticmethod
    def from_dict(obj: Any) -> 'meteorologicalData':
        date=str( obj["observation_time"]).split(',')[0].split("on")[1]
        hour=str( obj["observation_time"]).split(',')[1]
        observation_davis= obj["davis_current_observation"]
        EToD=float(observation_davis["et_day"])
        RainD=float(observation_davis["rain_day_in"])
        TeMax=round((float(observation_davis["temp_day_high_f"])-32) * (5/9),2)
        TeMin=round((float(observation_davis["temp_day_low_f"])-32) * (5/9),2) 
        return meteorologicalData( date,hour ,EToD,RainD,TeMax,TeMin)
