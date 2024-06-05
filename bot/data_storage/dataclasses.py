# -*- coding: UTF-8 -*-

from dataclasses import dataclass


@dataclass
class ConnectionData:
    host: str
    port: int
    user: str
    password: str
    db_name: str
    

@dataclass
class UserData:
    id_tg: str
    nickname: str
    full_name: str
    phone: str
    

@dataclass
class ProductData:
    date_of_man: str
    number_packgage: str
    identifier: str