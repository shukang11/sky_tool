import uuid
import os
from werkzeug.datastructures import FileStorage
from flask import request, jsonify, render_template, current_app, g
from app.utils.ext import fileStorage, db
from ..views import api
from app.utils import response_succ, CommonError, login_require
from app.models import FileModel, FileUserModel


@api.route('/upload', methods=['POST'])
@login_require
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
        ext: str = extension[1]
        identifier = str(uuid.uuid4()).replace("-", "")+"."+ext.lower()
        try:
            rec = fileStorage.save(file, name=identifier)
            fileObj = FileModel(file_hash=identifier, file_name=file.filename, file_type=file.mimetype)
            fileObj.save()
            db.session.flush()
            fileId = fileObj.file_id
            userId = g.current_user.id
            relationObj = FileUserModel(user_id=userId, file_id=fileId)
            relationObj.save(commit=True)
            
            resp.append({
                "origin": file.filename,
                "fileName": fileStorage.url(rec)
            })
        except Exception as e:
            current_app.logger.error(e)
            print(e)
            return CommonError.get_error(9999)
    return response_succ(body=resp)


@api.route('/file/list', methods=['POST', 'GET'])
@login_require
def listall():
    userId = g.current_user.id
    allFiles = db.session.query(FileModel, FileUserModel).\
        filter(FileModel.file_id==FileUserModel.file_id).\
        filter(FileUserModel.user_id==userId).all()
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