# -*- coding: UTF-8 -*-

from sqlalchemy.orm import declarative_base
from sqlalchemy import MetaData


Base = declarative_base(metadata=MetaData(schema='helper_bot'))