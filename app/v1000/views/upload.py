import uuid
import os
from werkzeug.datastructures import FileStorage
from flask import request, jsonify, render_template, current_app
from app.utils.ext import fileStorage, db
from ..views import api
from app.utils import response_succ, CommonError
from app.models import FileModel


@api.route('/upload', methods=['POST'])
def upload():
    # 如果是单个文件
    # file = request.files["files"]
    files: list = request.files.getlist("files")
    if len(files) == 0:
        return CommonError.get_error(40000)
    resp = []
    for file in files:
        file: FileStorage = file
        extension = file.filename.split('.')
        identifier = str(uuid.uuid4()).replace("-", "")+"."+extension[1]
        try:
            rec = fileStorage.save(file, name=identifier)
            fileObj = FileModel(file_hash=identifier, file_name=file.filename, file_type=file.mimetype)
            fileObj.save(commit=True)
            resp.append({
                "origin": file.filename,
                "fileName": fileStorage.url(rec)
            })
        except Exception as e:
            current_app.logger.error(e)
            return CommonError.get_error(9999)
    return response_succ(body=resp)


@api.route('/file/list', methods=['POST', 'GET'])
def listall():
    allFiles = FileModel.query_all(FileModel)
    payload = []
    for file in allFiles:
        f: FileModel = file
        payload.append({
            "name": f.file_name,
            "id": f.file_id,
            "mimetype": f.file_type,
            "hash": f.file_hash,
            "url": fileStorage.url(f.file_hash)
        })
    if request.method == "GET":
        return render_template("all_images.html", images=payload)
    return response_succ(body=payload)


@api.route('/file/delete', methods=['POST'])
def delete():
    file_id = request.args.get('file_id')
    item = db.session.query(FileModel).filter(file_id==file_id).first()
    if item:
        path = fileStorage.path(item.file_hash)
        try:
            os.remove(path)
        except:
            return CommonError.get_error(9999)

        item: FileModel = item
        item.delete(logic=False)
        return response_succ()
    return CommonError.get_error(40400)
