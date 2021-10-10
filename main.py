import db
from typing import Optional
import uuid
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from pdf2image import convert_from_path
from sessions import *
from cvinfo import *
from azure_functions import azure_ocr
from docx2pdf import convert
import zipfile
import constants
# import models
from jd_functions import ocr_and_update
import rqueue

from file_manager import save_file, save_cvs_zip
from pydantic import BaseModel
import add_to_store

class UpdateFS(BaseModel):
    id: str
    feature_store: dict


def configure_static(app):
    app.mount("/static", StaticFiles(directory="static"), name="static")


def start_application():
    app = FastAPI(title="cynor", version="1.0")
    configure_static(app)
    return app


app = start_application()

cors_origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


@app.get("/")
def read_root():
    return {"Status": "Online"}


@app.post("/send-jd")
async def send_jd(file: UploadFile = File(...)):
    u_id = str(uuid.uuid4().hex)
    if file.filename == "":
        return JSONResponse(content={"message": "No file sent!"}, status_code=400)
    else:
        if file.filename.endswith(".pdf") or file.filename.endswith(".docx"):
            if file.filename.endswith(".pdf"):
                file_name = "jd.pdf"
            else:
                file_name = "jd.docx"
            content = await file.read()
            file_path = save_file(file_name, content, u_id, "jd")
            if file_path.endswith(".docx"):
                convert(file_path, file_path.replace(".docx", ".pdf"))
            images = convert_from_path(file_path.replace(".docx", ".pdf"))
            jd_imgs = []
            i = 1
            for image in images:
                image.save("static/jd/" + u_id + "/" +
                           "jd-page_" + str(i) + ".jpg", "JPEG")
                jd_imgs.append("static/jd/" + u_id + "/" +
                               "jd-page_" + str(i) + ".jpg")
                i += 1
            id_afi = init_session(u_id, file_path, jd_imgs)
            print(id_afi)
            update_session_status(id_afi, "initiated")
            return JSONResponse(content={
                "message": "File created!",
                "_id": id_afi,
                "jd_img": jd_imgs,
                "jd_org": file_path
            }, status_code=201)
        else:
            return JSONResponse(content={"message": "Wrong file type!"}, status_code=400)
    return JSONResponse(content={"message": "Not implemented yet"}, status_code=501)


@app.get("/get-status")
async def get_status(id: str):
    try:
        status = get_session_status(id)
        return JSONResponse(content={"status": status}, status_code=200)
    except:
        return JSONResponse(content={"status": "Error, Invalid id"}, status_code=500)


@app.post("/send-selected-features")
async def send_selected_features(id: str, resp: UploadFile = File(...), req: UploadFile = File(...)):
    if resp.filename == "" or req.filename == "":
        return JSONResponse(content={"message": "Resp/Req image missing"}, status_code=400)
    else:
        if resp.filename.endswith(".png") and req.filename.endswith(".png"):
            resp_content = await resp.read()
            req_content = await req.read()
            resp_path = save_file("resp.png", resp_content, id, "jd")
            req_path = save_file("req.png", req_content, id, "jd")
            rqueue.q.enqueue(ocr_and_update, resp_path, req_path, id)
            return JSONResponse(content={
                "message": "Images saved",
                "resp_img": resp_path,
                "req_img": req_path
            }, status_code=201)
        else:
            return JSONResponse(content={"message": "Wrong file type!"}, status_code=400)
    return JSONResponse(content={"message": "Not implemented yet"}, status_code=501)


@app.get("/get-feature-store")
async def get_feature_store(id: str):
    try:
        feature_store = get_session_feature_store(id)
        if feature_store is None:
            return JSONResponse(content={"message": "Feature store not available yet"}, status_code=200)
        return JSONResponse(content={"feature_store": feature_store}, status_code=200)
    except:
        return JSONResponse(content={"message": "Error, Invalid id"}, status_code=500)


@app.post("/send-updated-feature_store")
async def send_updated_feature_store(item: UpdateFS):
    try:
        update_session_features(item.id, item.feature_store)
        return JSONResponse(content={"message": "Feature store updated"}, status_code=200)
    except:
        return JSONResponse(content={"message": "Error, Invalid id"}, status_code=500)


@app.post("/send-cvs")
async def send_cvs(id: str, file: UploadFile = File(...)):
    if file.filename == "":
        return JSONResponse(content={"message": "No file sent!"}, status_code=400)
    else:
        insterted_cvs = []
        cv_ids = []
        cv_paths = []
        if file.filename.endswith(".zip"):
            content = await file.read()
            file_path = save_cvs_zip(content, id)
            archive = zipfile.ZipFile(file_path, 'r')
            # print(archive.namelist())
            files_in_zip = archive.namelist()
            for fil in files_in_zip:
                if fil.endswith(".pdf") and not fil.startswith("__MACOSX"):
                    print(fil)
                    u_id = str(uuid.uuid4().hex)
                    data = archive.read(fil)
                    fp = save_file(u_id + ".pdf", data, id, "cv")
                    ins_cv = init_cv(u_id, id, fp)
                    insterted_cvs.append({"cv_id": ins_cv, "file": fp})
                    cv_ids.append(ins_cv)
                    cv_paths.append(fp) 
            archive.close()
            if len(insterted_cvs) > 0:
                rqueue.q.enqueue(add_to_store.add_to_store, cv_ids, cv_paths, id)
                return JSONResponse(content={"message": "Files saved", "cvs": insterted_cvs}, status_code=201)
            else:
                return JSONResponse(content={"message": "No files saved, zip had no pdf files!"}, status_code=400)
        else:
            return JSONResponse(content={"message": "Wrong file type!"}, status_code=400)
    return JSONResponse(content={"message": "Not implemented yet"}, status_code=501)
