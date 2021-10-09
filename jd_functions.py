from azure_functions import azure_ocr
import constants
from sessions import get_session_jd_img, update_session_ocr
import rqueue

def ocr_and_update(resp_path, req_path, id):
    resp_ocr = azure_ocr(constants.PUBLIC_BASE_URL + "/" + resp_path)
    req_ocr = azure_ocr(constants.PUBLIC_BASE_URL + "/" + req_path)
    jd_imgs = get_session_jd_img(id)
    jd_ocr = []
    for img in jd_imgs:
        img_ocr = azure_ocr(constants.PUBLIC_BASE_URL + "/" + img)
        for line in img_ocr:
            jd_ocr.append(line)
    #save to db
    ocr_all = {
        "resp": resp_ocr,
        "req": req_ocr,
        "jd": jd_ocr
    }
    update_session_ocr(id, ocr_all)