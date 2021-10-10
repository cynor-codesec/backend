from db import cv_collection


def init_cv(id, jd_id, path):
    ins = cv_collection.insert_one({
        "_id": id,
        "jd_id": jd_id,
        "file": path,
        "total_score": -1,
        "cv_feature_store": {},
        "name": None,
        "mobile_number": None,
        "email": None,
        "degree": None,
        "designation": None,
        "experience": [],
        "total_experience": -1,
        "college_name": None,
        "github_link": None,
        "skill_verify": {}
    })
    return ins.inserted_id
