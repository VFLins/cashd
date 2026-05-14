from pathlib import Path
from typing import Any, List
from argon2 import PasswordHasher
from sqlalchemy import (
    create_engine,
    Engine,
    Integer,
    String,
    types,
    Column,
    ForeignKey,
    insert,
    select,
    exists,
)
from sqlalchemy.orm import (
    Session,
    DeclarativeBase,
    Mapped,
    relationship,
    Mapped,
)

from cashd_core.data import DATA_PATH, _DataSource


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
        """Fetches one row of data from the database and loads into this instance.

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
                    f"{row_id=} not present in '{self.__tablename__}.Id'."
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
            stmt = select(cls)
            for colname, val in self.data.items():
                if val is None:
                    return False
                col = self.__table__.columns[colname]
                stmt = stmt.where(col == val)
            return bool(ses.execute(stmt.exists().select()).scalar())


class User(AuthTable):
    __tablename__ = "users"
    UserRoleRelation: Mapped["Role"] = relationship()
    RoleId = Column("RoleId", RequiredText, ForeignKey("roles.Id"), nullable=False)
    Username = Column("Username", RequiredText, nullable=False, unique=True)
    HashStr = Column("HashStr", RequiredText, nullable=False)

    def read_user(self, username: str, engine: Engine = DB_ENGINE):
        """Fetches one row of data from the database and loads into this instance.

        :param username: Username to bo looked for in the database.
        :param engine: `sqlalchemy.Engine` reflecting the database that will be read.

        :raises ValueError: If `row_id` is not present in the table.
        """
        stmt = select(User).where(User.Username == username)
        with Session(bind=engine) as ses:
            res = ses.execute(stmt).first()
            if res is None:
                raise ValueError(f"'{username}' not present in the database")
            row = res[0]
            for col in self.__table__.columns:
                value = getattr(row, col.name, None)
                setattr(self, col.name, value)

    @property
    def ForbiddenPages(self) -> list[str] | None:
        role_id = getattr(self, "RoleId", None)
        if type(role_id) is int:
            role = Role()
            role.read(row_id=role_id)
            return role.ForbiddenPages.split(";")

    def __repr__(self):
        RoleId, Username = self.RoleId, self.Username
        return f"<AuthTable:User {RoleId=} {Username=}>"


class Role(AuthTable):
    __tablename__ = "roles"
    RoleUsersRelation: Mapped[List["User"]] = relationship(back_populates="UserRoleRelation")
    RoleName = Column("RoleName", RequiredText, nullable=False, unique=True)
    ForbiddenPages = Column("ForbiddenPages", RequiredText, nullable=False, default="")

    def __repr__(self):
        RoleName, ForbiddenPages = self.RoleName, self.ForbiddenPages
        return f"<AuthTable:Role {RoleName=} {ForbiddenPages=}>"


AuthTable.metadata.create_all(DB_ENGINE)


DEFAULT_ROLES = (
    Role(RoleName="Operador", ForbiddenPages="/stats;/config"),
    Role(RoleName="Supervisor", ForbiddenPages="/config"),
)
for role in DEFAULT_ROLES:
    if not role.exists():
        role.write()


def verify_login(username: str, password: str) -> User:
    """Verify if the username+password combination is valid.

    :param username: Public username provided by the user.
    :param password: Private password to be verified by the algorithm.

    :returns: If the login is valid, a `User` object, containing user information.
    :raises ValueError: If the username provided does not exist.
    :raises argon2.exceptions.VerifyMismatchError: If the password is not correct.
    """
    user = User()
    user.read_user(username)
    ph = PasswordHasher()
    _ = ph.verify(user.HashStr, password)
    return user
 

def store_login(role_id: int, username: str, password: str):
    """Writes a new user to the database.

    :param role_id: Identifier of this user's role.
    :param username: New user's username.
    :param password: New user's password.

    :raises ValueError: If the `role_id` does not exist.
    :raises sqlalchemy.exc.IntegrityError: If the username already exists.
    """
    _ = Role().read(row_id=role_id) # Raises the expected ValueError
    ph = PasswordHasher()
    hashed = ph.hash(password)
    user = User(RoleId=role_id, username=username, HashStr=hashed)
    user.write()


class UserRoleSource(_DataSource):
    def __init__(self, engine: Engine = DB_ENGINE):
        stmt = select(
            User.Id.label("Id"),
            User.Username.label("Username"),
            User.Role.label("Role")
        )
        super().__init__(
            select_stmt=stmt,
            paginated=True,
            searchable=True,
            search_colnames=["Username", "Role"],
            engine=engine,
        )

