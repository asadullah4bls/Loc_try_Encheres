import re
import logging


def build_text_surfaces(historique_volumes_surfaces):

    # historique_volumes_surfaces = get_historique_volumes_surfaces(criteria)

    historique_volumes_surfaces["meanBySurface"] = historique_volumes_surfaces.iloc[
        :, 1:
    ].mean(axis=1)

    historique_volumes_surfaces["meanGlobal"] = historique_volumes_surfaces.iloc[
        :, -1
    ].mean()

    # historique_volumes_surfaces = historique_volumes_surfaces[
    #     historique_volumes_surfaces.meanBySurface
    #     > historique_volumes_surfaces.meanGlobal * 0.5
    # ]

    historique_volumes_surfaces["ranking"] = historique_volumes_surfaces[
        "meanBySurface"
    ].rank(pct=False)
    historique_volumes_surfaces = historique_volumes_surfaces[
        historique_volumes_surfaces.ranking > historique_volumes_surfaces.shape[0] - 3
    ]

    if historique_volumes_surfaces.shape[0] > 3:
        historique_volumes_surfaces = historique_volumes_surfaces[:3]

    surfaces_names = historique_volumes_surfaces.Surface.to_list()
    surfaces_means = historique_volumes_surfaces.meanBySurface.to_list()
    surfaces_means = [int(x) for x in surfaces_means]
    max_surface = historique_volumes_surfaces[
        historique_volumes_surfaces.meanBySurface
        == historique_volumes_surfaces.meanBySurface.max()
    ].Surface
    max_surface = max_surface.values[0]

    if historique_volumes_surfaces.shape[0] == 3:
        text = f"""* Les surfaces {surfaces_names[0]}, {surfaces_names[1]} et
          {surfaces_names[2]} dominent le marché, avec une moyenne respective d'environ {max(1,surfaces_means[0])}, {max(1,surfaces_means[1])} et {max(1,surfaces_means[2])} ventes par an
          ; les biens de {max_surface} étant les plus vendus.""".replace(
            "\n", ""
        )

    elif historique_volumes_surfaces.shape[0] == 2:
        text = f"""* Les surfaces {surfaces_names[0]}
         et {surfaces_names[1]} dominent le marché, avec une moyenne respective d'environ {max(1,surfaces_means[0])} et {max(1,surfaces_means[1])} ventes par an
        ; les biens de {max_surface} étant les plus vendus.""".replace(
            "\n", ""
        )

    elif historique_volumes_surfaces.shape[0] == 1:
        text = f"""* Les surfaces {surfaces_names[0]} dominent le marché, avec une moyenne d'environ {max(1,surfaces_means[0])} ventes par an."""
    text = text.replace("\n", "")
    text = re.sub(r"\s+", " ", text)
    return text


def build_text_pieces(historique_volumes_pieces):

    # historique_volumes_pieces = get_historique_volumes_pieces(criteria)

    # historique_volumes_pieces.nb_pieces = historique_volumes_pieces.nb_pieces.apply(lambda p: p.replace('ie', 'iè'))

    historique_volumes_pieces["meanBySurface"] = historique_volumes_pieces.iloc[
        :, 1:
    ].mean(axis=1)

    historique_volumes_pieces["meanGlobal"] = historique_volumes_pieces.iloc[
        :, -1
    ].mean()

    # historique_volumes_pieces = historique_volumes_pieces[
    #     historique_volumes_pieces.meanBySurface
    #     > historique_volumes_pieces.meanGlobal * 0.8
    # ]

    historique_volumes_pieces["ranking"] = historique_volumes_pieces[
        "meanBySurface"
    ].rank(pct=False)
    historique_volumes_pieces = historique_volumes_pieces[
        historique_volumes_pieces.ranking > historique_volumes_pieces.shape[0] - 3
    ]

    if historique_volumes_pieces.shape[0] > 3:
        historique_volumes_pieces = historique_volumes_pieces[:3]

    surfaces_names = historique_volumes_pieces.nb_pieces.to_list()
    surfaces_means = historique_volumes_pieces.meanBySurface.to_list()
    surfaces_means = [int(x) for x in surfaces_means]
    max_surface = historique_volumes_pieces[
        historique_volumes_pieces.meanBySurface
        == historique_volumes_pieces.meanBySurface.max()
    ].nb_pieces
    max_surface = max_surface.values[0]

    if historique_volumes_pieces.shape[0] == 3:
        text = f"""* Les biens de type {surfaces_names[0]}, {surfaces_names[1]} et
          {surfaces_names[2]} dominent le marché, avec une moyenne respective d'environ {max(1,surfaces_means[0])}, {max(1,surfaces_means[1])} et {max(1,surfaces_means[2])} ventes par an
         ; les biens de type {max_surface} étant les plus vendus."""

    elif historique_volumes_pieces.shape[0] == 2:
        text = f"""* Les biens de type {surfaces_names[0]} et
          {surfaces_names[1]} dominent le marché, avec une moyenne respective d'environ {max(1,surfaces_means[0])} et {max(1,surfaces_means[1])} ventes par an
        ; les biens de type {max_surface} étant les plus vendus."""

    elif historique_volumes_pieces.shape[0] == 1:
        text = f"""* Les biens de type {surfaces_names[0]} dominent le marché, avec une moyenne d'environ {max(1,surfaces_means[0])} ventes par an."""
    text = text.replace("\n", "").replace("piece", "pièce")
    text = re.sub(r"\s+", " ", text)
    return text


def build_text_prix(analytics):
    try:
        delta = round(
            (analytics.prix_m2_c50[len(analytics) - 1] / analytics.prix_m2_c50[0] - 1)
            * 100,
            2,
        )
    except Exception as e:
        logging.debug(f"An error occurred when computing delta : {e}")
        delta = 0

    try:
        delta_1 = round(
            (
                analytics.prix_m2_c50[len(analytics) - 1]
                / analytics.prix_m2_c50[len(analytics) - 2]
                - 1
            )
            * 100,
            2,
        )
    except Exception as e:
        logging.debug(f"An error occurred when computing delta_1 : {e}")
        delta_1 = 0

    try:
        delta_2 = round(
            (
                analytics.prix_m2_c50[len(analytics) - 2]
                / analytics.prix_m2_c50[len(analytics) - 3]
                - 1
            )
            * 100,
            2,
        )
    except Exception as e:
        logging.debug(f"An error occurred when computing delta_2 : {e}")
        delta_2 = 0

    try:
        delta_5 = round(
            (
                analytics.prix_m2_c50[len(analytics) - 1]
                / analytics.prix_m2_c50[len(analytics) - 5]
                - 1
            )
            * 100,
            2,
        )
    except Exception as e:
        logging.debug(f"An error occurred when computing delta_5 : {e}")
        delta_5 = 0
    # delta_1 = f'{delta_1}%'
    mean_volume = int(analytics.Volume_c.mean())
    # delta, delta_5, delta_1, delta_2 # , mean_volume
    if mean_volume >= 30:
        text = f"""* Evolution du prix médian : {delta}% sur la période, {delta_5}% sur 5 ans, {delta_1}% sur 1 an."""
        if (delta_1 < delta_2) and (delta_1 > 0) and (delta_2 > 0):
            text += (
                """ Ralentissement de la croissance des prix sur la dernière année."""
            )
        elif (delta_1 > delta_2) and (delta_1 > 0) and (delta_2 > 0):
            text += """ Légère accélération de la croissance des prix sur la dernière année."""
        elif (abs(delta_1) < abs(delta_2)) and (delta_1 < 0) and (delta_2 < 0):
            text += """ Ralentissement de la chute des prix sur la dernière année."""
        elif (abs(delta_1) > abs(delta_2)) and (delta_1 < 0) and (delta_2 < 0):
            text += (
                """ Légère accélération de la chute des prix sur la dernière année."""
            )
        text = text.replace("0%", "non disponible")
        return text
    return "* Volume de ventes insuffisant sur la période"


# build_text_prix(analytics)
