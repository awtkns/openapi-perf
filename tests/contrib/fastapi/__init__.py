from . import sqlalchemy_impl
from ._server import Server

implementations = [
    sqlalchemy_impl.app
]

implementations = [Server(app) for app in implementations]
