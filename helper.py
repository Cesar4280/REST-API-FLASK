# modulos
from os import urandom
from datetime import datetime


# generar contraseña
def safekey():
    return urandom(12).hex()


# generar registro de tiempo
def timestamp():
    return datetime.timestamp(datetime.now())


# obtener valores a insertar
def values(dic):
    return tuple(dic.values())


# obtener campos a insertar
def fields(dic):
    return ','.join(dic.keys())


# generar marcadores de posición
def params(count):
    return ','.join(["%s"] * count)
