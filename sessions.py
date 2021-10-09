from db import sessions_collection

def init_session(id, jd_org, jd_img):
    ins = sessions_collection.insert_one({
        '_id': id,
        'status': None,
        'JD_org': jd_org,
        'JD_img': jd_img,
        'req_img': None,
        'resp_img': None,
        'features_store': None,
        'rating': -1
    })
    return ins.inserted_id

def get_session_status(id):
    return sessions_collection.find_one({'_id': id})['status']