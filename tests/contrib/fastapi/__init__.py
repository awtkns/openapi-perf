from ._server import Server

from . import sqlalchemy_impl, memory_impl

implementations = [Server(app) for app in [sqlalchemy_impl.app, memory_impl.app]]
