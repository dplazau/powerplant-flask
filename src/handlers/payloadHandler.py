import json
import os

cwd = os.getcwd()
PATH_PAYLOADS = '/app/example_payloads'
PAYLOADS = [PAYLOAD for PAYLOAD in os.listdir(PATH_PAYLOADS) if PAYLOAD.endswith('.json')]
EMITTED_CO2 = 0.3


def show_files():
    all_payloads = []
    i = 0
    for PAYLOAD in PAYLOADS:
        with open(os.path.join(PATH_PAYLOADS, PAYLOAD)) as json_payload:
            all_payloads.append(json.load(json_payload))
        i += 1
    return all_payloads


def merit_order(fuels, powerplants):
    merit_dict = {}
    for fuel_key, fuel_value in fuels.items():
        for k, v in powerplants.items():
            if fuel_key == 'gas' and v['type'] == 'gasfired':
                min_output = float(fuel_value) * float(v['pmin']) / float(v['efficiency'])
                max_output = float(fuel_value) * float(v['pmax']) / float(v['efficiency'])
                co2_min_output = (float(v['pmin']) / float(v['efficiency'])) * EMITTED_CO2 * float(fuels['co2'])
                co2_max_output = (float(v['pmax']) / float(v['efficiency'])) * EMITTED_CO2 * float(fuels['co2'])
                total_min_output = co2_min_output + min_output
                total_max_output = co2_max_output + max_output
                price_per_unit = total_max_output / float(v['pmax'])
                merit_dict[k] = round(price_per_unit, 1)
                #print(k, fuel_key, fuel_value, v['type'], total_min_output, total_max_output, price_per_unit, merit_dict)
            elif fuel_key == "kerosine" and v['type'] == 'turbojet':
                min_output = float(fuel_value) * float(v['pmin']) / float(v['efficiency'])
                max_output = float(fuel_value) * float(v['pmax']) / float(v['efficiency'])
                co2_min_output = (float(v['pmin']) / float(v['efficiency'])) * EMITTED_CO2 * float(fuels['co2'])
                co2_max_output = (float(v['pmax']) / float(v['efficiency'])) * EMITTED_CO2 * float(fuels['co2'])
                total_min_output = co2_min_output + min_output
                total_max_output = co2_max_output + max_output
                price_per_unit = total_max_output / float(v['pmax'])
                merit_dict[k] = round(price_per_unit, 1)
                #print(k, fuel_key, fuel_value, v['type'], total_min_output, total_max_output, price_per_unit, merit_dict)
            elif v['type'] == 'windturbine':
                merit_dict[k] = 0.0
            else:
                pass
    return merit_dict


def set_load(data):
    data_dict = {}
    load = {}
    for e in data:
        data_dict[e] = data[e]
    for key, value in data_dict.items():
        PAYLOAD_ATTRIBUTE = key.split(".")
        if PAYLOAD_ATTRIBUTE[0] == "load":
            load[key.split(".")[1]] = float(value)
    return load


def powerplants_set(data):
    data_dict = {}
    powerplants_list = []
    for e in data:
        data_dict[e] = data[e]

    for key, value in data_dict.items():
        PAYLOAD_ATTRIBUTE = key.split(".")
        if PAYLOAD_ATTRIBUTE[0] == "powerplant":
            powerplants_list.append(PAYLOAD_ATTRIBUTE[1])

    return set(powerplants_list)


def set_fuels(data):
    data_dict = {}
    fuels = {}
    for e in data:
        data_dict[e] = data[e]
    for key, value in data_dict.items():
        PAYLOAD_ATTRIBUTE = key.split(".")
        if PAYLOAD_ATTRIBUTE[0] == "fuel":
            fuels[PAYLOAD_ATTRIBUTE[1].split("(")[0]] = float(value)
    return fuels


def calculate(data):
    data_dict = {}
    fuels = set_fuels(data)
    load = set_load(data)
    powerplants = {}
    powerplant_info = {}
    powerplants_unique_list = powerplants_set(data)
    for e in data:
        data_dict[e] = data[e]

    for powerplant in powerplants_unique_list:
        attributes = {}
        for key, value in data_dict.items():
            PAYLOAD_ATTRIBUTE = key.split(".")
            if PAYLOAD_ATTRIBUTE[0] == "powerplant":
                if PAYLOAD_ATTRIBUTE[1] == powerplant:
                    attributes[PAYLOAD_ATTRIBUTE[2]] = value
        powerplants[powerplant] = attributes

    #pprint.pprint(load)
    #pprint.pprint(fuels)
    #pprint.pprint(powerplants)
    merit_dict = merit_order(fuels, powerplants)
    merit_dict = {k: v for k, v in sorted(merit_dict.items(), key=lambda item: item[1])}
    print(merit_dict)

    target_load = load['load']
    target_powerplants = {}
    total_load_consumed = 0
    for k, v in merit_dict.items():
        if target_load >= 0:
            load_consumed = 0
            for powerplant, attributes in powerplants.items():
                if k == powerplant:
                    if attributes['type'] == 'windturbine' and target_load >= float(attributes['pmin']):
                        if target_load >= float(attributes['pmax']):
                            load_consumed = float(attributes['pmax']) * float(fuels['wind'])/100
                            target_load -= load_consumed
                            total_load_consumed += load_consumed
                            target_powerplants[powerplant] = load_consumed
                        elif float(attributes['pmin']) <= target_load <= float(attributes['pmax']):
                            load_consumed = target_load
                            target_load -= load_consumed
                            total_load_consumed += load_consumed
                    elif attributes['type'] != 'windturbine':
                        if target_load >= float(attributes['pmax']):
                            load_consumed = 0.8 * float(attributes['pmax'])
                            total_load_consumed += load_consumed
                            target_load -= load_consumed
                        elif float(attributes['pmin']) <= target_load <= float(attributes['pmax']):
                            load_consumed = target_load
                            target_load -= load_consumed
                            total_load_consumed += load_consumed
                        target_powerplants[powerplant] = load_consumed
    print(total_load_consumed)

    return target_powerplants
