"""
Only DAtabase MODELS
"""

from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, func, Interval
from sqlalchemy.orm import relationship

from DataBase.Database import Base


class UserDB(Base):
    """
    Модель данных таблицы users в Postgres для Алхимии
    """
    __tablename__ = "users"  # таблица users

    id = Column(Integer, primary_key=True)
    username = Column(String(50), nullable=False, unique=False)
    password = Column(String(255), nullable=False)
    info = Column(String(50), nullable=True)

    # Связь с todoo (активные задачи)
    todoo = relationship("TodooDB", back_populates="user", cascade="all, delete")

    # Связь с todoofinished (завершенные задачи)
    todoo_finished = relationship("TodooFinishedDB", back_populates="user", cascade="all, delete")


class TodooDB(Base):
    """
    Модель таблицы todoo в Postgres для Алхимии
    задачи в исполнении (флаг completed = False)
    """

    __tablename__ = "todoo"  # table todoo

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    title = Column(String(100), nullable=False)
    description = Column(String(500), nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        comment='время  автоматически устанавливается при создании записи'
    )

    user = relationship("UserDB", back_populates="todoo")


class TodooFinishedDB(Base):
    """
    модель таблцицы todoofinished в postgres для завершенных задач
    скорее всего нужно хранить задачи за удаленным пользователем. но пока удаляю вместе с ним
    """

    __tablename__ = "todoofinished"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    title = Column(String(100), nullable=False)
    description = Column(String(500), nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        comment='время переносится из todoo'
    )

    finished_at = Column(
        DateTime(timezone=True),
        nullable=False,
        comment='время  устанавливается в ендпоинте(по логике такой всего 1)'
    )

    all_time_cost = Column(
        Integer,  # секунды как целое число
        nullable=True,
        comment='общее время затраченое на задачу в секундах вычисляется при переходе в TodooFinished'
    )

    user = relationship("UserDB", back_populates="todoo_finished")


