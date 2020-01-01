import sqlalchemy
from models.base_model import Base


class Contents(Base):
    __tablename__ = 'contents'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    name = sqlalchemy.Column(sqlalchemy.String(255))
    unique_id = sqlalchemy.Column(sqlalchemy.String(20))
    tags = sqlalchemy.Column(sqlalchemy.String(255))
    type = sqlalchemy.Column(sqlalchemy.SMALLINT)
    thumb_url = sqlalchemy.Column(sqlalchemy.String(255))
    torrent_url = sqlalchemy.Column(sqlalchemy.String(1000))