import json

def save_json(name,list_data):
    with open(f"./results_graphics/{name}.json","w") as file:
        json.dump(list_data,file,indent=4)
