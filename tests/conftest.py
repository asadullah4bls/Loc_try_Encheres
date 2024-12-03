import pytest

from app import creat_app


@pytest.fixture
def client():
    # app = creat_app({"TESTING": True})
    app = creat_app()
    app.config.update(
        {
            "TESTING": True,
        }
    )
    with app.test_client() as client:
        yield client


@pytest.fixture
def city():
    yield "PARIS"


@pytest.fixture
def city_full():
    yield "PARIS 16"


@pytest.fixture
def tribunal():
    yield "PARIS"


@pytest.fixture
def type_local():
    yield "Appartement"


@pytest.fixture
def adress():
    yield "GAMB"
