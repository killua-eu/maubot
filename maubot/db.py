# maubot - A plugin-based Matrix bot system.
# Copyright (C) 2019 Tulir Asokan
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
from typing import Iterable, Optional

from sqlalchemy import Column, String, Boolean, ForeignKey, Text
from sqlalchemy.engine.base import Engine
import sqlalchemy as sql

from mautrix.types import UserID, FilterID, SyncToken, ContentURI
from mautrix.util.db import Base

from .config import Config


class DBPlugin(Base):
    __tablename__ = "plugin"

    id: str = Column(String(255), primary_key=True)
    type: str = Column(String(255), nullable=False)
    enabled: bool = Column(Boolean, nullable=False, default=False)
    primary_user: UserID = Column(String(255),
                                  ForeignKey("client.id", onupdate="CASCADE", ondelete="RESTRICT"),
                                  nullable=False)
    config: str = Column(Text, nullable=False, default='')

    @classmethod
    def all(cls) -> Iterable['DBPlugin']:
        return cls._select_all()

    @classmethod
    def get(cls, id: str) -> Optional['DBPlugin']:
        return cls._select_one_or_none(cls.c.id == id)


class DBClient(Base):
    __tablename__ = "client"

    id: UserID = Column(String(255), primary_key=True)
    homeserver: str = Column(String(255), nullable=False)
    access_token: str = Column(Text, nullable=False)
    enabled: bool = Column(Boolean, nullable=False, default=False)

    next_batch: SyncToken = Column(String(255), nullable=False, default="")
    filter_id: FilterID = Column(String(255), nullable=False, default="")

    sync: bool = Column(Boolean, nullable=False, default=True)
    autojoin: bool = Column(Boolean, nullable=False, default=True)

    displayname: str = Column(String(255), nullable=False, default="")
    avatar_url: ContentURI = Column(String(255), nullable=False, default="")

    @classmethod
    def all(cls) -> Iterable['DBClient']:
        return cls._select_all()

    @classmethod
    def get(cls, id: str) -> Optional['DBClient']:
        return cls._select_one_or_none(cls.c.id == id)


def init(config: Config) -> Engine:
    db_engine = sql.create_engine(config["database"])
    Base.metadata.bind = db_engine

    for table in (DBPlugin, DBClient):
        table.db = db_engine
        table.t = table.__table__
        table.c = table.t.c
        table.column_names = table.c.keys()

    return db_engine
