import os
from datetime import date
from dotenv import load_dotenv
from google.cloud import bigquery
from google.oauth2 import service_account

load_dotenv()


today = date.today()
today = str(today).replace("-", "_")

ENV = os.getenv("ENV")


class BQ_MANAGER:
    def __init__(self):
        if ENV == "dev_local":
            # self.key_path_bq = os.getenv("GOOGLE_BIG_QUERY_CREDENTIALS_PATH")
            pass

        self.project_id = os.getenv("GCP_project_id")
        self.dataset_id = os.getenv("BQ_dataset_id")
        self.credential_scope = os.getenv("BQ_Credential_scope")

        self.table_ventes_id = os.getenv("BQ_table_ventes_id")
        self.table_ventes = (
            f"{self.project_id}.{self.dataset_id}.{self.table_ventes_id}"
        )

        self.table_past_auctions_id = os.getenv("BQ_table_past_auctions_id")
        self.past_auctions_table = (
            f"{self.project_id}.{self.dataset_id}.{self.table_past_auctions_id}"
        )

        self.table_future_auctions_id = os.getenv("BQ_table_future_auctions_id")
        self.future_auctions_table = (
            f"{self.project_id}.{self.dataset_id}.{self.table_future_auctions_id}"
        )

        self.vue_villes_id = os.getenv("BQ_vue_villes")
        self.vue_villes = f"{self.project_id}.{self.dataset_id}.{self.vue_villes_id}"

        if ENV == "dev_local":
            self.credentials = service_account.Credentials.from_service_account_file(
                self.key_path_bq,
                scopes=[self.credential_scope],
            )

            self.client = bigquery.Client(
                credentials=self.credentials, project=self.credentials.project_id
            )
        else:
            self.client = bigquery.Client()

        # self.gcs_manager = GCS_manager.GCS_MANAGER()

    def get_auctions_url(self, past_or_future: bool):
        if past_or_future == "past":
            auctions_table = self.past_auctions_table

        elif past_or_future == "future":
            auctions_table = self.future_auctions_table

        sql = f"""
                            SELECT link
                            FROM {auctions_table}
                            """

        query_job = self.client.query(sql)
        df = query_job.result().to_dataframe()
        return df.link.to_list()

    def get_tribunal_city_list(self, tribunal: str):
        """

        get future auctions city list by tribunal

        """
        sql = f"""  
                SELECT DISTINCT city
                FROM {self.future_auctions_table}
                WHERE tribunal = "{tribunal}"
                ORDER BY city ASC;
                """
        # print(sql)
        query_job = self.client.query(sql)
        df = query_job.result().to_dataframe()

        return df.city.to_list()

    def get_auctions_by_tribunal(self, tribunal: str, past_or_future: bool):
        if past_or_future == "past":
            auctions_table = self.past_auctions_table

        elif past_or_future == "future":
            auctions_table = self.future_auctions_table

        tribunal_city_list = self.get_tribunal_city_list(tribunal)

        sql = f"""  
                    SELECT *
                    FROM {auctions_table}
                    WHERE City IN {tuple(tribunal_city_list)}
                    ORDER BY publication_date
                """
        query_job = self.client.query(sql)
        df = query_job.result().to_dataframe()
        return df

    def get_auctions_by_date(self, tribunal: str, past_or_future: bool):
        if past_or_future == "past":
            auctions_table = self.past_auctions_table

        elif past_or_future == "future":
            auctions_table = self.future_auctions_table

        tribunal_city_list = self.get_tribunal_city_list(tribunal)

        sql = f"""  
                SELECT auction_date, COUNT(auction_date) as date_enchere
                FROM {auctions_table}
                WHERE City IN {tuple(tribunal_city_list)}
                --ORDER BY publication_date
                GROUP BY auction_date
            """

        # print(sql)
        query_job = self.client.query(sql)
        df = query_job.result().to_dataframe()
        df.columns = ["date", "volume"]
        df.sort_values(by=["date"], inplace=True)
        return df

    def get_transactions_stats(
        self,
        commune: str,
        adresse: str = None,
        semestre: int = None,
        type_local: str = None,
        nombre_pieces: int = None,
        surface_min: float = None,
        surface_max: float = None,
    ):
        sql = f'''
                SELECT Annee AS annee, 
                AVG(Nombre_pieces_principales) AS nb_pieces, 
                AVG(Surface_reelle_bati) AS surface, 
                AVG(Surface_terrain) AS surface_terrain, 
                AVG(Valeur_fonciere) AS prix, 
                AVG(prix_m2) AS prix_au_m2, 
                COUNT(Valeur_fonciere) AS nb_transactions
                FROM {self.table_ventes}
                WHERE Commune = "{commune}"'''

        if semestre:
            sql += f"\nAND Semestre = {semestre}"

        if type_local:
            sql += f'\nAND Type_local = "{type_local}"'

        if nombre_pieces:
            sql += f"\nAND Nombre_pieces_principales = {nombre_pieces}"

        if surface_min:
            sql += f"\nAND Surface_reelle_bati >= {surface_min}"

        if surface_max:
            sql += f"\nAND Surface_reelle_bati <= {surface_max}"

        if adresse:
            sql += f'\nAND Adresse LIKE "%{adresse}%"'

        sql += "\nGROUP BY Annee"

        print(sql)
        query_job = self.client.query(sql)
        df = query_job.result().to_dataframe()

        df.sort_values(by=["annee"], inplace=True)
        df.set_index("annee", inplace=True)

        return df

    def get_adress_by_city(self, commune: str):
        sql = f"""
                SELECT DISTINCT
                    regexp_replace(REPLACE(Adresse, Commune, ''), '[0-9]', '') voie,
                    regexp_extract(Adresse, '[0-9]+') num,
                    Adresse AS adresse
                FROM {self.table_ventes}
                WHERE Commune = "{commune}"
                AND Adresse IS NOT NULL
                ORDER BY voie ASC, num
                """

        query_job = self.client.query(sql)
        df = query_job.result().to_dataframe()

        df.sort_values(by=["adresse"], inplace=True)

        return df

    def get_cities(self):
        sql = f"""
                SELECT DISTINCT Commune AS commune
                FROM {self.vue_villes}
                ORDER BY Commune ASC
                """
        sql = f"""
                SELECT city
                FROM {self.vue_villes}
                ORDER BY city ASC
                """

        query_job = self.client.query(sql)
        df = query_job.result().to_dataframe()

        return df

    def get_transactions_details(
        self,
        commune: str,
        adresse: str = None,
        semestre: int = None,
        type_local: str = None,
        nombre_pieces: int = None,
        surface_min: float = None,
        surface_max: float = None,
        limit: int = None,
    ):
        sql = f'''SELECT * 
                    FROM {self.table_ventes}
                    WHERE Commune = "{commune}"'''

        if semestre:
            sql += f"\nAND Semestre = {semestre}"

        if type_local:
            sql += f'\nAND Type_local = "{type_local}"'

        if nombre_pieces:
            sql += f"\nAND Nombre_pieces_principales = {nombre_pieces}"

        if surface_min:
            sql += f"\nAND Surface_reelle_bati >= {surface_min}"

        if surface_max:
            sql += f"\nAND Surface_reelle_bati <= {surface_max}"

        if adresse:
            sql += f'\nAND Adresse LIKE "%{adresse}%"'

        if limit:
            sql += f"\nLIMIT {limit}"

        print(sql)
        query_job = self.client.query(sql)
        df = query_job.result().to_dataframe()
        df.sort_values(by=["Date_mutation"], inplace=True)

        return df

    def get_city_analytics(self, commune: str, group_by_local_type=True):
        # if transactions_ou_stats=='stats':
        sql = f"""
                SELECT Annee AS annee,
                Type_local AS type_bien,
                CAST(AVG(Nombre_pieces_principales) AS INT64) AS nb_pieces,
                AVG(Surface_reelle_bati) AS surface, 
                AVG(Surface_terrain) AS surface_terrain, 
                AVG(Valeur_fonciere) AS prix_moyen,
                APPROX_QUANTILES(Valeur_fonciere, 100)[OFFSET(50)] AS prix_median,
                APPROX_QUANTILES(Valeur_fonciere, 100)[OFFSET(75)]  AS prix_haut,
                APPROX_QUANTILES(Valeur_fonciere, 100)[OFFSET(25)]  AS prix_bas,
                AVG(prix_m2) AS prix_au_m2_moyen,
                APPROX_QUANTILES(prix_m2, 100)[OFFSET(50)] AS prix_au_m2_median,
                APPROX_QUANTILES(prix_m2, 100)[OFFSET(75)]  AS prix_au_m2_haut,
                APPROX_QUANTILES(prix_m2, 100)[OFFSET(25)]  AS prix_au_m2_bas,
                COUNT(Valeur_fonciere) AS nb_transactions
                FROM {self.table_ventes}
                WHERE Commune = "{commune}"
                        """
        if group_by_local_type:
            sql += "\nGROUP BY Annee, Type_local"
        else:
            sql += "\nGROUP BY Annee"
        print(sql)
        query_job = self.client.query(sql)
        df = query_job.result().to_dataframe()
        df.sort_values(by=["annee"], inplace=True)
        df.set_index("annee", inplace=True)

        return df
