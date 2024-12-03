# from tests.conftest import client, tribunal, city

# client = creat_app.test_client()


def test_index(client):
    response = client.get("/")
    assert response.status_code == 200
    # assert b"Hello, this is your BigQuery API!" in response.data


def test_get_tribunal_city_list(client, tribunal):
    response = client.get(f"/get_tribunal_city_list?tribunal={tribunal}")
    assert response.status_code == 200
    # Add more assertions to check the response data if needed


def test_get_past_auctions_by_tribunal(client, tribunal):
    response = client.get(
        f"/get_auctions_by_tribunal?tribunal={tribunal}&past_or_future=past"
    )
    assert response.status_code == 200
    # Add more assertions to check the response data if needed


def test_get_future_auctions_by_tribunal(client, tribunal):
    response = client.get(
        f"/get_auctions_by_tribunal?tribunal={tribunal}&past_or_future=future"
    )
    assert response.status_code == 200
    # Add more assertions to check the response data if needed


def test_get_past_auctions_by_tribunal_date(client, tribunal):
    response = client.get(
        f"/get_auctions_by_date?tribunal={tribunal}&past_or_future=past"
    )
    assert response.status_code == 200
    # Add more assertions to check the response data if needed


def test_get_future_auctions_by_tribunal_date(client, tribunal):
    response = client.get(
        f"/get_auctions_by_date?tribunal={tribunal}&past_or_future=future"
    )
    assert response.status_code == 200
    # Add more assertions to check the response data if needed


def test_get_adress_by_city(client, city):
    response = client.get(f"/get_adress_by_city?commune={city}")
    assert response.status_code == 200
    # Add more assertions to check the response data if needed


def test_get_cities(client):
    response = client.get("/get_cities")
    assert response.status_code == 200
    # Add more assertions to check the response data if needed


# def test_get_transactions_stats(client, city, adress):
#     response = client.get(f"/get_transactions_stats?commune={city}&adresse={adress}")
#     assert response.status_code == 200
def test_get_transactions_stats(client, city_full, type_local):
    response = client.get(
        f"/get_transactions_stats?commune={city_full}&type_local={type_local}"
    )
    assert response.status_code == 200
    # Add more assertions to check the response data if needed


def test_get_city_analytics(client, city):
    response = client.get(f"/get_city_analytics?commune={city}")
    assert response.status_code == 200
    # Add more assertions to check the response data if needed


def test_get_transactions_details(client, city, adress):
    response = client.get("/get_transactions_details?commune={city}&adresse={adress}")
    assert response.status_code == 200
    # Add more assertions to check the response data if needed


def test_get_auctions_url(client):
    response = client.get("/get_auctions_url?past_or_future=future")
    assert response.status_code == 200
    # Add more assertions to check the response data if needed


def test_get_past_auctions_url(client):
    response = client.get("/get_auctions_url?past_or_future=past")
    assert response.status_code == 200
    # Add more assertions to check the response data if needed


def test_get_future_auctions_url(client):
    response = client.get("/get_auctions_url?past_or_future=future")
    assert response.status_code == 200
    # Add more assertions to check the response data if needed


def get_historique_volumes_pieces(client, city, type_local):
    response = client.get(
        f"/get_historique_volumes_pieces?commune={city}&type_local={type_local}"
    )
    assert response.status_code == 200


def get_historique_volumes_surfaces(client, city, type_local):
    response = client.get(
        f"/get_historique_volumes_surfaces?commune={city}&type_local={type_local}"
    )
    assert response.status_code == 200


def get_historique_prix_m2_pieces(client, city, type_local):
    response = client.get(
        f"/get_statistiques_pieces?commune={city}&type_local={type_local}"
    )
    assert response.status_code == 200


def get_distributions_decotes(client, city_full):
    response = client.get(f"/get_distributions_decotes?commune={city_full}")
    assert response.status_code == 200


def get_scoring_voies(client, city_full):
    response = client.get(f"/get_scoring_voies?commune={city_full}")
    assert response.status_code == 200
