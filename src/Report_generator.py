from .utility import log_execution_time
from .Excel_Utility import (
    getCellsRef,
    # add_horizontal_border,
    # add_vertical_border,
    cell_format,
    apply_worksheet_with_basic_format,
    add_title,
    write_text,
    add_creteria,
    build_metrics_text,
)

from .Text_Utility import (
    build_text_surfaces,
    build_text_pieces,
    build_text_prix,
)

import pandas as pd
import numpy as np

# import xlsxwriter
from xlsxwriter.utility import xl_rowcol_to_cell

import glob
import os

# import logging


class REPORT_BUILDER:
    def __init__(
        self,
        df_stats,
        df_volumes_pieces,
        df_volumes_surfaces,
        df_prix_m2_pieces,
        df_distributions_decotes,
        df_scoring,
        # user_logo,
        # user_website,
        color_palette,
        criteria,
        report_name="Raport",
        prix_marche=200000,
        taux_frais=0.15,
        taux_travaux=0.1,
        bbg_color="#73a1b2",
        info_font_color="#9da19e",
        selection_color="#d99795",
    ):

        self.df_stats = df_stats
        self.df_volumes_pieces = df_volumes_pieces
        self.df_prix_m2_pieces = df_prix_m2_pieces
        self.criteria = criteria
        self.prix_marche = prix_marche
        self.cible_decote = 0.6
        self.mise_a_prix = prix_marche * 0.15
        self.taux_travaux = taux_travaux
        self.taux_frais = taux_frais
        self.color_palette = color_palette
        self.selection_color = selection_color

        self.path_disclaimer = os.path.abspath(
            "static/contents/disclaimer/disclaimer.txt"
        )
        self.disclaimer = open(f"{self.path_disclaimer}")
        self.path_logos = "static/contents/logos/"
        self.logos = [logo for logo in glob.glob(self.path_logos + "*.png")]
        self.url_logos = [open(e.replace("png", "txt")).read() for e in self.logos]
        # self.path_avocat = "static/contents/avocat/"
        # self.logo_avocat = f"{self.path_avocat}Logo_Cabinet_Avocat.png"
        # self.logo_avocat = (user_logo,)
        # self.url_avocat = open(self.logo_avocat.replace("png", "txt")).read()
        # self.url_avocat = (user_website,)
        self.cible_decote = 0.6

        self.writer = pd.ExcelWriter(f"reports/{report_name}", engine="xlsxwriter")
        self.workbook = self.writer.book
        # self.work_book_name = "Report.xlsx"

        # --------------- NEW FORMAT ------------------
        self.bg_color = "#FFFFFF"
        self.chart_font_color = "black"
        self.font_name = "Cambria"

        self.border_width = 5  # Medium border width
        self.border_color = "#FFFFFF"  # #73a1b2 Dark blue border color

        self.title_font_size = 14
        self.title_fg_color = "#9da19e"  # #fa8448

        self.background_format = self.workbook.add_format(
            {
                "bg_color": self.bg_color,
                "font_color": self.bg_color,
                "font_name": self.font_name,
            }
        )
        self.white_background_format = self.workbook.add_format(
            {"bg_color": "white", "font_color": "white", "font_name": self.font_name}
        )

        self.info_fmt_bis = self.workbook.add_format(
            {
                "bold": True,
                "font_color": "white",
                "bg_color": self.bg_color,
                "font_name": self.font_name,
            }
        )

        self.format_diclaimer = self.workbook.add_format(
            {
                "bold": False,
                # 'font_color': self.info_font_color,
                "font_color": "white",
                "italic": True,
                "bg_color": self.bg_color,
                "font_name": self.font_name,
                "align": "center",
                "valign": "vcenter",
            }
        )

        self.link_format = self.workbook.add_format(
            {
                "bold": 1,
                "align": "center",
                "valign": "vcenter",
                "fg_color": self.bg_color,
                "font_color": "white",
                "font_name": self.font_name,
            }
        )

        self.basic_format = self.workbook.add_format(
            {
                "bg_color": "white",
                "font_color": self.bg_color,
                "font_name": self.font_name,
            }
        )

        self.gray_basic_format = self.workbook.add_format(
            {
                "bg_color": "#f2f2f2",
                "font_color": self.bg_color,
                "fg_color": "#f2f2f2",
                "font_name": self.font_name,
            }
        )

        # --------------- END NEW FORMAT ------------------

        self.bbg_color = bbg_color
        self.info_font_color = info_font_color
        self.neural_color = color_palette[-1]

        self.merge_format = self.workbook.add_format(
            {
                "bold": 1,
                "border": 0,
                "align": "center",
                "valign": "vcenter",
                "fg_color": self.bbg_color,
                "font_color": "white",
                "font_name": self.font_name,
            }
        )

        self.merge_format_neural = self.workbook.add_format(
            {
                "bold": 1,
                "border": 0,
                "align": "center",
                "valign": "vcenter",
                "fg_color": self.info_font_color,
                "font_color": "black",
                "font_name": self.font_name,
            }
        )

        # self.title_font_size = 20
        self.merge_format_neutral = self.workbook.add_format(
            {
                "bold": 1,
                "border": 0,
                "align": "center",
                "valign": "vcenter",
                # 'fg_color': self.bbg_color,
                "font_color": self.bbg_color,
                "font_size": int(self.title_font_size * 1.1),
                "fg_color": self.neural_color,
                "font_name": self.font_name,
            }
        )

        self.percent_fmt_locked = self.workbook.add_format(
            {"num_format": "0%", "align": "right", "valign": "vcenter", "locked": True}
        )

        self.percent_fmt_centered_locked = self.workbook.add_format(
            {"num_format": "0%", "align": "center", "valign": "vcenter", "locked": True}
        )

        self.info_fmt = self.workbook.add_format(
            {
                "bold": 1,
                # 'border': 1,
                "align": "left",
                "valign": "vcenter",
                "fg_color": self.bg_color,
                "font_color": "white",
                "locked": False,
                "font_name": self.font_name,
            }
        )

        # self.money_fmt = self.workbook.add_format(
        #     {"num_format": "# ##0 €", "align": "center"}
        # )
        # self.percent_fmt = self.workbook.add_format(
        #     {"num_format": "0%", "align": "center"}
        # )

        self.index_fmt = self.workbook.add_format(
            {
                "bold": False,
                "font_color": "white",
                "right": 5,
                "right_color": self.bbg_color,
                "font_name": self.font_name,
            }
        )

        # Define the format for the right border
        # self.right_border_format = self.workbook.add_format(
        #     {"right": 5, "right_color": self.bbg_color, "bg_color": "#215867"}
        # )

        # Define the format for the right border
        # self.left_border_format = self.workbook.add_format(
        #     {"left": 5, "left_color": self.bbg_color}
        # )
        # percent_fmt_unlocked = self.workbook.add_format({'num_format': '0%','align': 'right',
        #                                 'valign': 'vcenter', 'locked': False})
        # self.background_format = self.workbook.add_format({"bg_color": "#215867"})

        self.create_ws_accueil()
        self.create_ws_distrib_decotes(
            df=df_distributions_decotes.copy(), sheet_name="DECOTES"
        )
        self.create_ws_scoring(df=df_scoring, sheet_name="SCORING")

        self.create_ws_stat_pieces(df=df_volumes_pieces, sheet_name="VOLUMES_PIECES")
        self.create_ws_stat_pieces(
            df=df_volumes_surfaces, sheet_name="VOLUMES_SURFACES"
        )
        self.create_ws_stat_pieces(df=df_prix_m2_pieces, sheet_name="PRIX_PIECES")
        # self.create_ws_frais()
        self.create_ws_simulateur_2()
        self.create_ws_optimal_auction("ANALYSE SIMULATIONS")
        self.create_ws_simulateur()
        self.create_ws_liens("LIENS UTILES")

        self.writer.close()

    def set_border_format(self, border_color=None, bg_color=None):
        """Update the border colors for the formats."""

        if not border_color:
            border_color = self.border_color

        if not bg_color:
            bg_color = self.bg_color

        self.top_border_format = self.workbook.add_format(
            {
                "top": self.border_width,
                "top_color": border_color,  # Updated top color
                "bg_color": bg_color,  # Updated background color
            }
        )
        self.bottom_border_format = self.workbook.add_format(
            {
                "bottom": self.border_width,
                "bottom_color": border_color,
                "bg_color": bg_color,
            }
        )
        self.left_border_format = self.workbook.add_format(
            {
                "left": self.border_width,
                "left_color": border_color,
                "bg_color": bg_color,
            }
        )
        self.right_border_format = self.workbook.add_format(
            {
                "right": self.border_width,
                "right_color": border_color,
                "bg_color": bg_color,
            }
        )
        # self.right_top_corner_format = self.workbook.add_format(
        #     {
        #         "right": self.border_width,
        #         "right_color": border_color,
        #         "top": self.border_width,
        #         "top_color": border_color,
        #         "bg_color": bg_color,
        #     }
        # )
        # self.right_bottom_corner_format = self.workbook.add_format(
        #     {
        #         "right": self.border_width,
        #         "right_color": border_color,
        #         "bottom": self.border_width,
        #         "bottom_color": border_color,
        #         "bg_color": bg_color,
        #     }
        # )
        # self.left_top_corner_format = self.workbook.add_format(
        #     {
        #         "left": self.border_width,
        #         "left_color": border_color,
        #         "top": self.border_width,
        #         "top_color": border_color,
        #         "bg_color": bg_color,
        #     }
        # )
        # self.left_bottom_corner_format = self.workbook.add_format(
        #     {
        #         "left": self.border_width,
        #         "left_color": border_color,
        #         "bottom": self.border_width,
        #         "bottom_color": border_color,
        #         "bg_color": bg_color,
        #     }
        # )

    def set_title_format(self, fg_color=None, font_size=None, bold=None):

        if not fg_color:
            fg_color = self.title_fg_color

        if not bold:
            bold = 1

        if not font_size:
            font_size = self.title_font_size

        self.title_format = self.workbook.add_format(
            {
                "bold": bold,
                "border": 0,
                "align": "center",
                "valign": "vcenter",
                "fg_color": fg_color,
                "font_color": "white",
                "font_name": self.font_name,
                "font_size": font_size,
            }
        )

    def set_money_format(
        self, fg_color=None, font_size=None, font_color=None, bold=None, locked=None
    ):

        if not fg_color:
            fg_color = self.title_fg_color

        if not bold:
            bold = 1

        if not font_size:
            font_size = self.title_font_size

        if not font_color:
            font_color = self.bg_color

        if not locked:
            locked = True

        self.money_fmt = self.workbook.add_format(
            {
                "num_format": "# ##0 €",
                "align": "center",
                "fg_color": fg_color,
                "bold": bold,
                "font_color": font_color,
                "font_size": font_size,
                "font_name": self.font_name,
                "locked": locked,
            }
        )

    def set_percent_format(
        self, fg_color=None, font_size=None, font_color=None, bold=None
    ):

        if not fg_color:
            fg_color = self.title_fg_color

        if not bold:
            bold = 1

        if not font_size:
            font_size = self.title_font_size

        if not font_color:
            font_color = self.bg_color

        self.percent_fmt = self.workbook.add_format(
            {
                "num_format": "0%",
                "align": "center",
                "fg_color": fg_color,
                "bold": bold,
                "font_color": font_color,
                "font_size": font_size,
                "font_name": self.font_name,
            }
        )

    def draw_rectangle(self, worksheet, cellRef, border_color=None, bg_color=None):
        self.set_border_format(border_color, bg_color)
        (
            start_row,
            end_row,
            start_col,
            end_col,
            colRange,
            rowRange,
            top_left_corner,
            bottom_left_corner,
            top_right_corner,
            bottom_right_corner,
        ) = getCellsRef(cellRef=cellRef)

        if not bg_color:
            bg_format = self.background_format
        else:
            bg_format = self.workbook.add_format({"bg_color": bg_color})

        start_col_index = ord(start_col) - ord("A")
        end_col_index = ord(end_col) - ord("A")
        # Fill in the background for the full range (no borders)
        for row in range(start_row, end_row):
            for col in range(start_col_index, end_col_index):
                worksheet.write_blank(row, col, "", bg_format)

        # worksheet = add_horizontal_border(
        #     worksheet, row=start_row, colRange=colRange, format=self.top_border_format
        # )
        # worksheet = add_horizontal_border(
        #     worksheet, row=end_row, colRange=colRange, format=self.bottom_border_format
        # )
        # worksheet = add_vertical_border(
        #     worksheet, rowRange=rowRange, col=start_col, format=self.left_border_format
        # )
        # worksheet = add_vertical_border(
        #     worksheet, rowRange=rowRange, col=end_col, format=self.right_border_format
        # )
        # worksheet = cell_format(
        #     worksheet, refCell=top_left_corner, format=self.left_top_corner_format
        # )
        # worksheet = cell_format(
        #     worksheet, refCell=bottom_left_corner, format=self.left_bottom_corner_format
        # )
        # worksheet = cell_format(
        #     worksheet, refCell=top_right_corner, format=self.right_top_corner_format
        # )
        # worksheet = cell_format(
        #     worksheet,
        #     refCell=bottom_right_corner,
        #     format=self.right_bottom_corner_format,
        # )
        return worksheet

    @log_execution_time
    def create_ws_accueil(self):
        # worksheet.protect()
        worksheet = self.workbook.add_worksheet("ACCUEIL")
        worksheet = apply_worksheet_with_basic_format(
            worksheet, format=self.background_format
        )

        worksheet.set_column("J:J", 6, self.background_format)

        worksheet = self.draw_rectangle(
            worksheet, cellRef="C3:Q26", border_color=None, bg_color=None
        )

        self.set_title_format(fg_color=None, font_size=None, bold=None)
        worksheet = add_title(
            worksheet,
            range="F4:N4",
            text="Outil d'Analyse de Marché et de Simulation",
            format=self.title_format,
        )

        self.set_title_format(fg_color=self.bg_color, font_size=10, bold=0)
        worksheet = add_title(
            worksheet, range="F5:N5", text="offert par", format=self.title_format
        )

        self.set_title_format(fg_color=self.bg_color, font_size=12, bold=0)
        worksheet = add_title(
            worksheet, range="F6:N6", text="...USER...", format=self.title_format
        )

        worksheet = add_title(
            worksheet, range="F15:N15", text="...CONTACT...", format=self.title_format
        )

        worksheet = add_creteria(
            worksheet,
            self.criteria,
            row=19,
            title_col="I",
            value_col="K",
            format=self.info_fmt_bis,
        )

        # worksheet = add_horizontal_border(
        #     worksheet, row=18, colRange="f:n", format=self.top_border_format
        # )
        # worksheet = add_horizontal_border(
        #     worksheet, row=21, colRange="f:n", format=self.bottom_border_format
        # )

        worksheet = write_text(
            worksheet,
            text=self.disclaimer,
            ref_cell="J23",
            format=self.format_diclaimer,
        )

        # worksheet.set_column(0, 0, 25)
        worksheet.set_column("A:A", 25, self.background_format)
        # worksheet.set_column(15, 15, 25)
        worksheet.set_column("S:S", 25, self.background_format)
        worksheet.freeze_panes(30, 21)

    @log_execution_time
    def create_ws_liens(self, sheet_name):

        worksheet = self.workbook.add_worksheet(sheet_name)
        worksheet = apply_worksheet_with_basic_format(
            worksheet, format=self.background_format
        )
        worksheet = self.draw_rectangle(
            worksheet, cellRef="B2:M29", border_color=None, bg_color="white"
        )

        worksheet = self.draw_rectangle(worksheet, cellRef="C8:F10")
        worksheet = self.draw_rectangle(worksheet, cellRef="I8:L10")

        # worksheet = self.draw_rectangle(
        #     worksheet, cellRef="C5:L7", border_color="white", bg_color="white"
        # )
        # worksheet = self.draw_rectangle(
        #     worksheet, cellRef="C11:L13", border_color="white", bg_color="white"
        # )

        # worksheet = self.draw_rectangle(
        #     worksheet, cellRef="C5:L7", border_color="white", bg_color="white"
        # )

        worksheet = self.draw_rectangle(worksheet, cellRef="C17:F19")
        worksheet = self.draw_rectangle(worksheet, cellRef="I17:L19")

        worksheet = self.draw_rectangle(worksheet, cellRef="C21:F23")
        worksheet = self.draw_rectangle(worksheet, cellRef="I21:L23")

        worksheet = self.draw_rectangle(worksheet, cellRef="C25:F27")
        worksheet = self.draw_rectangle(worksheet, cellRef="I25:L27")

        self.set_title_format(fg_color=None, font_size=16, bold=None)
        worksheet = add_title(
            worksheet,
            range="C4:L4",
            text="EXPLORER LES AVIS SUR LA VILLE",
            format=self.title_format,
        )
        worksheet = add_title(
            worksheet,
            range="C14:L14",
            text="EXPLORER LES PRIX RECENTS",
            format=self.title_format,
        )

        for logo, url in zip(self.logos, self.url_logos):
            # Determine the cell position based on the URL
            if "ideal" in url:
                worksheet.write_url(
                    "D9", url, string="ville-ideale.fr", cell_format=self.link_format
                )
            elif "bien" in url:
                worksheet.write_url(
                    "J9",
                    url,
                    string="bien-dans-ma-ville.fr",
                    cell_format=self.link_format,
                )

            elif "city" in url:
                worksheet.write_url(
                    "D18", url, string="efficity.com", cell_format=self.link_format
                )
            elif "immo.notaire" in url:
                worksheet.write_url(
                    "J18",
                    url,
                    string="leprixdelimmo.notaires.fr",
                    cell_format=self.link_format,
                )
            elif "agent" in url:
                worksheet.write_url(
                    "D22",
                    url,
                    string="meilleursagents.com",
                    cell_format=self.link_format,
                )
            elif "immobilier.notaires" in url:
                worksheet.write_url(
                    "J22",
                    url,
                    string="immobilier.notaires.fr",
                    cell_format=self.link_format,
                )
            elif "loger" in url:
                worksheet.write_url(
                    "D26", url, string="seloger.com", cell_format=self.link_format
                )
            elif "figa" in url:
                worksheet.write_url(
                    "J26", url, string="lefigaro.fr", cell_format=self.link_format
                )
            else:
                pass

        worksheet.set_column("A:A", 40, self.background_format)
        # worksheet.set_column(15, 15, 25)
        worksheet.set_column("N:N", 40, self.background_format)
        worksheet.set_row(0, 25)
        worksheet.set_row(4, 9)  # Set height for row 6
        worksheet.set_row(5, 9)  # Set height for row 7
        worksheet.set_row(6, 9)  # Set height for row 8
        worksheet.set_row(10, 9)  # Set height for row 6
        worksheet.set_row(11, 9)  # Set height for row 7
        worksheet.set_row(12, 9)  # Set height for row 8

    @log_execution_time
    def create_ws_simulateur(self):

        self.set_percent_format(
            fg_color=self.bg_color, font_size=11, font_color="white", bold=1
        )
        self.set_money_format(
            fg_color=self.bg_color,
            font_size=11,
            font_color="white",
            bold=1,
            locked=True,
        )

        worksheet = self.workbook.add_worksheet("SIMULATEUR")
        worksheet = apply_worksheet_with_basic_format(
            worksheet, format=self.background_format
        )

        worksheet.set_column("F:F", 25, self.background_format)
        worksheet.set_column("G:G", 25, self.background_format)
        worksheet.set_column("H:H", 25, self.background_format)

        worksheet = self.draw_rectangle(
            worksheet, cellRef="E6:I27", border_color=None, bg_color="white"
        )

        self.set_title_format(fg_color=None, font_size=16, bold=None)
        worksheet = add_title(
            worksheet,
            range="F8:H8",
            text="RAPPEL DES CRITERES",
            format=self.title_format,
        )

        self.set_title_format(fg_color=None, font_size=16, bold=None)
        worksheet = add_title(
            worksheet,
            range="F20:H20",
            text="RESULTATS DE LA SIMULATION",
            format=self.title_format,
        )

        # row = 8
        # col = 6
        # row -= 1
        # col -= 1

        # worksheet.merge_range(
        #     "F8:H8", "RENSEIGNER POUR EFFECTUER UNE SIMULATION", self.merge_format
        # )

        # ############ Type d'utilisateur
        worksheet.write("F9", "Type d'utilisateur", self.gray_basic_format)
        self.workbook.define_name("utilisateur_s2", "=SIMULATEUR!$H$9")
        # worksheet.data_validation(
        #     "H9", {"validate": "list", "source": ["Particulier", "Professionnel"]}
        # )
        worksheet.write_formula("H9", "=utilisateur", self.money_fmt)
        # worksheet.write(
        #     "J9", "    <-- Sélectionner le type d'utilisateur.", self.info_fmt_bis
        # )

        # ############ Prix de revente
        worksheet.write("F10", "Prix de revente (prix de marché)", self.basic_format)
        self.workbook.define_name("prix_revente_s2", "=SIMULATEUR!$H$10")
        worksheet.write_formula("H10", "=prix_marche", self.money_fmt)
        # worksheet.write(
        #     "J10",
        #     "    <-- Renseigner votre prix de revente suite à l'analyse du marché.",
        #     self.info_fmt_bis,
        # )

        # ############ Prix limite
        worksheet.write("F11", "Prix limite", self.basic_format)
        self.workbook.define_name("prix_limite_s2", "=SIMULATEUR!$H$11")
        worksheet.write_formula("H11", "=prix_limite", self.money_fmt)
        # worksheet.write(
        #     "J11", "    <-- Renseigner votre prix limite.", self.info_fmt_bis
        # )

        # ############ Montant des travaux
        worksheet.write("F12", "Montant des travaux", self.basic_format)
        self.workbook.define_name("montant_travaux_s2", "=SIMULATEUR!$H$12")
        worksheet.write_formula(
            "H12",
            "=travaux",
            self.money_fmt,
        )
        # worksheet.write(
        #     "J12", "    <-- Renseigner le montant des travaux.", self.info_fmt_bis
        # )

        # ############ SIMULATION DES FRAIS
        self.set_title_format(fg_color=None, font_size=10, bold=None)
        worksheet = add_title(
            worksheet,
            range="F14:H14",
            text="FRAIS",
            format=self.title_format,
        )
        # worksheet.merge_range("F14:H14", "ELEMENTS DE FRAIS", self.merge_format)
        # ----------- Frais de représentation
        worksheet.write("F15", "Frais de représentation", self.basic_format)
        self.workbook.define_name("frais_pres_s2", "=SIMULATEUR!$H$15")
        worksheet.write_formula(
            "H15",
            "=frais_pres",
            self.money_fmt,
        )
        # worksheet.write(
        #     "J15",
        #     "    <-- Renseigner les frais de représentation de l'avocat",
        #     self.info_fmt_bis,
        # )
        # ----------- Frais préalables
        worksheet.write("F16", "Frais préalables de saisie", self.basic_format)
        self.workbook.define_name("frais_prea_saisi_s2", "=SIMULATEUR!$H$16")
        worksheet.write_formula(
            "H16",
            "=frais_prea_saisi",
            self.money_fmt,
        )
        # worksheet.write(
        #     "J16",
        #     "    <-- Renseigner les frais préalables de saisie",
        #     self.info_fmt_bis,
        # )
        # ----------- Frais préalables
        worksheet.write("F17", "Autres frais", self.basic_format)
        self.workbook.define_name("autres_frais_s2", "=SIMULATEUR!$H$17")
        worksheet.write_formula(
            "H17",
            "=autres_frais",
            self.money_fmt,
        )
        # worksheet.write(
        #     "J17", "    <-- Renseigner les autres frais potentiels", self.info_fmt_bis
        # )

        # ----------- Total Frais
        worksheet.write("F18", "Montant estimé des Frais", self.basic_format)
        self.workbook.define_name("frais_estimes_s2", "=SIMULATEUR!$H$18")
        worksheet.write_formula(
            "H18",
            # """=frais_pres_s2
            #                                         +1.2*IF(prix_limite_s2 < 6500,
            #                                             prix_limite_s2 * 0.07397,
            #                                             IF(prix_limite_s2 <= 17000,
            #                                                 ((prix_limite_s2 - 6500) * 0.03051) + 481,
            #                                                 IF(prix_limite_s2 <= 60000,
            #                                                     ((prix_limite_s2 - 17000) * 0.02034) + 800,
            #                                                     ((prix_limite_s2 - 60000) * 0.01526) + 1675
            #                                                 )
            #                                             )
            #                                         )
            #                                         +frais_prea_saisi_s2
            #                                         +autres_frais_s2
            #                                         +IF(utilisateur_s2 = "particulier",
            #                                             prix_limite_s2 * 0.045 + prix_limite_s2 * 0.012 + (prix_limite_s2 * 0.045 * 0.0237),
            #                                             prix_limite_s2 * 0.00715 + prix_limite_s2 * 0.0237
            #                                         )
            #                                         +MAX(prix_limite_s2 * 0.001, 15) + 12 + 46
            #                                         +prix_limite_s2 * 0.001""",
            """=frais_pres_s2
                                                    +1.2*IF(prix_limite_s2 < 6500,
                                                        prix_limite_s2 * 0.07256,
                                                        IF(prix_limite_s2 <= 17000,
                                                            ((prix_limite_s2 - 6500) * 0.02993) + 472,
                                                            IF(prix_limite_s2 <= 60000,
                                                                ((prix_limite_s2 - 17000) * 0.01995) + 786,
                                                                ((prix_limite_s2 - 60000) * 0.01497) + 1644
                                                            )
                                                        )
                                                    )
                                                    +frais_prea_saisi_s2
                                                    +autres_frais_s2
                                                    +IF(utilisateur_s2 = "particulier",
                                                        prix_limite_s2 * 0.045 + prix_limite_s2 * 0.012 + (prix_limite_s2 * 0.045 * 0.0237),
                                                        prix_limite_s2 * 0.00715 + prix_limite_s2 * 0.0237
                                                    )
                                                    +MAX(prix_limite_s2 * 0.001, 15) + 12 + 46
                                                    +prix_limite_s2 * 0.001""",
            self.money_fmt,
        )

        # ----------- Cout total de l'opération
        worksheet.write(
            "F22", "Cout total de l'opération (montant à financer)", self.basic_format
        )
        self.workbook.define_name("cout_total_s2", "=SIMULATEUR!$H$22")
        worksheet.write_formula(
            "H22",
            "prix_limite_s2 + montant_travaux_s2 + frais_estimes_s2",
            self.money_fmt,
        )
        # worksheet.write('J22', "    <-- Coût total de l'opération / montant à financer", self.info_fmt_bis)

        # worksheet.write('F25', "Plus Value potentielle à la revente")
        # self.workbook.define_name('plus_value', f'=SIMULATEUR!$H$25')

        # ----------- Plus Value
        worksheet.write("F23", "Plus Value potentielle à la revente", self.basic_format)
        self.workbook.define_name("plus_value_s2", "=SIMULATEUR!$H$23")
        worksheet.write_formula(
            "H23", "prix_revente_s2 - cout_total_s2", self.money_fmt
        )

        # worksheet.write('F26', "Rentabilité potentielle à la revente")
        # self.workbook.define_name('rentabilite', f'=SIMULATEUR!$H$26')
        # ----------- Rentabilité
        worksheet.write(
            "F24", "Rentabilité potentielle à la revente", self.basic_format
        )
        self.workbook.define_name("renta_s2", "=SIMULATEUR!$H$24")
        worksheet.write_formula(
            "H24",
            "plus_value_s2\
                                /cout_total_s2",
            self.percent_fmt,
        )

        # ----------- Probabilité
        worksheet.write(
            "F25", "Probabilité d'obtention de la décote", self.basic_format
        )
        self.workbook.define_name("proba_s2", "=SIMULATEUR!$H$25")
        worksheet.write_formula(
            "H25",
            '=IF(SUM(decotes)=0,"indisponible",COUNTIF(decotes,">="&(1-prix_limite_s2/prix_revente_s2)*100)/COUNT(decotes))',
            self.percent_fmt,
        )

        # worksheet.write("F25", "Probabilité d'obtention de l'enchère")
        # worksheet.write_formula(
        #     "H24",
        #     '=IF(SUM(decotes)=0,"indisponible",COUNTIF(decotes,">="&(1-prix_limite_s2/prix_revente_s2)*100)/COUNT(decotes))',
        #     self.percent_fmt,
        # )
        # self.money_fmt_unlocked = self.workbook.add_format(
        #     {
        #         "num_format": "# ##0 €",
        #         "align": "right",
        #         "valign": "vcenter",
        #         "locked": False,
        #     }
        # )

        # Widen the first column to make the text clearer.
        # worksheet.set_column("A:A", 20)
        # row += 1
        # worksheet.merge_range(f'{xl_rowcol_to_cell(row+7, col)}:{xl_rowcol_to_cell(row+7, col+2)}', 'RESULTAT DE LA SIMULATION', self.merge_format)
        # worksheet.merge_range("F20:H20", "RESULTAT DE LA SIMULATION", self.merge_format)

        # Remove gridlines
        # worksheet.hide_gridlines(2)

        # worksheet.set_column(col, col + 2, 20)
        worksheet.set_column("A:A", 20, self.background_format)

        # worksheet.set_column(col + 11, col + 11, 20)
        worksheet.set_column("L:L", 20, self.background_format)
        worksheet.set_column("F:F", 34, self.background_format)
        worksheet.freeze_panes(32 + 24, 18)
        # worksheet.freeze_panes(32, 24)
        # worksheet.set_row(row+23, row+23, 10)
        # worksheet.set_row(row + 23, 20)

        # Define the format for the right border
        # right_border_format = self.workbook.add_format(
        #     {"right": 5, "right_color": self.bbg_color}
        # )

        # # Define the format for the right border
        # left_border_format = self.workbook.add_format(
        #     {"left": 5, "left_color": self.bbg_color}
        # )

        # Apply right border to the range E2:E9
        # for row in range(5, 28):  # E2:E9 corresponds to row indices 2 to 9
        #     worksheet.write(row, 3, "", self.right_border_format)
        #     worksheet.write(row, 8, "", self.right_border_format)

        # # Define the format for the top blue border
        # top_blue_border = self.workbook.add_format(
        #     {"top": 5, "top_color": self.bbg_color}
        # )

        # # Apply top blue border to C2:D2
        # worksheet.write("E6", "", top_blue_border)
        # worksheet.write("F6", "", top_blue_border)
        # worksheet.write("G6", "", top_blue_border)
        # worksheet.write("H6", "", top_blue_border)
        # worksheet.write("I6", "", top_blue_border)

        # # Apply top blue border to C10:D10
        # worksheet.write("E28", "", top_blue_border)
        # worksheet.write("F28", "", top_blue_border)
        # worksheet.write("G28", "", top_blue_border)
        # worksheet.write("H28", "", top_blue_border)
        # worksheet.write("I28", "", top_blue_border)

        # # Define the format for the right border
        # angle_border_format = self.workbook.add_format(
        #     {
        #         "right": 5,
        #         "right_color": self.bbg_color,
        #         "top": 5,
        #         "top_color": self.bbg_color,
        #     }
        # )
        # worksheet.write("I6", "", angle_border_format)

        # worksheet.protect()

        # self.money_fmt_unlocked = self.workbook.add_format(
        #     {
        #         "num_format": "# ##0 €",
        #         "align": "center",
        #         "valign": "vcenter",
        #         "locked": False,
        #     }
        # )
        # percent_fmt_unlocked = self.workbook.add_format(
        #     {
        #         "num_format": "0%",
        #         "align": "center",
        #         "valign": "vcenter",
        #         "locked": False,
        #     }
        # )

    @log_execution_time
    def create_ws_simulateur_NEW(self):

        self.money_fmt_unlocked = self.workbook.add_format(
            {
                "num_format": "# ##0 €",
                "align": "right",
                "valign": "vcenter",
                "locked": False,
            }
        )

        # percent_fmt_unlocked = self.workbook.add_format(
        #     {"num_format": "0%", "align": "right", "valign": "vcenter", "locked": False}
        # )

        # Create worksheet
        worksheet = self.workbook.add_worksheet("SIMULATEUR")
        worksheet.set_column("A:A", 20)

        row, col = 7, 5

        # Set values and create named ranges
        worksheet.write(
            row + 2,
            col + 2,
            self.prix_marche * self.cible_decote,
            self.money_fmt_unlocked,
        )
        worksheet.write(row + 3, col + 2, self.prix_marche, self.money_fmt)
        worksheet.write(
            row + 4,
            col + 2,
            self.taux_travaux * self.prix_marche * self.cible_decote,
            self.money_fmt_unlocked,
        )
        worksheet.write(row + 5, col + 2, self.taux_frais, self.percent_fmt_unlocked)

        self.workbook.define_name(
            "prix_limite", f"SIMULATEUR!{xl_rowcol_to_cell(row+2, col+2)}"
        )
        self.workbook.define_name(
            "prix_revente", f"SIMULATEUR!{xl_rowcol_to_cell(row+3, col+2)}"
        )
        self.workbook.define_name(
            "montant_travaux", f"SIMULATEUR!{xl_rowcol_to_cell(row+4, col+2)}"
        )
        self.workbook.define_name(
            "taux_frais", f"SIMULATEUR!{xl_rowcol_to_cell(row+5, col+2)}"
        )

        # Add Montant frais (si connu) in F14
        worksheet.write(row + 7, col, "Montant frais (si connu)")
        worksheet.write_formula(
            row + 7, col + 2, "taux_frais * prix_limite", self.money_fmt
        )
        self.workbook.define_name(
            "frais_estimes", f"SIMULATEUR!{xl_rowcol_to_cell(row+7, col+2)}"
        )
        worksheet.write(
            row + 7, col + 4, "    <-- Estimation des frais.", self.info_fmt
        )

        # Headers
        worksheet.merge_range(
            f"{xl_rowcol_to_cell(row, col)}:{xl_rowcol_to_cell(row, col+2)}",
            "RENSEIGNER POUR EFFECTUER UNE SIMULATION",
            self.merge_format,
        )

        # Simulation Result Section
        worksheet.merge_range(
            f"{xl_rowcol_to_cell(row+8, col)}:{xl_rowcol_to_cell(row+8, col+2)}",
            "RESULTAT DE LA SIMULATION",
            self.merge_format,
        )

        worksheet.write(row + 10, col, "Montant des travaux")
        worksheet.write_formula(row + 10, col + 2, "montant_travaux", self.money_fmt)
        worksheet.write(
            row + 10,
            col + 4,
            "    <-- Montant des travaux renseigné plus haut.",
            self.info_fmt,
        )

        worksheet.write(row + 11, col, "Montant des frais")
        worksheet.write_formula(
            row + 11, col + 2, "prix_limite * taux_frais", self.money_fmt
        )
        worksheet.write(
            row + 11,
            col + 4,
            "    <--  Montant des frais si leur montant a été évalué.",
            self.info_fmt,
        )

        worksheet.write(row + 12, col, "Total à payer")
        worksheet.write_formula(
            row + 12,
            col + 2,
            "prix_limite + montant_travaux + frais_estimes",
            self.money_fmt,
        )
        worksheet.write(
            row + 12,
            col + 4,
            "    <-- Coût total de l'opération / montant à financer",
            self.info_fmt,
        )

        worksheet.write(row + 13, col, "Plus Value potentiel à la revente")
        worksheet.write_formula(
            row + 13,
            col + 2,
            "prix_revente - (prix_limite + montant_travaux + frais_estimes)",
            self.money_fmt,
        )

        worksheet.write(row + 14, col, "Rentabilité potentielle à la revente")
        worksheet.write_formula(
            row + 14,
            col + 2,
            "(prix_revente / (prix_limite + montant_travaux + frais_estimes)) - 1",
            self.percent_fmt,
        )

        worksheet.write(row + 15, col, "Probabilité d'obtention de l'enchère")
        worksheet.write_formula(
            row + 15,
            col + 2,
            'IF(SUM(decotes)=0, "indisponible", COUNTIF(decotes,">="&(1-H11/H12)*100)/COUNT(decotes))',
            self.percent_fmt,
        )

        # Formatting
        worksheet.hide_gridlines(2)
        worksheet.set_column(col, col + 2, 20)
        worksheet.freeze_panes(row + 25, col + 12)
        worksheet.set_column(col + 11, col + 11, 20)
        worksheet.set_row(row + 24, 20)

        # Borders
        # right_border_format = self.workbook.add_format(
        #     {"right": 5, "right_color": self.bbg_color}
        # )
        # left_border_format = self.workbook.add_format(
        #     {"left": 5, "left_color": self.bbg_color}
        # )
        top_blue_border = self.workbook.add_format(
            {"top": 5, "top_color": self.bbg_color}
        )
        angle_border_format = self.workbook.add_format(
            {
                "right": 5,
                "top": 5,
                "right_color": self.bbg_color,
                "top_color": self.bbg_color,
            }
        )

        for i in range(5, 24):
            worksheet.write(i, 3, "", self.right_border_format)
            worksheet.write(i, 8, "", self.right_border_format)

        worksheet.write("I6", "", angle_border_format)
        worksheet.write("E6:I6", "", top_blue_border)
        worksheet.write("E25:I25", "", top_blue_border)

        self.money_fmt_unlocked = self.workbook.add_format(
            {
                "num_format": "# ##0 €",
                "align": "right",
                "valign": "vcenter",
                "locked": False,
            }
        )

        # percent_fmt_unlocked = self.workbook.add_format(
        #     {"num_format": "0%", "align": "right", "valign": "vcenter", "locked": False}
        # )

        # Create worksheet
        # worksheet = self.workbook.add_worksheet('SIMULATEUR')
        # worksheet.set_column('A:A', 20)

        row, col = 7, 5

        # Define named cells
        worksheet.write(
            row + 2,
            col + 2,
            self.prix_marche * self.cible_decote,
            self.money_fmt,
        )
        worksheet.write(row + 3, col + 2, self.prix_marche, self.money_fmt)
        worksheet.write(
            row + 4,
            col + 2,
            self.taux_travaux * self.prix_marche * self.cible_decote,
            self.money_fmt,
        )
        worksheet.write(row + 5, col + 2, self.taux_frais, self.percent_fmt_unlocked)

        worksheet.write(row + 2, col, "Prix limite")
        worksheet.write(row + 3, col, "Prix de revente (prix de marché)")
        worksheet.write(row + 4, col, "Montant des travaux")
        worksheet.write(row + 5, col, "% frais")

        worksheet.write(
            row + 2, col + 4, "    <-- Renseigner votre prix limite.", self.info_fmt
        )
        worksheet.write(
            row + 3,
            col + 4,
            "    <-- Renseigner votre prix de revente suite à l'analyse du marché.",
            self.info_fmt,
        )
        worksheet.write(
            row + 4, col + 4, "    <-- Ajuster le montant des travaux.", self.info_fmt
        )
        worksheet.write(
            row + 5,
            col + 4,
            "    <-- Ajuster le montant des frais (% du prix limite).",
            self.info_fmt,
        )

        self.workbook.define_name("prix_limite", xl_rowcol_to_cell(row + 2, col + 2))
        self.workbook.define_name("prix_revente", xl_rowcol_to_cell(row + 3, col + 2))
        self.workbook.define_name(
            "montant_travaux", xl_rowcol_to_cell(row + 4, col + 2)
        )
        self.workbook.define_name("taux_frais", xl_rowcol_to_cell(row + 5, col + 2))

        # Add Montant frais (si connu) in F14
        worksheet.write(row + 7, col, "Montant frais (si connu)")
        worksheet.write_formula(
            xl_rowcol_to_cell(row + 7, col + 2),
            "taux_frais * prix_limite",
            self.money_fmt,
        )
        self.workbook.define_name("frais_estimes", xl_rowcol_to_cell(row + 7, col + 2))
        worksheet.write(
            xl_rowcol_to_cell(row + 7, col + 4),
            "    <-- Estimation des frais.",
            self.info_fmt,
        )

        # Headers
        worksheet.merge_range(
            f"{xl_rowcol_to_cell(row, col)}:{xl_rowcol_to_cell(row, col+2)}",
            "RENSEIGNER POUR EFFECTUER UNE SIMULATION",
            self.merge_format,
        )

        # Simulation Result Section
        worksheet.merge_range(
            f"{xl_rowcol_to_cell(row+8, col)}:{xl_rowcol_to_cell(row+8, col+2)}",
            "RESULTAT DE LA SIMULATION",
            self.merge_format,
        )

        worksheet.write(xl_rowcol_to_cell(row + 10, col), "Montant des travaux")
        worksheet.write_formula(
            xl_rowcol_to_cell(row + 10, col + 2),
            "montant_travaux",
            self.money_fmt,
        )
        worksheet.write(
            xl_rowcol_to_cell(row + 10, col + 4),
            "    <-- Montant des travaux renseigné plus haut.",
            self.info_fmt,
        )

        worksheet.write(xl_rowcol_to_cell(row + 11, col), "Montant des frais")
        worksheet.write_formula(
            xl_rowcol_to_cell(row + 11, col + 2),
            "prix_limite * taux_frais",
            self.money_fmt,
        )
        worksheet.write(
            xl_rowcol_to_cell(row + 11, col + 4),
            "    <--  Montant des frais si leur montant a été évalué.",
            self.info_fmt,
        )

        worksheet.write(xl_rowcol_to_cell(row + 12, col), "Total à payer")
        worksheet.write_formula(
            xl_rowcol_to_cell(row + 12, col + 2),
            "prix_limite + montant_travaux + frais_estimes",
            self.money_fmt,
        )
        worksheet.write(
            xl_rowcol_to_cell(row + 12, col + 4),
            "    <-- Coût total de l'opération / montant à financer",
            self.info_fmt,
        )

        worksheet.write(
            xl_rowcol_to_cell(row + 13, col), "Plus Value potentiel à la revente"
        )
        worksheet.write_formula(
            xl_rowcol_to_cell(row + 13, col + 2),
            "prix_revente - (prix_limite + montant_travaux + frais_estimes)",
            self.money_fmt,
        )

        worksheet.write(
            xl_rowcol_to_cell(row + 14, col), "Rentabilité potentielle à la revente"
        )
        worksheet.write_formula(
            xl_rowcol_to_cell(row + 14, col + 2),
            "(prix_revente / (prix_limite + montant_travaux + frais_estimes)) - 1",
            self.percent_fmt,
        )

        worksheet.write(
            xl_rowcol_to_cell(row + 15, col), "Probabilité d'obtention de l'enchère"
        )
        worksheet.write_formula(
            xl_rowcol_to_cell(row + 15, col + 2),
            'IF(SUM(decotes)=0, "indisponible", COUNTIF(decotes,">="&(1-H11/H12)*100)/COUNT(decotes))',
            self.percent_fmt,
        )

        # Formatting
        worksheet.hide_gridlines(2)
        worksheet.set_column(col, col + 2, 20)
        worksheet.freeze_panes(row + 25, col + 12)
        worksheet.set_column(col + 11, col + 11, 20)
        worksheet.set_row(row + 24, 20)

        # Borders
        # right_border_format = self.workbook.add_format(
        #     {"right": 5, "right_color": self.bbg_color}
        # )
        # left_border_format = self.workbook.add_format(
        #     {"left": 5, "left_color": self.bbg_color}
        # )
        top_blue_border = self.workbook.add_format(
            {"top": 5, "top_color": self.bbg_color}
        )
        angle_border_format = self.workbook.add_format(
            {
                "right": 5,
                "top": 5,
                "right_color": self.bbg_color,
                "top_color": self.bbg_color,
            }
        )

        for i in range(5, 24):
            worksheet.write(i, 3, "", self.right_border_format)
            worksheet.write(i, 8, "", self.right_border_format)

        worksheet.write("I6", "", angle_border_format)
        worksheet.write("E6:I6", "", top_blue_border)
        worksheet.write("E25:I25", "", top_blue_border)

    @log_execution_time
    def create_ws_simulateur_2(self):

        self.set_money_format(
            fg_color="white", font_size=11, font_color=None, bold=None, locked=False
        )
        self.set_percent_format(fg_color="white", font_size=11, font_color=None, bold=1)
        # Create a self.workbook and add a worksheet
        worksheet = self.workbook.add_worksheet("SIMULATEUR_2")
        worksheet = apply_worksheet_with_basic_format(
            worksheet, format=self.background_format
        )

        worksheet.set_column("A:A", 2, self.background_format)
        worksheet.set_column("B:B", 15, self.background_format)
        worksheet.set_column("C:C", 24, self.background_format)
        worksheet.set_column("D:D", 20, self.background_format)
        worksheet.set_column("E:E", 60, self.background_format)
        worksheet.set_column("F:F", 28, self.background_format)
        worksheet.set_column("G:H", 25, self.background_format)
        worksheet.set_column("I:I", 2, self.background_format)
        # worksheet.set_column("G:G", 25, self.background_format)
        # worksheet.set_column("H:H", 25, self.background_format)

        worksheet = self.draw_rectangle(
            worksheet, cellRef="B2:H10", border_color=None, bg_color="white"
        )

        # Write the static values to the cells
        values = zip(
            [
                "Mise à prix",
                "Prix de marché",
                "Prix limite",
                "Décote",
                "Probabilité d'obtention",
                "Travaux",
                "Montant surenchère",
            ],
            [
                "<-- Renseigner le montant de la mise à prix.",
                "<-- Renseigner votre prix de revente suite à l'analyse du marché.",
                "<-- Renseigner votre prix limite.",
                "<-- Décote relative au prix de revente.",
                "<-- Probabilité d'obtenir votre prix limite.",
                "<-- Renseigner le montant des travaux.",
                "<-- Renseigner votre montant de surenchère.",
            ],
        )
        for row, value in enumerate(values, start=2):
            worksheet.write(row, 2, value[0], self.info_fmt)
            worksheet.write(row, 4, value[1], self.basic_format)

        worksheet.write("B12", "Prix adjugée", self.info_fmt)
        worksheet.write("C12", "Montant des travaux", self.info_fmt)
        worksheet.write("D12", "Montant des frais", self.info_fmt)  # 15%
        worksheet.write("E12", "Total à payer", self.info_fmt)  # 15%
        worksheet.write("F12", "Plus Value potentielle", self.info_fmt)
        worksheet.write("G12", "Rentabilité potentielle", self.info_fmt)
        worksheet.write("H12", "Probabilité d'obtention", self.info_fmt)

        self.workbook.define_name("mise_a_prix", "SIMULATEUR_2!$D$3")
        self.workbook.define_name("prix_marche", "SIMULATEUR_2!$D$4")
        self.workbook.define_name("prix_limite", "SIMULATEUR_2!$D$5")
        self.workbook.define_name("decote", "SIMULATEUR_2!$D$6")
        self.workbook.define_name("travaux", "SIMULATEUR_2!$D$8")
        self.workbook.define_name("surenchere", "SIMULATEUR_2!$D$9")

        self.set_money_format(
            fg_color="#f2f2f2", font_size=11, font_color=None, bold=1, locked=False
        )
        self.set_percent_format(fg_color="white", font_size=11, font_color=None, bold=1)

        worksheet.write("D3", self.mise_a_prix, self.money_fmt)
        worksheet.write("D4", self.prix_marche, self.money_fmt)
        worksheet.write("D5", self.prix_marche * self.cible_decote, self.money_fmt)
        worksheet.write_formula(
            # "D6", "1-prix_limite/prix_marche", self.percent_fmt_centered_locked
            "D6",
            "1-prix_limite/prix_marche",
            self.percent_fmt,
        )
        # worksheet.write_formula('C7', f'IF(SUM(decotes)=0, "indisponible", COUNTIF(decotes,">="&(1-D5/D4)*100)/COUNT(decotes))', self.percent_fmt_locked)
        worksheet.write_formula(
            "D7",
            'IF(SUM(decotes)=0, "indisponible", COUNTIF(decotes,">="&decote*100)/COUNT(decotes))',
            self.percent_fmt,
        )
        # worksheet.write_formula(i + 9, 1, f'mise_a_prix + A{i+10}*surenchere', self.money_fmt)
        montant_travaux = int(self.taux_travaux * self.prix_marche * self.cible_decote)
        worksheet.write("D8", montant_travaux, self.money_fmt)
        montant_enchere = int((self.prix_marche - self.mise_a_prix) / 20)
        worksheet.write("D9", montant_enchere, self.money_fmt)

        self.set_title_format(fg_color=None, font_size=10, bold=None)
        worksheet = add_title(
            worksheet, range="F3:G3", text="ELEMENTS DE FRAIS", format=self.title_format
        )

        worksheet.write("F4", "Type d'utilisateur", self.basic_format)
        worksheet.write("F5", "Frais de représentation avocat", self.basic_format)
        worksheet.write("F6", "Frais préalables de saisie", self.basic_format)
        worksheet.write("F7", "Autres frais de procédure", self.basic_format)

        self.workbook.define_name("utilisateur", "SIMULATEUR_2!$G$4")
        self.workbook.define_name("frais_pres", "SIMULATEUR_2!$G$5")
        self.workbook.define_name("frais_prea_saisi", "SIMULATEUR_2!$G$6")
        self.workbook.define_name("autres_frais", "SIMULATEUR_2!$G$7")

        worksheet.data_validation(
            "G4", {"validate": "list", "source": ["Particulier", "Professionnel"]}
        )
        worksheet.write("G4", "Particulier", self.money_fmt)

        worksheet.write("G5", 0, self.money_fmt)
        worksheet.write("G6", 0, self.money_fmt)
        worksheet.write("G7", 0, self.money_fmt)

        # Fill range A10:A1010 with values from 1 to 1000
        offset = 3
        nb_simulations = 100

        worksheet = self.draw_rectangle(
            worksheet,
            cellRef=f"B13:H{nb_simulations+13}",
            border_color=None,
            bg_color="white",
        )

        # Fill range B10:B1010 with the formula (value column A) * mise_a_prix * surenchere

        self.set_money_format(
            fg_color="white", font_size=11, font_color=None, bold=None, locked=True
        )
        self.set_percent_format(fg_color="white", font_size=11, font_color=None, bold=1)

        for i in range(nb_simulations):
            i += offset
            worksheet.write_formula(
                i + 9, 1, f"mise_a_prix + A{i+10}*surenchere", self.money_fmt
            )

        # Fill range C10:C1010 with the value from travaux cell
        for i in range(nb_simulations):
            i += offset
            worksheet.write_formula(i + 9, 2, "travaux", self.money_fmt)

        # Fill range D10:D1010 with the formula (value column B) * frais
        for i in range(nb_simulations):
            i += offset
            # worksheet.write_formula(i + 9, 3, f'B{i+10}*frais', self.money_fmt)
            worksheet.write_formula(
                i + 9,
                3,
                f"""=frais_pres
                                                    +1.2*IF(B{i+10} < 6500,
                                                        B{i+10} * 0.07397,
                                                        IF(B{i+10} <= 17000,
                                                            ((B{i+10} - 6500) * 0.03051) + 481,
                                                            IF(B{i+10} <= 60000,
                                                                ((B{i+10} - 17000) * 0.02034) + 800,
                                                                ((B{i+10} - 60000) * 0.01526) + 1675
                                                            )
                                                        )
                                                    )
                                                    +frais_prea_saisi
                                                    +autres_frais
                                                    +IF(utilisateur= "particulier",
                                                        B{i+10} * 0.045 + B{i+10} * 0.012 + (B{i+10} * 0.045 * 0.0237),
                                                        B{i+10} * 0.00715 + B{i+10} * 0.0237
                                                    )
                                                    +MAX(B{i+10} * 0.001, 15) + 12 + 46
                                                    +B{i+10} * 0.001""",
                self.money_fmt,
            )

        # Fill range E10:E1010 with the formula SUM(B, C, D)
        for i in range(nb_simulations):
            i += offset
            worksheet.write_formula(
                i + 9, 4, f"SUM(B{i+10},C{i+10},D{i+10})", self.money_fmt
            )

        # Fill range F10:F1010 with the formula prix_limite - E
        for i in range(nb_simulations):
            i += offset
            worksheet.write_formula(i + 9, 5, f"prix_marche-E{i+10}", self.money_fmt)

        # Fill range G10:G1010 with the formula F/E
        for i in range(nb_simulations):
            i += offset
            worksheet.write_formula(i + 9, 6, f"F{i+10}/E{i+10}", self.percent_fmt)

        for i in range(nb_simulations):
            i += offset
            worksheet.write_formula(
                i + 9,
                7,
                f'IF(SUM(decotes)=0, "indisponible", COUNTIF(decotes,">="&(1-B{i+10}/prix_marche)*100)/COUNT(decotes))',
                self.percent_fmt,
            )

        for i in range(nb_simulations):
            i += offset
            # worksheet.write_formula(
            #     i + 9, 8, f"G{i+10}-H{i+10}", self.background_format
            # )
            worksheet.write_formula(
                f"I{i+10}", f"G{i+10}-H{i+10}", self.background_format
            )

            worksheet.write_formula(
                f"J{i+10}",
                f'IF(AND(G{i+10}>0,I{i+10}>-0.1,I{i+10}<0.15),B{i+10},"")',
                self.background_format,
            )

            # worksheet.write_formula(
            #         f"I{i+10}", f"G{i+10}-H{i+10}", self.background_format
            #     )

            worksheet.write_formula(
                f"K{i+10}", f'IF(J{i+10}<>"",E{i+10},"")', self.background_format
            )  # Financement
            worksheet.write_formula(
                f"L{i+10}", f'IF(J{i+10}<>"",F{i+10},"")', self.background_format
            )  # PV
            worksheet.write_formula(
                f"M{i+10}", f'IF(J{i+10}<>"",G{i+10},"")', self.background_format
            )  # Renta
            worksheet.write_formula(
                f"N{i+10}", f'IF(J{i+10}<>"",H{i+10},"")', self.background_format
            )  # Proba
            worksheet.write_formula(
                f"O{i+10}",
                f'IF(J{i+10}<>"",1-B{i+10}/prix_marche,"")',
                self.background_format,
            )  # Decote

        self.workbook.define_name(
            "prix_adjudication",
            "=OFFSET(SIMULATEUR_2!$B$12,1,0,COUNT(SIMULATEUR_2!$A:$A),1)",
        )

        self.workbook.define_name(
            "courbe_renta",
            "=OFFSET(SIMULATEUR_2!$G$12,1,0,COUNT(SIMULATEUR_2!$A:$A),1)",
        )

        self.workbook.define_name(
            "courbe_proba",
            "=OFFSET(SIMULATEUR_2!$H$12,1,0,COUNT(SIMULATEUR_2!$A:$A),1)",
        )

        self.workbook.define_name(
            "min_adju",
            '=IF(SUM(decotes)<>0,MIN(SIMULATEUR_2!$J:$J),"indisponible")',
        )

        self.workbook.define_name(
            "max_adju",
            '=IF(SUM(decotes)<>0,MAX(SIMULATEUR_2!$J:$J),"indisponible")',
        )

        self.workbook.define_name(
            "min_cout",
            '=IF(SUM(decotes)<>0,MIN(SIMULATEUR_2!$K:$K),"indisponible")',
        )

        self.workbook.define_name(
            "max_cout",
            '=IF(SUM(decotes)<>0,MAX(SIMULATEUR_2!$K:$K),"indisponible")',
        )

        self.workbook.define_name(
            "min_pv",
            '=IF(SUM(decotes)<>0,MIN(SIMULATEUR_2!$L:$L),"indisponible")',
        )

        self.workbook.define_name(
            "max_pv",
            '=IF(SUM(decotes)<>0,MAX(SIMULATEUR_2!$L:$L),"indisponible")',
        )

        self.workbook.define_name(
            "min_proba",
            '=IF(SUM(decotes)<>0,MIN(SIMULATEUR_2!$N:$N),"indisponible")',
        )

        self.workbook.define_name(
            "max_proba",
            '=IF(SUM(decotes)<>0,MAX(SIMULATEUR_2!$N:$N),"indisponible")',
        )

        self.workbook.define_name(
            "min_renta",
            '=IF(SUM(decotes)<>0,MIN(SIMULATEUR_2!$M:$M),"indisponible")',
        )

        self.workbook.define_name(
            "max_renta",
            '=IF(SUM(decotes)<>0,MAX(SIMULATEUR_2!$M:$M),"indisponible")',
        )

        self.workbook.define_name(
            "min_decote",
            '=IF(SUM(decotes)<>0,MIN(SIMULATEUR_2!$O:$O),"indisponible")',
        )

        self.workbook.define_name(
            "max_decote",
            '=IF(SUM(decotes)<>0,MAX(SIMULATEUR_2!$O:$O),"indisponible")',
        )

        # Filter
        worksheet.autofilter("B12:H12")
        # Add borders to the range B12:G1010

        border_format = self.workbook.add_format({"border": 0})
        # nb_simulations
        worksheet.conditional_format(
            f"B{i+10}:H1012", {"type": "no_blanks", "format": border_format}
        )

        # Apply right border to the range E2:E9
        # for row in range(1, 10):  # E2:E9 corresponds to row indices 2 to 9
        #     worksheet.write(row, 7, "", self.right_border_format)

        # Apply right border to the range E2:E9
        # for row in range(
        #     1, nb_simulations + 1
        # ):  # E2:E9 corresponds to row indices 2 to 9
        #     worksheet.write(row + 11, 0, "", self.right_border_format)
        #     worksheet.write(row + 11, 8, "", self.left_border_format)

        # Define the format for the top blue border
        # top_blue_border = self.workbook.add_format(
        #     {"top": 5, "top_color": self.bbg_color}
        # )

        # # Apply top blue border to C2:D2
        # worksheet.write("B2", "", top_blue_border)
        # worksheet.write("C2", "", top_blue_border)
        # worksheet.write("D2", "", top_blue_border)
        # worksheet.write("E2", "", top_blue_border)
        # worksheet.write("F2", "", top_blue_border)
        # worksheet.write("G2", "", top_blue_border)
        # worksheet.write("H2", "", top_blue_border)

        # Apply top blue border to C10:D10
        # worksheet.write("B11", "", top_blue_border)
        # worksheet.write("C11", "", top_blue_border)
        # worksheet.write("D11", "", top_blue_border)
        # worksheet.write("E11", "", top_blue_border)
        # worksheet.write("F11", "", top_blue_border)
        # worksheet.write("G11", "", top_blue_border)
        # worksheet.write("H11", "", top_blue_border)

        # Define the format for the right border
        # angle_border_format = self.workbook.add_format(
        #     {
        #         "right": 5,
        #         "right_color": self.bbg_color,
        #         "top": 5,
        #         "top_color": self.bbg_color,
        #     }
        # )
        # worksheet.write("H2", "", angle_border_format)
        # Close the self.workbook

        for i in range(nb_simulations):
            i += offset
            worksheet.write(i + 9, 0, i + 1 - offset, self.background_format)

        # worksheet = self.draw_rectangle(
        #     worksheet,
        #     cellRef=f"B13:H{nb_simulations+13}",
        #     border_color=None,
        #     bg_color="white",
        # )

        worksheet.freeze_panes(13, 2)

    @log_execution_time
    def create_ws_stat(self):

        df = self.df_stats
        # Create a self.workbook and add a worksheet
        worksheet = self.workbook.add_worksheet("STATISTIQUES")
        # Protect the worksheet
        # worksheet.protect()

        # Define the cell format with black background and white font color.
        # cell_format = self.workbook.add_format(
        #     {
        #         "bg_color": "white",  # Background color
        #         "font_color": "white",
        #         "font_name": self.font_name,
        #     }
        # )

        # Write the DataFrame headers to the worksheet.
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, cell_format)

        # Write the DataFrame data to the worksheet.
        for row_num, row_data in enumerate(df.values):
            worksheet.write_row(row_num + 1, 0, row_data, cell_format)

        # Determine the number of rows in the DataFrame.
        num_rows = len(df)

        # Create a line chart object for 'prix_au_m2'.
        chart = self.workbook.add_chart({"type": "line"})

        # Configure the 'prix_au_m2' series.
        chart.add_series(
            {
                "name": "Prix au m2",
                "categories": f"=STATISTIQUES!$A$2:$A${num_rows + 1}",
                "values": f"=STATISTIQUES!$B$2:$B${num_rows + 1}",
                "data_labels": {
                    "value": True,
                    "position": "above",
                    "show_zero_values": False,
                },
                "y2_axis": False,  # Use primary y-axis
                # "marker": {"type": "circle"},
                # 'line': {'color': self.bbg_color},  # Set line to dotted and black
                "marker": {
                    "type": "circle",
                    "border": {"color": self.bbg_color},
                    "fill": {"color": self.bbg_color},
                },
            }
        )

        # Create a column chart object for 'nb_transactions'.
        chart2 = self.workbook.add_chart({"type": "column"})

        # Configure the 'nb_transactions' series.
        chart2.add_series(
            {
                "name": "Volume",
                "categories": f"=STATISTIQUES!$A$2:$A${num_rows + 1}",
                "values": f"=STATISTIQUES!$C$2:$C${num_rows + 1}",
                "data_labels": {
                    "value": True,
                    "angle": "inside_end",
                    "show_zero_values": False,
                },
                "y2_axis": True,  # Use secondary y-axis
                "fill": {"color": self.bbg_color},  # Set bar color to black
                "border": {"color": self.bbg_color},  # Set bar border color to black
            }
        )

        # Combine the two charts.
        chart.combine(chart2)

        # Add a title and axis labels to the combined chart.
        chart.set_title(
            {
                "name": "Prix au m2 et Volumes de transactions \nsource DVF",
                "name_font": {"color": self.chart_font_color, "name": self.font_name},
            }
        )
        chart.set_x_axis({"name": "Annee"})
        chart.set_y_axis({"name": "Prix au m2"})
        chart.set_y2_axis({"name": "Volume"})
        chart.set_x_axis(
            {
                "major_gridlines": {"visible": False},
                "major_tick_mark": "none",
                "num_font": {"color": self.chart_font_color, "name": self.font_name},
            }
        )
        chart.set_y_axis(
            {"major_gridlines": {"visible": False}, "major_tick_mark": "none"}
        )
        chart.set_y2_axis(
            {"major_gridlines": {"visible": False}, "major_tick_mark": "none"}
        )

        # Set chart size to 100% of the window
        chart.set_size({"width": 920, "height": 590})  # Adjust as needed

        # Insert the combined chart into the worksheet.
        worksheet.insert_chart("E2", chart)
        worksheet.freeze_panes(32, 24)
        worksheet.hide_gridlines(2)
        worksheet.protect()

    @log_execution_time
    def create_ws_stat_pieces(self, df, sheet_name):

        worksheet = self.workbook.add_worksheet(sheet_name)
        worksheet = apply_worksheet_with_basic_format(
            worksheet, format=self.background_format
        )

        # Write the DataFrame headers to the worksheet.
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, self.background_format)

        # Write the DataFrame data to the worksheet.
        for row_num, row_data in enumerate(df.values):
            worksheet.write_row(row_num + 1, 0, row_data, self.background_format)

        # Determine the number of rows in the DataFrame.
        num_rows = len(df)
        num_col = df.shape[1]

        # Create a line chart object for 'prix_au_m2'.
        col_name = {i - 96: chr(i).upper() for i in range(ord("a"), ord("z") + 1)}
        # prev_position = ''
        valid_val = False
        try:
            validation_list = df.iloc[:, 0].to_list()
            valid_val = True
        except:
            pass

        if sheet_name == "VOLUMES_PIECES" or sheet_name == "VOLUMES_SURFACES":
            chart = self.workbook.add_chart(
                {"type": "column", "subtype": "percent_stacked"}
            )

            chart.set_y_axis(
                {
                    "visible": False,
                    "name": None,
                    "major_gridlines": {"visible": False},
                    "minor_gridlines": {"visible": False},
                    "line": {"visible": False},
                    "tick_label": {"visible": False},
                    "tick_marks": {"visible": False},
                }
            )

            for r in range(1, num_rows + 1):
                chart.add_series(
                    {
                        "name": f"={sheet_name}!$A${r+1}",  # 'Prix au m2',
                        "categories": f"={sheet_name}!$B1:${col_name[num_col]}$1",
                        "values": f"={sheet_name}!$B${r+1}:${col_name[num_col]}${r+1}",
                        "data_labels": {
                            "value": True,
                            "position": "outside_end",  # Position of the labels
                            "font": {
                                "bold": True,
                                "color": "white",
                                "rotation": -90,
                            },  # Set the rotation angle (e.g., 45 degrees)
                        },
                        "y2_axis": False,  # Use primary y-axis
                    }
                )
            # Add a title and axis labels to the combined chart.
            if sheet_name == "VOLUMES_PIECES":
                title = "Historique des Volumes de ventes par pièce *"
            elif sheet_name == "VOLUMES_SURFACES":
                title = "Historique des Volumes de ventes par surface *"
            chart.set_title(
                {
                    "name": title,
                    "name_font": {
                        "color": self.chart_font_color,
                        "name": self.font_name,
                    },
                }
            )
            chart.set_x_axis({"name": "Annee"})
            # chart.set_y_axis({'name': 'Volume'})

        # self.color_palette

        elif sheet_name == "PRIX_PIECES":
            if  valid_val:
                worksheet.data_validation(
                    "B17", {"validate": "list", "source": validation_list[:-1]}
                )
                worksheet.data_validation(
                    "B18", {"validate": "list", "source": validation_list[:-1]}
                )
             


            self.workbook.define_name(
                "prix_q25",
                # "=OFFSET(PRIX_PIECES!$B$1, MATCH(PRIX_PIECES!$A$2, PRIX_PIECES!$A$1:$A$16, 0) - 1, 0, 1, COUNTA(PRIX_PIECES!$1:$1) - 1)",
                """=OFFSET(PRIX_PIECES!$B$1, MATCH("prix des 25% les moins cheres", PRIX_PIECES!$A$1:$A$16, 0) - 1, 0, 1, COUNTA(PRIX_PIECES!$1:$1) - 1)""",
            )
            self.workbook.define_name(
                "prix_q75",
                # "=OFFSET(PRIX_PIECES!$B$1, MATCH(PRIX_PIECES!$A$3, PRIX_PIECES!$A$1:$A$16, 0) - 1, 0, 1, COUNTA(PRIX_PIECES!$1:$1) - 1)",
                """=OFFSET(PRIX_PIECES!$B$1, MATCH("prix des 25% les plus cheres", PRIX_PIECES!$A$1:$A$16, 0) - 1, 0, 1, COUNTA(PRIX_PIECES!$1:$1) - 1)""",
            )
            self.workbook.define_name(
                "prix_q50",
                # "=OFFSET(PRIX_PIECES!$B$1, MATCH(PRIX_PIECES!$A$5, PRIX_PIECES!$A$1:$A$16, 0) - 1, 0, 1, COUNTA(PRIX_PIECES!$1:$1) - 1)",
                """=OFFSET(PRIX_PIECES!$B$1, MATCH("prix médian", PRIX_PIECES!$A$1:$A$16, 0) - 1, 0, 1, COUNTA(PRIX_PIECES!$1:$1) - 1)""",
            )
            self.workbook.define_name(
                "volumes",
                '=OFFSET(PRIX_PIECES!$B$1, MATCH("volume de transactions", PRIX_PIECES!$A$1:$A$16, 0) - 1, 0, 1, COUNTA(PRIX_PIECES!$1:$1) - 1)',
            )

            # chart = self.workbook.add_chart({'type': 'column'})
            chart = self.workbook.add_chart({"type": "line"})

            # chart.set_y_axis({'visible': False})
            chart.set_y_axis(
                {
                    "visible": False,
                    "name": None,
                    "major_gridlines": {"visible": False},
                    "minor_gridlines": {"visible": False},
                    "line": {"visible": False},
                    "tick_label": {"visible": False},
                    "tick_marks": {"visible": False},
                }
            )

            # Create a column chart object for 'nb_transactions'.
            chart2 = self.workbook.add_chart({"type": "column"})

            # Configure the 'nb_transactions' series.
            chart2.add_series(
                {
                    "name": "Volume",
                    "categories": f"={sheet_name}!$B1:${col_name[num_col]}$1",
                    "values": f"={sheet_name}!volumes",
                    "data_labels": {"value": True, "angle": "inside_end"},
                    "y2_axis": False,  # Use secondary y-axis
                    "fill": {"color": self.color_palette[0]},  # Set bar color to black
                    "border": {
                        "color": self.color_palette[0]
                    },  # Set bar border color to black
                }
            )
            chart2.set_title(
                {
                    "name": "Historique des volumes de transactions",
                    "name_font": {
                        "color": self.chart_font_color,
                        "name": self.font_name,
                    },
                }
            )

            chart2.set_legend({"none": True})

            chart2.set_x_axis(
                {
                    "major_gridlines": {"visible": False},
                    "major_tick_mark": "none",
                    "num_font": {
                        "color": self.chart_font_color,
                        "name": self.font_name,
                    },
                }
            )
            chart2.set_y_axis(
                {"major_gridlines": {"visible": False}, "major_tick_mark": "none"}
            )

            chart2.set_y_axis(
                {
                    "visible": False,
                    "name": None,
                    "major_gridlines": {"visible": False},
                    "minor_gridlines": {"visible": False},
                    "line": {"visible": False},
                    "tick_label": {"visible": False},
                    "tick_marks": {"visible": False},
                }
            )

            chart.add_series(
                {
                    "name": "1er quartile",
                    "categories": f"={sheet_name}!$B1:${col_name[num_col]}$1",
                    "values": f"={sheet_name}!prix_q25",
                    "data_labels": {
                        "value": True,
                        "position": "below",
                        "font": {"bold": False, "color": self.color_palette[0]},
                    },
                    "y2_axis": False,  # Use primary y-axis
                    "line": {
                        "color": self.color_palette[0]
                    },  # Set line to dotted and black
                    # "marker": {"type": "circle"},
                    "marker": {
                        "type": "circle",
                        "border": {"color": self.color_palette[0]},
                        "fill": {"color": self.color_palette[0]},
                    },
                    "y2_axis": False,  # Use primary y-axis
                }
            )

            chart.add_series(
                {
                    "name": "3ème quartile",
                    "categories": f"={sheet_name}!$B1:${col_name[num_col]}$1",
                    "values": f"={sheet_name}!prix_q75",
                    "data_labels": {
                        "value": True,
                        "position": "above",
                        "font": {"bold": False, "color": self.color_palette[1]},
                    },
                    "y2_axis": False,  # Use primary y-axis
                    "line": {
                        "color": self.color_palette[1]
                    },  # Set line to dotted and black
                    # "marker": {"type": "circle"},
                    "marker": {
                        "type": "circle",
                        "border": {"color": self.color_palette[1]},
                        "fill": {"color": self.color_palette[1]},
                    },
                    "y2_axis": False,  # Use primary y-axis
                }
            )

            chart.add_series(
                {
                    "name": "médiane",
                    "categories": f"={sheet_name}!$B1:${col_name[num_col]}$1",
                    "values": f"={sheet_name}!prix_q50",
                    "data_labels": {
                        "value": True,
                        "position": "below",
                        "font": {"bold": False, "color": self.color_palette[3]},
                    },
                    "y2_axis": False,  # Use primary y-axis
                    "line": {
                        "color": self.color_palette[3]
                    },  # Set line to dotted and black
                    # "marker": {"type": "circle"},
                    "marker": {
                        "type": "circle",
                        "border": {"color": self.color_palette[1]},
                        "fill": {"color": self.color_palette[3]},
                    },
                    "y2_axis": False,  # Use primary y-axis
                }
            )

            # Add a title and axis labels to the combined chart.
            chart.set_title(
                {
                    "name": "Historique des prix au m2 *",
                    "name_font": {
                        "color": self.chart_font_color,
                        "name": self.font_name,
                    },
                }
            )

            chart.set_x_axis({"name": "Annee"})
            # chart.set_legend(
            #     {"position": "top", "font": {"bold": False, "color": self.bg_color}}
            # )

            chart.set_legend({"position": "top", "font": {"bold": False}})

        chart.set_x_axis(
            {
                "major_gridlines": {"visible": False},
                "major_tick_mark": "none",
                "num_font": {"color": self.chart_font_color, "name": self.font_name},
            }
        )

        # chart.set_chartarea(
        #     {
        #         "border": {
        #             "color": self.border_color,  # Border color
        #             "width": 3,  # Border width
        #             "dash_type": "solid",  # Line style (solid, dash, etc.)
        #         }
        #     }
        # )
        if sheet_name == "PRIX_PIECES":
            chart.set_size({"width": 1350, "height": 365})  # Adjust as needed
            chart2.set_size({"width": 1350, "height": 120})

            # chart2.set_chartarea(
            #     {
            #         "border": {
            #             "color": self.border_color,  # Border color
            #             "width": 3,  # Border width
            #             "dash_type": "solid",  # Line style (solid, dash, etc.)
            #         }
            #     }
            # )

            worksheet.insert_chart("B2", chart)
            worksheet.insert_chart("B23", chart2)
            # Set the outer border of the chart

        else:
            chart.set_size({"width": 1100, "height": 400})  # Adjust as needed
            worksheet.insert_chart("D5", chart)

        self.set_title_format(fg_color=None, font_size=10, bold=None)
        if sheet_name == "PRIX_PIECES":
            text = build_text_prix(self.df_stats)
            if text:
                worksheet = add_title(
                    worksheet,
                    range="B21:V21",
                    text=text,
                    format=self.title_format,
                )
        else:
            if sheet_name == "VOLUMES_PIECES":
                text = build_text_pieces(df)
            else:
                text = build_text_surfaces(df)
            worksheet = add_title(
                worksheet,
                range="B27:V27",
                text=text,
                format=self.title_format,
            )

        worksheet.freeze_panes(32, 24)
        worksheet.hide_gridlines(2)

    @log_execution_time
    def create_ws_distrib_decotes(self, df, sheet_name):
        # print(df.head())
        worksheet = self.workbook.add_worksheet(sheet_name)
        transparent_format = self.workbook.add_format(
            {
                "bg_color": "white",  # Background color
                "font_color": "white",
                "font_name": self.font_name,
            }
        )

        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, transparent_format)

        for row_num, row_data in enumerate(df.values):
            worksheet.write_row(row_num + 1, 0, row_data, transparent_format)
        # print(f'######### : {3}')
        self.workbook.define_name(
            "decotes", "=OFFSET(DECOTES!$B$1, 1, 0,COUNTA(DECOTES!$A:$A) - 1, 1)"
        )
        self.workbook.define_name(
            "distributions", "=OFFSET(DECOTES!$C$1, 1, 0, COUNTA(DECOTES!$A:$A) - 1, 1)"
        )

        # Compute bin edges automatically using numpy's histogram_bin_edges
        bin_edges = np.histogram_bin_edges(df["Decote_prix_median"], bins="auto")
        # print(bin_edges)
        df["Binned"] = pd.cut(
            df["Decote_prix_median"], bins=bin_edges, include_lowest=True
        )
        bin_counts = df["Binned"].value_counts().sort_index()

        # Write the headers
        worksheet.write("E1", "Bins", transparent_format)
        worksheet.write("F1", "Counts", transparent_format)

        # Write the bins and counts to the worksheet
        for row_num, (bin_range, count) in enumerate(bin_counts.items(), start=1):
            worksheet.write(
                row_num, 4, f"{bin_range.left} - {bin_range.right}", transparent_format
            )
            worksheet.write(row_num, 5, count, transparent_format)

        if df["Decote_prix_median"].sum() != 0:
            # Create a column chart to represent the histogram
            chart = self.workbook.add_chart({"type": "column"})
            chart.set_legend({"none": True})

            # Configure the chart with the bins and counts
            chart.add_series(
                {
                    "categories": f"=DECOTES!$E$2:$E${len(bin_counts) + 1}",
                    "values": f"=DECOTES!$F$2:$F${len(bin_counts) + 1}",
                    "name": "Histogram",
                    "fill": {"color": self.bbg_color},  # Set bar color to black
                    "border": {
                        "color": self.bbg_color
                    },  # Set bar border color to black
                }
            )

            # Add chart title and labels
            chart.set_title(
                {
                    "name": "Répartition des décotes",
                    "name_font": {
                        "color": self.chart_font_color,
                        "name": self.font_name,
                    },
                }
            )
            chart.set_x_axis({"name": "Bins"})
            chart.set_y_axis({"name": "Counts"})

            # Insert the chart into the worksheet
            chart.set_size({"width": 1170, "height": 550})
            chart.set_x_axis(
                {
                    "major_gridlines": {"visible": False},
                    "major_tick_mark": "none",
                    "num_font": {
                        "color": self.chart_font_color,
                        "name": self.font_name,
                    },
                }
            )
            chart.set_y_axis(
                {
                    "visible": False,
                    "name": None,
                    "major_gridlines": {"visible": False},
                    "minor_gridlines": {"visible": False},
                    "line": {"visible": False},
                    "tick_label": {"visible": False},
                    "tick_marks": {"visible": False},
                }
            )

            worksheet.insert_chart("C3", chart)

        worksheet.hide()

        worksheet.hide_gridlines(2)
        worksheet.freeze_panes(32, 24)

    @log_execution_time
    def create_ws_scoring(self, df, sheet_name):

        worksheet = self.workbook.add_worksheet(sheet_name)
        worksheet = apply_worksheet_with_basic_format(
            worksheet, format=self.background_format
        )

        worksheet.set_column("H:H", 40, self.background_format)
        worksheet.set_column("I:I", 40, self.background_format)

        # Write the DataFrame headers to the worksheet.
        for col_num, value in enumerate(df.columns.values):
            # worksheet.write(0, col_num, value, cell_format)
            worksheet.write(0, col_num, value, self.background_format)

        # Write the DataFrame data to the worksheet.
        for row_num, row_data in enumerate(df.values):
            # worksheet.write_row(row_num + 1, 0, row_data, cell_format)
            worksheet.write_row(row_num + 1, 0, row_data, self.background_format)

        self.workbook.define_name("selection", f"={sheet_name}!$H$10")
        self.workbook.define_name(
            "voies",
            f"=OFFSET({sheet_name}!$B$1, 1, 0,COUNTA({sheet_name}!$A:$A) - 1, 1)",
        )
        self.workbook.define_name(
            "classements",
            f"=OFFSET({sheet_name}!$C$1, 1, 0,COUNTA({sheet_name}!$A:$A) - 1, 1)",
        )
        self.workbook.define_name(
            "scores",
            f"=OFFSET({sheet_name}!$D$1, 1, 0,COUNTA({sheet_name}!$A:$A) - 1, 1)",
        )
        
        # print(validation_list)

        # font_size = 20
        # merge_format = self.workbook.add_format({
        #                   'bold': 1,
        #                   'border': 0,
        #                   'align': 'center',
        #                   'valign': 'vcenter',
        #                   'fg_color': self.bbg_color,
        #                   'font_color':'white',
        #                   'font_size': font_size}
        #                   )

        # merge_format_neutral = self.workbook.add_format({
        #                   'bold': 1,
        #                   'border': 0,
        #                   'align': 'center',
        #                   'valign': 'vcenter',
        #                   # 'fg_color': self.bbg_color,
        #                   'font_color':self.bbg_color,
        #                   'font_size': int(font_size*.8),
        #                   'fg_color': self.neural_color,}
        #                   )

        worksheet = self.draw_rectangle(
            worksheet, cellRef="G7:J15", border_color=None, bg_color=None
        )

        self.set_title_format(fg_color=None, font_size=None, bold=None)

        worksheet = add_title(
            worksheet,
            range="H9:I9",
            text="Sélectionner Une Voie",
            format=self.title_format,
        )
        # worksheet.merge_range("H9:I9", "Sélectionner une voie", self.merge_format)

        print("df.shape",df.shape)
        try: 
            validation_list = df.iloc[:, 1].to_list()
            worksheet.data_validation(
                "H10", {"validate": "list", "source": f"B2:B{len(validation_list)+1}"}
            )

            worksheet.merge_range("H10:I10", validation_list[0], self.merge_format_neutral)
            print("valadation list first try success")
        except:
            print("valadation list second try start")
            try:
                validation_list = df.iloc[:, 0].to_list()
                worksheet.data_validation(
                    "H10", {"validate": "list", "source": f"B2:B{len(validation_list)+1}"}
                )

                worksheet.merge_range("H10:I10", validation_list[0], self.merge_format_neutral)
                print("valadation list second try success")
            except:
                zns = 1
                worksheet.data_validation(
                    "H10", {"validate": "list", "source": f"B2:B{zns}"}
                )

                worksheet.merge_range("H10:I10", 1, self.merge_format_neutral)
                print("valadation list end try success")


        

        # worksheet.write("H12", "Score", self.merge_format)
        worksheet = add_title(
            worksheet,
            range="H12",
            text="Score *",
            format=self.title_format,
            multiple_cell=False,
        )
        worksheet.write_formula(
            "H13",
            "=INDEX(scores, MATCH(selection, voies, 0), 1)",
            self.merge_format_neutral,
        )

        # worksheet.write("I12", "Classement", self.merge_format)

        worksheet = add_title(
            worksheet,
            range="I12",
            text="Classement *",
            format=self.title_format,
            multiple_cell=False,
        )
        worksheet.write_formula(
            "I13",
            '=INDEX(classements, MATCH(selection,voies,0),1)&"/"&MAX(classements)',
            self.merge_format_neutral,
        )

        self.set_title_format(fg_color=self.bg_color, font_size=10, bold=0)

        worksheet = add_title(
            worksheet,
            range="G17:J17",
            text="* Score de 1 à 4, plus le score et le classement sont élevés, plus les prix de la voie est élevé.",
            format=self.title_format,
        )
        worksheet.freeze_panes(30, 18)

    @log_execution_time
    def create_ws_optimal_auction(self, sheet_name):

        worksheet = self.workbook.add_worksheet(sheet_name)
        worksheet = apply_worksheet_with_basic_format(
            worksheet, format=self.background_format
        )

        self.set_money_format(
            fg_color="white", font_size=11, font_color=None, bold=None, locked=True
        )
        self.set_percent_format(
            fg_color="white", font_size=11, font_color=None, bold=None
        )

        worksheet.set_column("A:C", 6, self.background_format)
        worksheet.set_column("D:D", 25, self.background_format)
        worksheet.set_column("E:E", 12, self.background_format)
        worksheet.set_column("J:J", 13, self.background_format)
        worksheet.set_column("P:P", 4.43, self.background_format)
        worksheet.set_column("Q:R", 14, self.background_format)
        # # Write the DataFrame headers to the worksheet.
        # for col_num, value in enumerate(df.columns.values):
        #     worksheet.write(0, col_num, value, self.background_format)

        # # Write the DataFrame data to the worksheet.
        # for row_num, row_data in enumerate(df.values):
        #     worksheet.write_row(row_num + 1, 0, row_data, self.background_format)

        # # Determine the number of rows in the DataFrame.
        # num_rows = len(df)
        # num_col = df.shape[1]

        # # Create a line chart object for 'prix_au_m2'.
        # col_name = {i - 96: chr(i).upper() for i in range(ord("a"), ord("z") + 1)}
        # # prev_position = ''
        # validation_list = df.iloc[:, 0].to_list()
        # if sheet_name == "VOLUMES_PIECES" or sheet_name == "VOLUMES_SURFACES":
        chart = self.workbook.add_chart({"type": "line"})

        chart.set_y_axis(
            {
                "visible": True,
                "name": None,
                "major_gridlines": {"visible": False},
                "minor_gridlines": {"visible": False},
                "line": {"visible": False},
                "tick_label": {"visible": False},
                "tick_marks": {"visible": False},
            }
        )

        # Configure the first series (Rentabilité Potentielle)
        chart.add_series(
            {
                "name": "Rentabilité Potentielle",
                "categories": "=SIMULATEUR_2!prix_adjudication",
                "values": "=SIMULATEUR_2!courbe_renta",
                "line": {"color": self.color_palette[0]},
            }
        )

        # chart.set_legend(
        #     {"position": "top", "font": {"bold": False, "color": self.bg_color}}
        # )

        chart.set_legend({"position": "top", "font": {"bold": False}})
        # Configure the second series (Probabilité d\'Obtention)
        chart.add_series(
            {
                "name": "Probabilité d'Obtention",
                "categories": "=SIMULATEUR_2!prix_adjudication",
                "values": "=SIMULATEUR_2!courbe_proba",
                "line": {"color": self.color_palette[1]},
            }
        )
        # Add a title and axis labels to the combined chart.
        chart.set_title(
            {
                "name": "Rentabilité vs. Probabilité d'Obtention",
                "name_font": {"color": self.chart_font_color, "name": self.font_name},
            }
        )

        chart.set_x_axis(
            {
                "name": "Prix d'Adjudication",
                "major_gridlines": {"visible": False},
                "major_tick_mark": "none",
                "label_position": "low",
                "num_font": {
                    "color": self.chart_font_color,
                    "name": self.font_name,
                    "rotation": -45,
                    "size": 8,
                },
                "name_font": {"color": self.chart_font_color, "name": self.font_name},
            }
        )

        # chart.set_y_axis({'name': 'Volume'})

        chart.set_size({"width": 1180, "height": 350})
        worksheet.insert_chart("D11", chart)

        self.set_title_format(fg_color=None, font_size=None, bold=None)
        worksheet = add_title(
            worksheet,
            range="D2:E2",
            text="AU PRIX DE MARCHE",
            format=self.title_format,
        )

        worksheet = add_title(
            worksheet,
            range="G2:J2",
            text="AU PRIX LIMITE",
            format=self.title_format,
        )

        # self.set_title_format(fg_color=None, font_size=None, bold=None)
        worksheet = add_title(
            worksheet,
            range="L2:R2",
            text="PLAGE D'ENCHERES OPTIMALE *",
            format=self.title_format,
        )
        self.set_title_format(fg_color=self.bg_color, font_size=10, bold=None)
        worksheet = add_title(
            worksheet,
            range="D30:R30",
            text="* La plage d'enchère optimale permet de garantir la rentabilité de votre opération tout en maximisant la probabilité d'obtention de l'enchère. Elle est présentée à titre indicatif.",
            format=self.title_format,
        )

        worksheet = write_text(
            worksheet,
            text=build_metrics_text(header="Prix de marché"),
            ref_cell="D4",
            format=self.info_fmt,
        )

        worksheet = write_text(
            worksheet,
            text=build_metrics_text(header="Prix limite"),
            ref_cell="G4",
            format=self.info_fmt,
        )

        worksheet = write_text(
            worksheet,
            text=build_metrics_text(header="Prix d'Adjudication"),
            ref_cell="L4",
            format=self.info_fmt,
        )
        # ############# Au Prix de Marché
        # self.set_money_format(
        #     fg_color=None, font_size=11, font_color="white", bold=None
        # )
        worksheet.write_formula(
            "E4",
            "prix_marche",
            self.money_fmt,
        )
        worksheet.write(
            "E5",
            0,
            self.percent_fmt,
        )

        worksheet.write(
            "E6",
            "-",
            self.money_fmt,
        )

        worksheet.write(
            "E7",
            "-",
            self.money_fmt,
        )

        worksheet.write(
            "E8",
            "-",
            self.money_fmt,
        )

        worksheet.write(
            "E9",
            "-",
            self.money_fmt,
        )

        # ############# Plage d'Enchère Optimale
        worksheet.write_formula(
            "J4",
            "prix_limite",
            self.money_fmt,
        )
        worksheet.write_formula(
            "J5",
            "decote",
            self.percent_fmt,
        )

        worksheet.write_formula(
            "J6",
            "cout_total_s2",
            self.money_fmt,
        )

        worksheet.write_formula(
            "J7",
            "proba_s2",
            self.percent_fmt,
        )

        worksheet.write_formula(
            "J8",
            "plus_value_s2",
            self.money_fmt,
        )

        worksheet.write_formula(
            "J9",
            "renta_s2",
            self.percent_fmt,
        )

        worksheet.write_formula(
            "Q4",
            "min_adju",
            self.money_fmt,
        )

        worksheet.write_formula(
            "R4",
            "max_adju",
            self.money_fmt,
        )

        worksheet.write_formula(
            "Q5",
            "max_decote",
            self.percent_fmt,
        )

        worksheet.write_formula(
            "R5",
            "min_decote",
            self.percent_fmt,
        )

        worksheet.write_formula(
            "Q6",
            "min_cout",
            self.money_fmt,
        )

        worksheet.write_formula(
            "R6",
            "max_cout",
            self.money_fmt,
        )

        worksheet.write_formula(
            "Q7",
            "min_proba",
            self.percent_fmt,
        )

        worksheet.write_formula(
            "R7",
            "max_proba",
            self.percent_fmt,
        )

        worksheet.write_formula(
            "Q8",
            "max_pv",
            self.money_fmt,
        )

        worksheet.write_formula(
            "R8",
            "min_pv",
            self.money_fmt,
        )
        worksheet.write_formula(
            "Q9",
            "max_renta",
            self.percent_fmt,
        )

        worksheet.write_formula(
            "R9",
            "min_renta",
            self.percent_fmt,
        )

        worksheet.freeze_panes(30, 22)

    multiple_cell = True

    @log_execution_time
    def create_ws_frais(self):
        worksheet = self.workbook.add_worksheet("FRAIS")

        # Define formats
        header_format = self.workbook.add_format(
            {
                "bold": True,
                "font_color": "black",
                "bg_color": "#d9e1f2",
                "align": "center",
                "font_name": self.font_name,
            }
        )
        money_format = self.workbook.add_format(
            {"num_format": "# ##0 €", "align": "right"}
        )
        info_format = self.workbook.add_format(
            {"italic": True, "font_color": "gray", "font_name": self.font_name}
        )

        # Set column widths
        worksheet.set_column("A:A", 30)
        worksheet.set_column("B:B", 20)

        # Write headers
        worksheet.write("A1", "Description", header_format)
        worksheet.write("B1", "Montant Estimé", header_format)

        # Write cost descriptions and estimated amounts
        costs = [
            (
                "Chèque de banque pour caution (10% de la mise à prix, min 3 000 €)",
                "=MAX(3000, 0.1 * mise_a_prix)",
            ),
            ("Chèque de banque pour frais et honoraires", 10000),
            ("Frais préalables de saisie", "Entre 7000 et 13000 €"),
            ("Frais de représentation (200 à 600 €)", "Entre 200 et 600 €"),
            ("Honoraires d'adjudication (2000 à 6000 €)", "Entre 2000 et 6000 €"),
            ("Émoluments de vente", "Calculés selon le prix d'adjudication"),
            (
                "Droits d'enregistrement (5.81% pour particuliers)",
                "=prix_marche * 0.0581",
            ),
            (
                "Frais de publication (0.1% du prix de vente + 12 €)",
                "=prix_marche * 0.001 + 12",
            ),
            ("Autres frais de procédure", "Variables, à vérifier avec l'avocat"),
            ("Coût total de l'enchère", "Généralement entre 15000 € et 25000 €"),
        ]

        # Write costs to the worksheet
        for row, (description, amount) in enumerate(costs, start=2):
            worksheet.write(row, 0, description)
            worksheet.write(
                row,
                1,
                amount if isinstance(amount, (int, float)) else amount,
                info_format,
            )

        # Add a summary row
        worksheet.write(row + 1, 0, "Total Estimé", header_format)
        worksheet.write_formula(row + 1, 1, f"=SUM(B2:B{row})", money_format)

        # Freeze the header row
        worksheet.freeze_panes(1, 0)
