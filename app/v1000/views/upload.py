import uuid
import os
from werkzeug.datastructures import FileStorage
from flask import request, jsonify
from app.utils.ext import fileStorage, db
from ..views import api
from ..utils.respObj import RespObj
from app.models import FileModel


@api.route('/upload', methods=['POST'])
def upload():
    # 如果是单个文件
    # file = request.files["files"]
    files: list = request.files.getlist("files")
    resp = []
    for file in files:
        print(file)
        file: FileStorage = file
        extension = file.filename.split('.')
        identifier = str(uuid.uuid4()).replace("-", "")+"."+extension[1]
        try:
            rec = fileStorage.save(file, name=identifier)
            fileObj = FileModel(file_hash=identifier, file_name=file.name, file_type=file.mimetype)
            fileObj.save(commit=True)
            resp.append({
                "origin": file.filename,
                "fileName": fileStorage.url(rec)
            })
        except Exception as e:
            print(e)
            return jsonify(RespObj(0,toast="error").json())
    return jsonify(RespObj(1, body=resp, toast="收到{}个文件".format(len(resp))).json())


@api.route('/file/list', methods=['POST', 'GET'])
def listall():
    allFiles = FileModel.queryAll(FileModel)
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
    return jsonify(RespObj(1, body=payload).json())


@api.route('/file/delete', methods=['POST'])
def delete():
    file_id = request.args.get('file_id')
    item = db.session.query_by(file_id==file_id).first()
    if item:
        path = fileStorage.path(item.file_hash)
        try: os.remove(path)
        except: pass
        item: FileModel = item
        item.delete(logic=False)
        return jsonify(RespObj(1).json())
    return jsonify(RespObj(0, toast="文件不存在").json())