from cashd_core.data import (
    dec_base,
    tbl_clientes,
    tbl_transacoes,
    CustomerListSource,
    TransactionBalanceSource,
    get_default_customer,
    insert,
    select,
    func,
    create_engine,
    Engine,
    Session,
)
from cashd_core.prefs import settings
from . import mock_data
from datetime import date, datetime
from sqlalchemy import exc
from typing import Generator
from pathlib import Path
import pytest
import re


TEST_DB_PATH = Path(Path(__file__).parent, "test.db")


@pytest.fixture
def test_engine(scope="session") -> Generator[Engine, None, None]:
    engine = create_engine(f"sqlite:///{TEST_DB_PATH}")
    dec_base.metadata.create_all(bind=engine)
    with Session(engine) as ses:
        ses.execute(insert(tbl_clientes).values(mock_data.customers))
        ses.execute(insert(tbl_transacoes).values(mock_data.transactions))
        ses.commit()
    yield engine
    engine.dispose()
    TEST_DB_PATH.unlink(missing_ok=True)


def test_test_db(test_engine):
    """Tests if the test database is accessible and contains data."""
    with Session(bind=test_engine) as ses:
        n_customers = ses.execute(
            select(func.count()).select_from(tbl_clientes)
        ).scalar_one()
        n_transactions = ses.execute(
            select(func.count()).select_from(tbl_transacoes)
        ).scalar_one()
        assert len(mock_data.customers) == n_customers
        assert len(mock_data.transactions) == n_transactions


def test_fill_and_clear_customer():
    """Tests if `tbl_clientes` can fill values correctly."""
    customer = tbl_clientes()
    customer.fill(tbl_clientes(PrimeiroNome="John", Sobrenome="Doe"))
    assert customer.Id is None
    assert customer.PrimeiroNome == "John"
    assert customer.Sobrenome == "Doe"
    customer.clear()
    assert customer.PrimeiroNome is None
    assert customer.Sobrenome is None


def test_fill_and_clear_transaction():
    """Tests if `tbl_transacoes` can fill values correctly."""
    transaction = tbl_transacoes()
    transaction.fill(tbl_transacoes(Valor=123, DataTransac=date(2020, 11, 30)))
    assert transaction.Id is None
    assert transaction.Valor == 123
    assert transaction.DataTransac == date(2020, 11, 30)
    transaction.clear()
    assert transaction.Valor is None
    assert transaction.DataTransac is None


def test_read_customer(test_engine):
    """Tests if customer data is being correctly read from the database."""
    with Session(bind=test_engine) as ses:
        stmt = select(tbl_clientes).where(tbl_clientes.Id == 1)
        dbcustomer = ses.execute(stmt).first()[0]
        pycustomer = tbl_clientes()
        pycustomer.read(row_id=1, engine=test_engine)
    assert dbcustomer.Id == pycustomer.Id
    for name, value in pycustomer.data.items():
        assert getattr(dbcustomer, name) == value
    # check if Id is being reset on clear
    pycustomer.clear()
    assert pycustomer.Id is None


def test_read_transaction(test_engine):
    """Tests if transaction data is being correctly read from the database."""
    with Session(bind=test_engine) as ses:
        stmt = select(tbl_transacoes).where(tbl_transacoes.Id == 1)
        dbtransac = ses.execute(stmt).first()[0]
        pytransac = tbl_transacoes()
        pytransac.read(row_id=1, engine=test_engine)
    assert dbtransac.Id == pytransac.Id
    for name, value in pytransac.data.items():
        assert getattr(dbtransac, name) == value
    # check if Id is being reset on clear
    pytransac.clear()
    assert pytransac.Id is None


def test_update_customer(test_engine):
    """Tests if customer data is being correctly updated on the database."""
    customer = tbl_clientes()
    customer.read(row_id=1, engine=test_engine)
    customer.PrimeiroNome = "John"
    customer.Sobrenome = "doe wilson"
    customer.update(engine=test_engine)
    # check if Sobrenome was formmatted after calling `update`
    assert customer.Sobrenome == "Doe Wilson"
    with Session(bind=test_engine) as ses:
        stmt = select(tbl_clientes).where(tbl_clientes.Id == 1)
        db_customer = ses.execute(stmt).first()[0]
        assert db_customer.PrimeiroNome == "John"
        assert db_customer.Sobrenome == "Doe Wilson"


def test_write_customer(test_engine):
    """Tests if customer data is being correctly written to the database."""
    customer = get_default_customer()
    with pytest.raises(exc.StatementError):
        customer.write(engine=test_engine)
    customer.PrimeiroNome = "Novo Cliente"
    customer.Sobrenome = "de teste"
    # should not raise here
    customer.write(engine=test_engine)
    # check this customer exists
    with Session(bind=test_engine) as ses:
        stmt = (
            select(tbl_clientes)
            .where(tbl_clientes.PrimeiroNome == "Novo Cliente")
            .where(tbl_clientes.Sobrenome == "De Teste")
        )
        db_customer = ses.execute(stmt).first()
        assert db_customer is not None


def test_write_transaction(test_engine):
    """Tests if transaction data is being correctly written to the database."""
    transac = tbl_transacoes()
    with pytest.raises(exc.StatementError):
        transac.write(engine=test_engine)
    transac.DataTransac = date(1999, 12, 31)
    transac.Valor = 123123123
    # should not raise here
    transac.write(engine=test_engine)
    # check this transaction exists
    with Session(bind=test_engine) as ses:
        stmt = (
            select(tbl_transacoes)
            .where(tbl_transacoes.DataTransac == date(1999, 12, 31))
            .where(tbl_transacoes.Valor == 123123123)
        )
        db_transac = ses.execute(stmt).first()
        assert db_transac is not None


def test_searchable_paginated_data_source(test_engine):
    """Test if a paginated and/or searchable data source behaves accordingly."""
    source = CustomerListSource(engine=test_engine)
    # test current data length and format
    assert len(source.current_data) <= settings.data_tables_rows_per_page
    assert source.nrows >= source.max_idx
    assert source.current_data[0]._fields == ("Id", "Name", "Place")
    # test properties
    assert source.is_paginated()
    assert source.is_searchable()
    # test page navigation
    assert source.current_page == 1  # starts on page 1
    source.fetch_next_page()
    if source.min_idx > 1:
        # page changed if the indexes changed
        assert source.current_page == 2
    else:
        assert source.current_page == 1
    source.fetch_previous_page()
    assert source.current_page == 1
    # test search
    source.search_text = "José Silva"
    for row in source.current_data:
        assert ("José" in row.Name) or ("Silva" in row.Name)


def test_not_searchable_data_source(test_engine):
    """Test if a not searchable data source behaves accordingly."""
    source = TransactionBalanceSource(engine=test_engine)
    assert not source.is_searchable()
    with pytest.raises(AttributeError):
        source._search_text
    assert source.search_text == ""
    # assigning search_text should be no-op
    source.search_text = "New customized search"
    assert source.search_text == ""


def test_multiple_timings(test_engine):
    """Test special data sources that trasforms data by time grouping."""
    source = TransactionBalanceSource(engine=test_engine)
    # default format is 'm'
    # setting a higher frequency should return more rows
    n_m = source.nrows
    source.update_date_format("w")
    n_w = source.nrows
    source.update_date_format("d")
    n_d = source.nrows
    assert n_m <= n_w
    assert n_w <= n_d
    # test date format is correct
    assert source.current_data[0]._fields == ("Date", "Sums", "Deductions", "Balance")
    # this block should not raise
    source.update_date_format("m")
    cdate = source.current_data[0].Date
    datetime.strptime(cdate, "%Y-%m")
    source.update_date_format("w")
    cdate = source.current_data[0].Date
    datetime.strptime(cdate, "%Y-%W")
    source.update_date_format("d")
    cdate = source.current_data[0].Date
    datetime.strptime(cdate, "%Y-%m-%d")


def test_validated_data(test_engine):
    """Test `cashd.data.ValidatedData` properties."""
    customer = tbl_clientes()
    customer.read(row_id=1, engine=test_engine)
    # all columns except "Id" should be available on `data`
    colnames = tbl_clientes.__table__.c.keys()
    colnames.remove("Id")
    assert list(customer.data.keys()) == colnames
    # data should match values on read row
    with Session(bind=test_engine) as ses:
        stmt = select(tbl_clientes).where(tbl_clientes.Id == 1)
        rowdata = ses.execute(stmt).first()[0]
        for name in customer.data.keys():
            assert getattr(rowdata, name) == customer.data[name]
    # check if display names are correct
    for name in customer.data.keys():
        assert customer._display_name(name) == customer.display_names[name]
    # check if data types are correct
    for name in customer.data.keys():
        assert customer.types[name] == type(customer.__table__.c[name].type)


@pytest.mark.parametrize(argnames=("row_id"), argvalues=[i for i in range(1, 30)])
def test_customer_special_properties(row_id, test_engine):
    """Check if `tbl_clientes` special properties follow the expected format."""
    customer = tbl_clientes()
    customer.read(row_id=row_id, engine=test_engine)
    assert type(customer.NomeCompleto) == str
    for attr_name in ["PrimeiroNome", "Sobrenome", "Apelido"]:
        attr_val = getattr(customer, attr_name, None)
        if attr_val:
            assert attr_val in customer.NomeCompleto
    assert type(customer.Local) == str
    for attr_name in ["Endereco", "Bairro", "Cidade", "Estado"]:
        attr_val = getattr(customer, attr_name, None)
        if attr_val:
            assert attr_val in customer.Local
    assert type(customer.Saldo) == str
    assert re.match(r"^\d+,\d{2}$", customer.Saldo) is not None
