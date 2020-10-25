import json
import pickle

CLASS_FILE = './statistics/classification.json'
FAMILY_FILE = './statistics/children.pk'

def is_child(f, c):
    if len(c) <= len(f):
        return False
    if c[:len(f)] != f:
        return False
    if '.' in c[len(f)+1:]:
        return False
    return True

def main():
    with open(CLASS_FILE, mode='r', encoding='UTF-8') as f:
        items = json.load(f)

    result = dict()

    name_sid = dict()
    for item in items:
        name = item['nameZh']
        item_id = item['sid']
        name_sid[item_id] = name

    sids = name_sid.keys()
    for sid in sids:
        children_sids = []
        for i in sids:
            if is_child(sid, i):
                children_sids.append(i)
        name = name_sid[sid]
        children_names = [name_sid[i] for i in children_sids]
        result[name] = children_names
    
    with open(FAMILY_FILE, mode='wb') as w_f:
        pickle.dump(result, w_f)

if __name__ == "__main__":
    main()