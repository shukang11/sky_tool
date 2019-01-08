from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.dialects.mssql import FLOAT, TEXT, INTEGER, DECIMAL, SMALLINT
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound, \
    UnmappedColumnError
from sqlalchemy import Sequence
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, request
from flask_uploads import UploadSet, DEFAULTS
import redis

db = SQLAlchemy()

fileStorage = UploadSet('photos', DEFAULTS)

pool = redis.ConnectionPool(port=6379)
redisClient = redis.Redis(connection_pool=pool)

__all__ = ["Column", "ForeignKey", "String", "FLOAT",
           "TEXT", "INTEGER", "DECIMAL", "SMALLINT",
           "NoResultFound", "MultipleResultsFound",
           "UnmappedColumnError", "Sequence",
           "Flask", "request", "redisClient", "db", "fileStorage"]