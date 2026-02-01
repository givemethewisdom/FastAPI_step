"""
Only DAtabase MODELS
"""

from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, func, Interval, Boolean, Table
from sqlalchemy.orm import relationship

from DataBase.Database import Base


class UserDB(Base):
    """
    Модель данных таблицы users в Postgres для Алхимии
    """
    __tablename__ = "users"  # таблица users

    id = Column(Integer, primary_key=True)
    username = Column(String(45), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    info = Column(String(50), nullable=True)
    roles = Column(String(50), nullable=True,server_default='user')

    # Связь с todoo (активные задачи)
    todoo = relationship("TodooDB", back_populates="user", cascade="all, delete")

    # Связь с todoofinished (завершенные задачи)
    todoo_finished = relationship("TodooFinishedDB", back_populates="user", cascade="all, delete")
    token = relationship("TokenDB", back_populates="user", cascade="all, delete-orphan", uselist=False)


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


class TokenDB(Base):
    __tablename__ = "tokens"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False,
                     unique=True)  # Один токен на пользователя
    refresh_token = Column(String(500), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)  # Когда токен истекает
    is_active = Column(Boolean, default=True)  # Для инвалидации

    # Связь
    user = relationship("UserDB", back_populates="token", uselist=False)  # One-to-one
