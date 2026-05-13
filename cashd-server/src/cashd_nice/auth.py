from pathlib import Path
from typing import Any, List
from sqlalchemy import exists

from cashd_core.data import (
    create_engine,
    Engine,
    Session,
    Integer,
    String,
    types,
    DeclarativeBase,
    Column,
    insert,
    select,
    delete,
    relationship,
    Mapped,
    DATA_PATH,
)


DB_ENGINE = create_engine(f"sqlite:///{Path(DATA_PATH, 'auth.db')}", echo=False)


class RequiredText(types.TypeDecorator):
    """SQLAlchemy allows empty strings in a non nullable column by default.
    This custom type coerces the value to a stripped string and raises an error when
    the resulting string is empty.
    """
    impl = String
    cache_ok = True

    def process_bind_param(self, value, dialect):
        value = str(value).strip()
        if len(value) == 0:
            raise ValueError("Required text field was empty.")
        return value

    def process_result_value(self, value, dialect):
        return value


class AuthTable(DeclarativeBase):
    Id = Column("Id", Integer, primary_key=True)

    @property
    def data(self) -> dict[str, Any]:
        return {
            colname: getattr(self, colname, None)
            for colname in self.__table__.c.keys()
            if colname != "Id"
        }

    def read(self, row_id: int, engine: Engine = DB_ENGINE):
        """
        Fetches one row of data from the database and loads into this instance.

        :param row_id: Primary key integer value to look for in the table.
        :param engine: `sqlalchemy.Engine` reflecting the database that will be read.

        :raises ValueError: If `row_id` is not present in the table.
        """
        cls = type(self)
        stmt = select(cls).where(cls.Id == row_id)
        with Session(bind=engine) as ses:
            res = ses.execute(stmt).first()
            if res is None:
                raise ValueError(
                    f"{row_id=} not present in '{
                        self.__tablename__}.Id'."
                )
            row = res[0]
            for col in self.__table__.columns:
                value = getattr(row, col.name, None)
                setattr(self, col.name, value)

    def write(self, engine: Engine = DB_ENGINE):
        """Validates and adds a new row in the database with it's own data.

        :param engine: `sqlalchemy.Engine` reflecting the database that will be read.
        """
        cls = type(self)
        with Session(bind=engine) as ses:
            stmt = insert(cls).values(**self.data)
            ses.execute(stmt)
            ses.commit()

    def exists(self, engine: Engine = DB_ENGINE) -> bool:
        """Checks if the data in this instance is already present in the database.
        Ignores the 'Id' column and always return False if a value is None or not set.

        :param engine: `sqlalchemy.Engine` reflecting the database that will be read.

        :returns: A boolean value indicating if this instance's data is present in the
          database.
        """
        cls = type(self)
        with Session(bind=engine) as ses:
            exists_stmt = exists()
            for colname, val in self.data.items():
                if val is None:
                    return False
                col = self.__table__.columns[colname]
                exists_stmt.where(col == val)
            stmt = select(exists_stmt)
            return bool(ses.execute(stmt))


class User(AuthTable):
    __tablename__ = "users"
    UserRoleRelation: Mapped["permission_levels"] = relationship()
    RoleId = Column("Role", RequiredText, nullable=False)
    Username = Column("Username", RequiredText, nullable=False, unique=True)
    HashedPwd = Column("HashedPwd", RequiredText)

    def __repr__(self):
        RoleId, Username = self.RoleId, self.Username
        return f"<AuthTable:User {RoleId=} {Username=}>"


class PermissionLevel(AuthTable):
    __tablename__ = "permission_levels"
    RoleUsersRelation: Mapped[List["users"]] = relationship(
        back_populates="UserRoleRelation"
    )
    RoleName = Column("RoleName", RequiredText, nullable=False, unique=True)
    ForbiddenPages = Column("ForbiddenPages", RequiredText, nullable=False, default="")

    def __repr__(self):
        RoleName, ForbiddenPages = self.RoleName, self.ForbiddenPages
        return f"<AuthTable:PermissionLevel {RoleName=} {ForbiddenPages=}>"


AuthTable.metadata.create_all(DB_ENGINE)


DEFAULT_ROLES = [
    PermissionLevel(RoleName="Operador", ForbiddenPages="/stats;/config"),
    PermissionLevel(RoleName="Supervisor" ForbiddenPages="/config"),
]
for role in DEFAULT_ROLES:
    if not role.exists():
        role.write()

