import matplotlib
matplotlib.use('Agg')
import numpy as np
import skfuzzy.control as ctrl
import skfuzzy as fuzz

def Fuzzy_Metod_Presc(Moisture_A,Temperature_A,Radiation_A):
    print("init")
    Moisture = ctrl.Antecedent(np.arange(0, 52.56, 1), 'Moisture')  #  (np.arange(0, 60, 1), 'Moisture')
    Temperature = ctrl.Antecedent(np.arange(0, 25, 1), 'Temperature')
    Radiation = ctrl.Antecedent(np.arange(0, 3500, 1), 'Radiation')
    IrrTime = ctrl.Consequent(np.arange(0, 32, 1), 'IrrTime')

    Moisture['LowM'] = fuzz.trapmf(Moisture.universe, [-20, -20, 15.0, 30.0])   # [-20, -20, 15.92, 36.60])
    Moisture['MediumM'] = fuzz.trimf(Moisture.universe, [15, 30, 45])    # [15.92, 36.60, 52.56])
    Moisture['HighM'] = fuzz.trapmf(Moisture.universe, [30, 45, 65, 65])    # [36.60, 52.56, 65, 65])

    Temperature['LowT'] = fuzz.trapmf(Temperature.universe, [- 2, -2, 10, 15])
    Temperature['MediumT'] = fuzz.trimf(Temperature.universe, [10, 15, 20])
    Temperature['HighT'] = fuzz.trapmf(Temperature.universe, [15, 20, 25, 25])

    Radiation['LowR'] = fuzz.trapmf(Radiation.universe, [-10, -10, 10, 200])
    Radiation['MediumR'] = fuzz.trapmf(Radiation.universe, [10, 200, 1000, 1400])
    Radiation['HighR'] = fuzz.trapmf(Radiation.universe, [1000, 1400, 3550, 3550])

    IrrTime['Nothing'] = fuzz.trapmf(IrrTime.universe, [-20, -20, 0, 8])
    IrrTime['VeryLittle'] = fuzz.trimf(IrrTime.universe, [0, 8, 16])
    IrrTime['Little'] = fuzz.trimf(IrrTime.universe, [8, 16, 24])
    IrrTime['Long'] = fuzz.trimf(IrrTime.universe, [16, 24, 32])
    IrrTime['VeryLong'] = fuzz.trapmf(IrrTime.universe, [24, 32, 40, 40])

    rule1 = ctrl.Rule(Moisture['LowM'] & Temperature['LowT'] & Radiation['LowR'], IrrTime['VeryLong'])
    rule2 = ctrl.Rule(Moisture['LowM'] & Temperature['LowT'] & Radiation['MediumR'], IrrTime['VeryLong'])
    rule3 = ctrl.Rule(Moisture['LowM'] & Temperature['LowT'] & Radiation['HighR'], IrrTime['VeryLong'])
    rule4 = ctrl.Rule(Moisture['LowM'] & Temperature['MediumT'] & Radiation['LowR'], IrrTime['Long'])
    rule5 = ctrl.Rule(Moisture['LowM'] & Temperature['MediumT'] & Radiation['MediumR'], IrrTime['Long'])
    rule6 = ctrl.Rule(Moisture['LowM'] & Temperature['MediumT'] & Radiation['HighR'], IrrTime['Little'])
    rule7 = ctrl.Rule(Moisture['LowM'] & Temperature['HighT'] & Radiation['LowR'], IrrTime['VeryLong'])
    rule8 = ctrl.Rule(Moisture['LowM'] & Temperature['HighT'] & Radiation['MediumR'], IrrTime['VeryLittle'])
    rule9 = ctrl.Rule(Moisture['LowM'] & Temperature['HighT'] & Radiation['HighR'], IrrTime['Nothing'])
    rule10 = ctrl.Rule(Moisture['MediumM'] & Temperature['LowT'] & Radiation['LowR'], IrrTime['Little'])
    rule11 = ctrl.Rule(Moisture['MediumM'] & Temperature['LowT'] & Radiation['MediumR'], IrrTime['Little'])
    rule12 = ctrl.Rule(Moisture['MediumM'] & Temperature['LowT'] & Radiation['HighR'], IrrTime['Little'])
    rule13 = ctrl.Rule(Moisture['MediumM'] & Temperature['MediumT'] & Radiation['LowR'], IrrTime['Little'])
    rule14 = ctrl.Rule(Moisture['MediumM'] & Temperature['MediumT'] & Radiation['MediumR'], IrrTime['Little'])
    rule15 = ctrl.Rule(Moisture['MediumM'] & Temperature['MediumT'] & Radiation['HighR'], IrrTime['VeryLittle'])
    rule16 = ctrl.Rule(Moisture['MediumM'] & Temperature['HighT'] & Radiation['LowR'], IrrTime['Long'])
    rule17 = ctrl.Rule(Moisture['MediumM'] & Temperature['HighT'] & Radiation['MediumR'], IrrTime['VeryLittle'])
    rule18 = ctrl.Rule(Moisture['MediumM'] & Temperature['HighT'] & Radiation['HighR'], IrrTime['Nothing'])
    rule19 = ctrl.Rule(Moisture['HighM'] & Temperature['LowT'] & Radiation['LowR'], IrrTime['Nothing'])
    rule20 = ctrl.Rule(Moisture['HighM'] & Temperature['LowT'] & Radiation['MediumR'], IrrTime['Nothing'])
    rule21 = ctrl.Rule(Moisture['HighM'] & Temperature['LowT'] & Radiation['HighR'], IrrTime['Nothing'])
    rule22 = ctrl.Rule(Moisture['HighM'] & Temperature['MediumT'] & Radiation['LowR'], IrrTime['Nothing'])
    rule23 = ctrl.Rule(Moisture['HighM'] & Temperature['MediumT'] & Radiation['MediumR'], IrrTime['Nothing'])
    rule24 = ctrl.Rule(Moisture['HighM'] & Temperature['MediumT'] & Radiation['HighR'], IrrTime['Nothing'])
    rule25 = ctrl.Rule(Moisture['HighM'] & Temperature['HighT'] & Radiation['LowR'], IrrTime['Nothing'])
    rule26 = ctrl.Rule(Moisture['HighM'] & Temperature['HighT'] & Radiation['MediumR'], IrrTime['Nothing'])
    rule27 = ctrl.Rule(Moisture['HighM'] & Temperature['HighT'] & Radiation['HighR'], IrrTime['Nothing'])

    IrrTimeping_ctrl = ctrl.ControlSystem([rule1, rule2, rule3, rule4, rule5, rule6, rule7, rule8, rule9, rule10, rule11, rule12, rule13, rule14, rule15, rule16, rule17, rule18, rule19, rule20, rule21, rule22, rule23, rule24, rule25, rule26, rule27])
    IrrTimeping = ctrl.ControlSystemSimulation(IrrTimeping_ctrl)
    #
    #
    ## Pass inputs to the ControlSystem using Antecedent labels with Pythonic API
    ## Note: if you like passing many inputs all at once, use .inputs(dict_of_data)
    IrrTimeping.input['Moisture'] = Moisture_A
    IrrTimeping.input['Temperature'] = Temperature_A
    IrrTimeping.input['Radiation'] = Radiation_A

    IrrTimeping.compute()
    print (IrrTimeping.output['IrrTime'])
    return IrrTimeping.output['IrrTime']


def main():
    Moisture_A=25
    Temperature_A=26.8
    Radiation_A=720
    Fuzzy_Metod_Presc(Moisture_A,Temperature_A,Radiation_A)

if __name__ == '__main__':
    main()
 
sys.exit(0) 