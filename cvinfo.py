from db import cv_collection
from pyresparser import ResumeParser


def init_cv(id, jd_id, path):
    ins = cv_collection.insert_one({
        "_id": id,
        "jd_id": jd_id,
        "file": path,
        "total_score": -1,
        "cv_feature_store": None,
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


def update_cv_feature_store(id, feature_store):
    cv_collection.update_one(
        {"_id": id}, {"$set": {"cv_feature_store": feature_store}})


def parse_resume(cv_paths):
    for path in cv_paths:
        id = path.split("/")[-1].split(".")[0]
        print("py res parser is processing " + id)
        data = ResumeParser(path).get_extracted_data()
        name = data["name"]
        mobile_number = data["mobile_number"]
        email = data["email"]
        degree = data["degree"]
        designation = data["designation"]
        experience = data["experience"]
        total_experience = data["total_experience"]
        college_name = data["college_name"]
        # update in db
        cv_collection.update_one({"_id": id}, {"$set": {"name": name, "mobile_number": mobile_number, "email": email, "degree": degree,
                                                        "designation": designation, "experience": experience, "total_experience": total_experience, "college_name": college_name}})


def get_cvs_by_jd_id(jd_id):
    return cv_collection.find({"jd_id": jd_id})


def get_average_score(jd_id):
    cv_list = get_cvs_by_jd_id(jd_id)
    total_score = 0
    for cv in cv_list:
        total_score += cv["cv_feature_store"]["total_score"]
    return total_score/cv_list.count()


def number_of_cvs(jd_id):
    return get_cvs_by_jd_id(jd_id).count()


def get_list_of_total_scores(jd_id):
    cv_list = get_cvs_by_jd_id(jd_id)
    total_score_list = []
    for cv in cv_list:
        total_score_list.append(cv["cv_feature_store"]["total_score"])
    return total_score_list


def get_cv_by_id(id):
    return cv_collection.find_one({"_id": id})


def clean_list(list):
    return str(list).replace("[", "").replace("]", "").replace("'", "").replace(",", ";")

def get_cvs_by_jd_id_sorted_by_total_score(jd_id):
    cv_list = get_cvs_by_jd_id(jd_id)
    cv_list = list(cv_list)
    cv_list.sort(key=lambda x: x["cv_feature_store"]["total_score"], reverse=True)
    return cv_list


def create_csv(jd_id):
    cv_list = get_cvs_by_jd_id_sorted_by_total_score(jd_id)
    csv_file = open("static/csv/"+jd_id+".csv", "w")
    csv_file.write(
        "Name,Mobile Number,Email,Degree,Designation,Experience,Total Experience,College Name,Total Score,URL\n")
    for cv in cv_list:
        if not cv["degree"]:
            cv["degree"] = ["NA"]
        if not cv["designation"]:
            cv["designation"] = ["NA"]
        if not cv["college_name"]:
            cv["college_name"] = ["NA"]
        if not cv["experience"]:
            cv["experience"] = ["NA"]
        if not cv["college_name"]:
            cv["college_name"] = ["NA"]
        if not cv["name"]:
            cv["name"] = "NA"
        if not cv["mobile_number"]:
            cv["mobile_number"] = "NA"
        if not cv["email"]:
            cv["email"] = "NA"
        if not cv["total_experience"]:
            cv["total_experience"] = "NA"
        

        csv_file.write(cv["name"]+","+str(cv["mobile_number"])+","+cv["email"]+","+clean_list(cv["degree"][0])+","+clean_list(cv["designation"][0])+","+clean_list(cv["experience"][0])+","+str(cv["total_experience"]) +
                       ","+clean_list(cv["college_name"][0])+","+str(cv["cv_feature_store"]["total_score"])+ "," + str("static/cv/" + jd_id + "/" + cv["_id"] + ".pdf")+"\n")
    csv_file.close()
    return "static/csv/"+jd_id+".csv"
