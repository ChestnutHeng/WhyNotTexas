mod = {
    "pokes": {
        "files": [

        ]
    },
    "meta": {
        "generated": "1401380327373",
        "app": "Phaser 3 Asset Packer",
        "url": "https://phaser.io",
        "version": "1.0",
        "copyright": "Photon Storm Ltd. 2018"
    }
}

files = {
    "type": "image",
    "key": "%s",
    "url": "../static/assets/cards/%s",
    "overwrite": False
}

import json
import copy
import os

def trans_name(name):
    name = name.strip('.png')
    colors = {'C': '♣', 'D': '♦','H': '♥', 'S': '♠'}
    if len(name) <= 3:
        number = name[:-1]
        color = colors[name[-1:]]
        name = color+number
    return name

def gen_asset():
    for path,dir_list,file_list in os.walk('../static/assets/cards/'):  
        for file_name in file_list:
            nfile = copy.deepcopy(files)
            nfile['key'] = trans_name(file_name)
            nfile['url'] = nfile['url'] % file_name
            mod['pokes']['files'].append(nfile)
            #print(os.path.join(path, file_name))
    fp = open('../static/assets/asset.json', 'w+')
    json.dump(mod, fp, indent=4)
    fp.close()

gen_asset()