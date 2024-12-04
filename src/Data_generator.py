from .utility import log_execution_time
import os
import requests
import pandas as pd

# import numpy as np
# import datetime

base_url = "https://api-data-immo-yudqj273iq-uc.a.run.app"


# base_url = os.environ["BASE_URL"]


def get_libelle_piece(piece):
    if piece == 0:
        return "Studio"
    elif piece == 1:
        return "1 piece"
    elif piece > 1:
        return f"{piece} pieces"


def build_url(base_url, endpoint, criteria=None):
    url = f"{base_url}/{endpoint}?"

    if criteria:
        for k, v in criteria.items():
            # print(url)
            if v:
                if type(v) == str:
                    if url[-1] == "?":
                        url += f'{k}={v.replace(" ","%20")}'
                    else:
                        url += f'&{k}={v.replace(" ","%20")}'
                else:
                    url += f"&{k}={v}"
        # print(url)
    return url


@log_execution_time
def get_stats(url):
    # print(url)
    data = requests.get(url)
    # print(data.json())
    df = pd.json_normalize(data.json(), "data")
    return df


@log_execution_time
def get_transactions_stats(criteria):
    url = build_url(
        base_url=base_url, endpoint="get_transactions_stats", criteria=criteria
    )
    analytics = get_stats(url)
    return analytics


@log_execution_time
def get_historique_volumes_pieces(criteria):
    url = build_url(
        base_url=base_url, endpoint="get_historique_volumes_pieces", criteria=criteria
    )
    requests.get(url)
    historique_volumes_pieces = get_stats(url)
    historique_volumes_pieces = historique_volumes_pieces.iloc[:, 1:].fillna(0)
    historique_volumes_pieces.columns = [
        c.replace("_", "") if "nb" not in c else c
        for c in historique_volumes_pieces.columns
    ]
    historique_volumes_pieces = historique_volumes_pieces.sort_values(
        by="nb_pieces", ascending=True
    )
    historique_volumes_pieces.nb_pieces = historique_volumes_pieces.nb_pieces.apply(
        get_libelle_piece
    )
    return historique_volumes_pieces


@log_execution_time
def get_historique_volumes_surfaces(criteria):
    url = build_url(
        base_url=base_url, endpoint="get_historique_volumes_surfaces", criteria=criteria
    )
    requests.get(url)
    historique_volumes_surfaces = get_stats(url)
    historique_volumes_surfaces = historique_volumes_surfaces.iloc[:, 1:].fillna(0)
    historique_volumes_surfaces.columns = [
        c.replace("_", "") if "nb" not in c else c
        for c in historique_volumes_surfaces.columns
    ]

    # historique_prix_m2_pieces.nb_pieces = historique_prix_m2_pieces.nb_pieces.apply(get_libelle_piece)
    # Defined series to sort by
    defined_order = [
        "0m2 - 25m2",
        "25m2 - 35m2",
        "35m2 - 45m2",
        "45m2 - 65m2",
        "65m2 - 80m2",
        "80m2 - 100m2",
        "100m2 - 150m2",
        "150m2 - 175m2",
        "175m2 - 200m2",
        "> 200m2",
    ]

    # Set the Surface column as a categorical type with the defined order
    # historique_prix_m2_pieces["Surface"] = historique_prix_m2_pieces.Categorical(
    #     historique_prix_m2_pieces["Surface"], categories=defined_order, ordered=True
    # )
    historique_volumes_surfaces["Surface"] = pd.Categorical(
        historique_volumes_surfaces["Surface"], categories=defined_order, ordered=True
    )

    # Sort the DataFrame based on the 'Surface' column
    historique_volumes_surfaces = historique_volumes_surfaces.sort_values(
        "Surface"
    ).reset_index(drop=True)

    return historique_volumes_surfaces


@log_execution_time
def get_historique_prix_m2_pieces(criteria):
    url = build_url(
        base_url=base_url, endpoint="get_historique_prix_m2_pieces", criteria=criteria
    )
    historique_prix_m2_pieces = get_stats(url)
    historique_prix_m2_pieces = historique_prix_m2_pieces.iloc[:, 1:].fillna(0)
    historique_prix_m2_pieces.columns = [
        c.replace("_", "") if "nb" not in c else c
        for c in historique_prix_m2_pieces.columns
    ]
    return historique_prix_m2_pieces


@log_execution_time
def get_distributions_decotes(criteria):
    url = build_url(
        base_url=base_url, endpoint="get_distributions_decotes", criteria=criteria
    )
    distributions_decotes = get_stats(url)
    if distributions_decotes.empty:
        distributions_decotes = pd.DataFrame(
            0, index=range(3), columns=["Commune", "Decote_prix_median", "Cum_percent"]
        )
        # distributions_decotes = pd.DataFrame(0, columns=df.columns)
    else:
        distributions_decotes = distributions_decotes.iloc[:, 1:].fillna(0)
    return distributions_decotes


@log_execution_time
def get_scoring_voies(criteria):
    url = build_url(base_url=base_url, endpoint="get_scoring_voies", criteria=criteria)
    #print("the m url",url)
    scoring_voies = get_stats(url)
    # print("df start",scoring_voies)
    scoring_voies = scoring_voies.iloc[:, 1:].fillna(0)
    # print("df after",scoring_voies)
    # Define the CSV file path
    # csv_file_path = os.path.join(REPORTS_DIR, 'data_report.csv')

    # Save DataFrame to CSV
    # scoring_voies.to_csv(csv_file_path, index=False)
    return scoring_voies


@log_execution_time
def get_cities():
    url = build_url(base_url=base_url, endpoint="get_cities")
    cities = requests.get(url).json()
    cities = [c["city"] for c in cities]
    return cities


@log_execution_time
def get_annee_max():
    url = build_url(base_url=base_url, endpoint="get_annee_max")
    annee_max = requests.get(url).json()
    # cities = [c['city'] for c in cities]
    return annee_max
