from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List

db = SQLAlchemy()

class Moderator(db.Model):
    __tablename__ = "moderators"

    # Schema
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str] = mapped_column(nullable=False)

class Project(db.Model):
    __tablename__ = "projects"

    # Schema
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
    description: Mapped[str] = mapped_column(nullable=False)
    img_uri: Mapped[str] = mapped_column(nullable=False)
    server_endpoint: Mapped[str] = mapped_column(nullable=False)
    github_url: Mapped[str] = mapped_column(nullable=False)
    demo_url: Mapped[str] = mapped_column(nullable=True)

    # Relationships
    technologies: Mapped[List["Technology"]] = relationship(
        back_populates = "project", 
        cascade = "all, delete",
        passive_deletes = True
        )

class Technology(db.Model):
    __tablename__ = "technologies"

    # Schema
    id: Mapped[int] = mapped_column(primary_key=True)
    img_uri: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(nullable=False)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"))

    # Relationships
    project: Mapped["Project"] = relationship(back_populates="technologies")