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
        'rating': -1,
        'ocr': {"jd": None, "req": None, "resp": None},
    })
    return ins.inserted_id


def get_session_status(id):
    return sessions_collection.find_one({'_id': id})['status']


def get_session(id):
    return sessions_collection.find_one({'_id': id})


def update_session_status(id, status):
    sessions_collection.update_one({'_id': id}, {'$set': {'status': status}})


def update_session_rating(id, rating):
    sessions_collection.update_one({'_id': id}, {'$set': {'rating': rating}})


def update_session_ocr(id, ocr):
    sessions_collection.update_one({'_id': id}, {'$set': {'ocr': ocr}})


def update_session_features(id, features):
    sessions_collection.update_one(
        {'_id': id}, {'$set': {'features_store': features}})


def update_session_req_img(id, img):
    sessions_collection.update_one({'_id': id}, {'$set': {'req_img': img}})


def update_session_resp_img(id, img):
    sessions_collection.update_one({'_id': id}, {'$set': {'resp_img': img}})


def get_session_jd_img(id):
    return sessions_collection.find_one({'_id': id})['JD_img']


def get_session_feature_store(id):
    return sessions_collection.find_one({'_id': id})['features_store']
