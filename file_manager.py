import os
from docx2pdf import convert

jd_path = "static/jd"
cv_path = "static/cv"

def save_file(name, file_data, uid, type):
    if type == "jd":
        file_name = os.path.join(jd_path, uid + "/" + name)
    elif type == "cv":
        file_name = os.path.join(cv_path, uid + "/" + name)
    else:
        return False
    if not os.path.exists(os.path.dirname(file_name)):
        try:
            os.makedirs(os.path.dirname(file_name))
        except OSError as exc: # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise
    with open(file_name, "wb") as f:
        f.write(file_data)
    return file_name
