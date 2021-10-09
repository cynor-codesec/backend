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
from sessions import init_session, get_session_status
import PIL

from file_manager import save_file


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
            images = convert_from_path(file_path)
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
            return JSONResponse(content={
                "message": "File created!",
                "_id": id_afi,
                "jd_img": jd_imgs,
                "jd_org": file_path
            }, status_code=201)
        else:
            return JSONResponse(content={"message": "Wrong file type!"}, status_code=400)
    return JSONResponse(content={"message": "Error adding JD"}, status_code=500)

@app.get("/get-status")
async def get_status(id: str):
    try:
        status = get_session_status(id)
        return JSONResponse(content={"status": status}, status_code=200)
    except:
        return JSONResponse(content={"status": "Error, Invalid id"}, status_code=500)