from sqlalchemy import Column, Float, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import relationship

from .relational_db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)

    parameters = relationship("UserParameters", back_populates="owner")
    favorites = relationship("FavoriteOutfit", back_populates="user")


class UserParameters(Base):
    __tablename__ = "user_parameters"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    sex = Column(String, nullable=True)
    height = Column(Float, nullable=True)
    bust = Column(Float, nullable=True)
    waist = Column(Float, nullable=True)
    hips = Column(Float, nullable=True)
    body_type = Column(String, nullable=True)
    color_type = Column(String, nullable=True)

    body_type_recommendation = Column(JSON, nullable=True)
    color_type_recommendation = Column(JSON, nullable=True)

    owner = relationship("User", back_populates="parameters")


class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, index=True)
    action_type = Column(String, index=True)
    feedback_type = Column(String, index=True)
    count = Column(Integer, default=1)


class FavoriteOutfit(Base):
    __tablename__ = "favorite_outfits"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    outfit = Column(JSON)

    user = relationship("User", back_populates="favorites")
