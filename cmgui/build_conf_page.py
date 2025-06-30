"""The `build_conf_page` GUI module allows to built consolidated
list of contributions to conferences extracted from HAL database 
for the Institute selected.
"""

__all__ = ['build_conf_list']

# Standard library imports
import os
import threading
import tkinter as tk
from functools import partial
from pathlib import Path
from tkinter import font as tkFont
from tkinter import messagebox
from tkinter import ttk

# 3rd party imports
import bmgui.gui_globals as bm_gg
import pandas as pd
from bmfuncts.config_utils import set_org_params
from bmgui.gui_utils import disable_buttons
from bmgui.gui_utils import enable_buttons
from bmgui.gui_utils import font_size
from bmgui.gui_utils import mm_to_px
from bmgui.gui_utils import place_after
from bmgui.gui_utils import place_bellow
from bmgui.gui_utils import set_exit_button
from bmgui.gui_utils import set_page_title

# Local imports
import cmgui.cm_gui_globals as cm_gg
from cmfuncts.build_employees import adapt_search_depth
from cmfuncts.build_employees import read_hal_employees_data
from cmfuncts.build_employees import set_empl_paths
from cmfuncts.build_employees import update_hal_employees_data
from cmfuncts.conf_extract import read_conf_extract
from cmfuncts.conf_extract import set_extract_paths
from cmfuncts.conf_extract import set_hal_to_conf
from cmfuncts.consolidate_conf_list import build_final_conf_list
from cmfuncts.consolidate_conf_list import set_results_paths
from cmfuncts.merge_conf_employees import recursive_year_search
from cmfuncts.merge_conf_employees import set_merge_paths


def _launch_update_hal_employees_try(wf_root_path, progress_callback):
    """Launches adaptation of Intitute employees data to HAL extractions.

    This is done through the `update_hal_employees_data` function imported from 
    `cmfuncts.build_employees` module after check availability of original 
    file of Institute's employees data. 
    The useful file names and paths are built through the `set_empl_paths` 
    function imported from `cmfuncts.build_employees` module.

    Args:
        wf_root_path (path): The full path to the root folder where \
        the folder of Institute parameters is located.
        progress_callback (function): Function for updating \
        ProgressBar tkinter widget status.
    """    
    # Setting files parameters of employees data
    paths_list, filenames_list = set_empl_paths(wf_root_path)
    empl_file_name, hal_empl_file_name = filenames_list
    empl_folder_path, all_empl_path, hal_all_empl_path = paths_list
    progress_callback(5)

    # Initializing returned parameters
    empl_update_status, hal_all_empl_dict = False, {}
    
    # Checking availability of employees-data file 
    if os.path.isfile(all_empl_path):
        # Launch employees database update
        ask_title = "- Confirmation de la mise en conformité des effectifs -"
        ask_text = (f"Une copie du fichier '{empl_file_name}' des effectifs de l'Institut "
                    f"qui se trouve dans le dossier :\n   {empl_folder_path}"
                    "\n\nva être mise en conformité avec les extractions de HAL "
                    "pour les croisements auteurs-effectifs."
                    "\n\nCette opération peut prendre quelques minutes."
                    "\nDans l'attente, ne pas fermer l'application."
                    "\n\nAvant de commencer les traitements annuels par année, "
                    "confirmez-vous la mise en conformité ?")
        answer_1 = messagebox.askokcancel(ask_title, ask_text)
        if answer_1:
            return_tup = update_hal_employees_data(wf_root_path, progress_callback)
            empl_update_status, hal_all_empl_dict = return_tup
            if empl_update_status:
                info_title = "- Information -"
                info_text = ("La mise en conformité des effectifs a été effectuée."
                             f"\nLe fichier créé se nomme :\n\n   {hal_empl_file_name} "
                             f"\n\net se trouve dans le dossier :\n   {empl_folder_path}."
                             "\n\nLes traitements par année peuvent être effectués.")
                messagebox.showinfo(info_title, info_text)
            else:
                progress_callback(100)
                warning_title = "!!! ATTENTION : fichier vide !!!"
                warning_text = ("La mise en conformité des effectifs ne peut pas être effectuée "
                                f"car le fichier '{empl_file_name}' des effectifs de l'Institut "
                                f"qui se trouve dans le dossier :\n   {empl_folder_path} \n\nest vide."
                                "\n\n1- Mettez à jour ce fichier ;"
                                "\n\n2- Puis, relancez la mise en conformité.")
                messagebox.showwarning(warning_title, warning_text)
        else:
            progress_callback(100)
            # Checking availability of adapted-employees-data file
            if os.path.isfile(hal_all_empl_path):
                info_text = f"La mise en conformité des effectifs a été abandonnée."
                info_text += ("\n\nLes traitements par année peuvent être effectués "
                              "mais le croisement se fera avec le fichier :"
                              f"\n\n   '{hal_empl_file_name}' "
                              "\n\nexistant.")
                messagebox.showinfo(info_title, info_text)
            else:    
                warning_title = "!!! ATTENTION : fichier manquant !!!"
                warning_text = ("La mise en conformité des effectifs a été abandonnée."
                                f"\nOr, le fichier : \n\n   {hal_empl_file_name}"
                                "\n\n des effectifs de l'Institut, adapté aux extractions "
                                "de HAL est manquant dans le dossier :"
                                f"\n   {empl_folder_path}."
                                "\n\nLes traitements par année ne peuvent pas être effectués."
                                "\n\n1- Relancez la mise en conformité ;"
                                "\n\n2- Puis, confirmez la mise en conformité.")
                messagebox.showwarning(warning_title, warning_text)
    else:
        progress_callback(100)
        warning_title = "!!! ATTENTION : fichier manquant !!!"
        warning_text = ("La mise en conformité des effectifs ne peut pas être effectuée "
                        f"car le fichier :\n\n'   {empl_file_name}'\n\ndes effectifs "
                        " de l'Institut est manquant dans le dossier :"
                        f"\n   {empl_folder_path}."
                        "\n\n1- Mettez à jour ce dossier ;"
                        "\n\n2- Puis, relancez la mise en conformité.")
    return empl_update_status, hal_all_empl_dict


def _launch_set_hal_to_conf_try(institute, wf_path,
                                year_select, progress_callback):
    """Launches extraction of contributions to conferences from the HAL database.

    This is done through the `set_hal_to_conf` function imported from 
    `cmfuncts.conf_extract` module.

    Args:
        institute (str): Institute name.
        wf_path (path): Full path to working folder.
        year_select (str): Corpus year defined by 4 digits.
        progress_callback (function): Function for updating ProgressBar tkinter \
        widget status. 
    """
    # Setting files parameters of extracted data
    paths_list, filenames_list = set_extract_paths(wf_path, year_select)
    year_full_file, year_conf_file = filenames_list
    hal_corpus_path, full_file_path, conf_file_path = paths_list
    progress_callback(5)

    # Launch HAL extraction of contributions to conferences
    ask_title = "- Extraction des contributions à conférence -"
    ask_text = (f"L'extraction va être effectuée pour l'année {year_select} "
                "depuis la base de données HAL."
                "\n\nConfirmez-vous l'extraction ?")
    answer_1 = messagebox.askokcancel(ask_title, ask_text)
    if answer_1:
        _ = set_hal_to_conf(institute, wf_path, year_select, progress_callback)
        end_message = f"\nExtraction of contributions to conferences performed for {year_select}"
        print('\n',end_message)
        info_title = "- Information -"
        info_text = ("L'extraction des contributions à conférence a été effectuée "
                     f"pour l'année {year_select}."
                     "\n\nCette opération a créé deux fichiers:"
                     f"\n\n  - '{year_full_file}' : qui contient toutes les types de publication; "
                     f"\n  - '{year_conf_file}' : limité aux contributions à conférence."
                     f"\n\nCes fichiers se trouvent dans le dossier :\n   {hal_corpus_path}."
                     "\n\nLe croisement auteurs-effectifs peut être lancé.")
        messagebox.showinfo(info_title, info_text)
    else:
        progress_callback(100)
        # Checking availability of HAL extractions file
        if os.path.isfile(conf_file_path):
            info_text = ("L'extraction des contributions à conférence a été annulée "
                         f"pour l'année {year_select}."
                         "\n\nLe croisement auteurs_effectifs peut être lancé "
                         "mais il se fera à partir du fichier des contributions "
                         f"à conférence nommé :\n\n  {year_conf_file}\n\n existant "
                         f"dans le dossier :\n   {hal_corpus_path}.")
            messagebox.showinfo(info_title, info_text)
        else:    
            warning_title = "!!! ATTENTION : fichier manquant !!!"
            warning_text = ("L'extraction des contributions à conférence a été annulée "
                            f"pour l'année {year_select}."
                            f"\n\nLe fichier '{year_conf_file}' des contributions à conférence "
                            "est manquant dans le dossier :"
                            f"\n   {hal_corpus_path}."
                            "\n\nLe croisement auteurs_effectifs ne peut pas être lancé."
                            "\n\nRelancez l'extraction.")
            messagebox.showwarning(warning_title, warning_text)


def _launch_recursive_year_search_try(institute,
                                      wf_root_path,
                                      wf_path,
                                      year_select,
                                      empl_update_status,
                                      hal_all_empl_dict,
                                      progress_callback):
    """Launches merge of the list of contributions to conferences with 
    Institute employees for the selected year.

    This is done through the `recursive_year_search` function imported from 
    `cmfuncts.merge_conf_employees` module after:

    - setting the extracted contributions to conferences through the \
    `read_conf_extract` function imported from `cmfuncts.conf_extract` \
    module.
    - setting employees data if the existing dict is empty through the \
    `read_hal_employees_data` function imported from the \
    `cmfuncts.build_employees` module.

    Args:
        institute (str): Institute name.
        wf_path (path): Full path to working folder.
        year_select (str): Corpus year defined by 4 digits.
        progress_callback (function): Function for updating ProgressBar \
        tkinter widget status. 
    """
    # Internal function
    def _recursive_year_search_try(progress_callback):
        _, empl_use_years = adapt_search_depth(year_select, hal_all_empl_dict)
        if empl_use_years:
            _, _ = recursive_year_search(wf_root_path, wf_path, year_select,
                                         employees_dict=hal_all_empl_dict,
                                         years_to_search=empl_use_years,
                                         progress_callback=progress_callback)
            print("Merge of contributions to conferences with employees "
                  f"data performed for {year_select}")
            info_title = '- Information -'
            info_text = f"Le croisement auteurs-effectifs de l'année {year_select} a été effectué."
            info_text += ("\n\nExaminez le fichier des auteurs qui n'ont pas été "
                          "identifiés dans les effectifs et vérifiez que tous ceux "
                          "affiliés à l'Institut ont été pris en compte. \n Pour cela :"
                          f"\n\n1- Ouvrez le fichier {orphan_file_name} "
                          f"du dossier :\n  {conf_empl_folder_path} ;"
                          "\n\n2- Suivez le mode opératoire disponible pour son utilisation ;"
                          "\n3- Puis relancez le croisement pour cette année."
                          "\n\nNéanmoins, la consolidation de la liste des contributions "
                          "à conférence peut être lancée sans cette opération, "
                          "mais la liste sera peut-être incomplète.")
            messagebox.showinfo(info_title, info_text)
        else:
            progress_callback(100)
            warning_title = "!!! Attention !!!"
            warning_text  = ("Le nombre d'années disponibles est insuffisant "
                             "dans le fichier des effectifs de l'Institut."
                             "\nLe croisement auteurs-effectifs ne peut être effectué !"
                             "\n1- Complétez le fichier des effectifs de l'Institut ;"
                             "\n2- Puis relancez le croisement auteurs-effectifs.")
            messagebox.showwarning(warning_title, warning_text)

    # Setting files parameters for merged data
    paths_list, filenames_list = set_merge_paths(wf_path, year_select)
    conf_empl_folder_path, valid_file_path, _ = paths_list
    _, orphan_file_name = filenames_list    
    progress_callback(5)

    # Setting dialogs and checking answers for ad-hoc use
    # of '_recursive_year_search_try' internal function

    if not hal_all_empl_dict:
        print("\nReading employees data...")
        hal_all_empl_dict = read_hal_employees_data(wf_root_path)
    else:
        print("\nEmployees data already available as dict...")
    progress_callback(10)

    status = "sans"
    if empl_update_status:
        status = "avec"

    ask_title = "- Confirmation du croisement auteurs-effectifs -"
    ask_text = ("Le croisement avec les effectifs a été lancé pour "
                f"l'année {year_select}."
                f"\nCe croisement se fera {status} la mise à jour "
                "du fichier des effectifs."
                "\n\nCette opération peut prendre quelques minutes."
                "\nDans l'attente, ne pas fermer l'application."
                "\n\nConfirmez le croisement ?")
    answer = messagebox.askokcancel(ask_title, ask_text)
    if answer:
        merge_status = os.path.exists(valid_file_path)
        if not merge_status:
            _recursive_year_search_try(progress_callback)
        else:
            ask_title = "- Reconstruction du croisement auteurs-effectifs -"
            ask_text = (f"Le croisement pour l'année {year_select} est déjà disponible."
                        "\n\nReconstruire le croisement ?")
            answer_4 = messagebox.askokcancel(ask_title, ask_text)
            if answer_4:
                _recursive_year_search_try(progress_callback)
            else:
                progress_callback(100)
                info_title = "- Information -"
                info_text = (f"Le croisement auteurs-effectifs de l'année {year_select} "
                             "dejà disponible est conservé.")
                messagebox.showinfo(info_title, info_text)
    else:
        progress_callback(100)
        info_title = "- Information -"
        info_text = (f"Le croisement auteurs-effectifs de l'année {year_select} "
                     "est annulé.")
        messagebox.showinfo(info_title, info_text)


def _launch_conf_list_conso_try(institute, org_tup, wf_path,
                                year_select, progress_callback):
    """Launches merge of publications list with Institute employees.

    This is done through the `recursive_year_search` function imported from 
    `bmfuncts.merge_pub_employees` module after:

    - setting employees data through `_set_employees_data` function 
    - check of status of parsing step through `check_dedup_parsing_available` \
    function imported from `bmfuncts.useful_functs` module.

    Args:
        institute (str): Institute name.
        org_tup (tup): Contains Institute parameters.
        wf_path (path): Full path to working folder.
        year_select (str): Corpus year defined by 4 digits.
        progress_callback (function): Function for updating ProgressBar tkinter \
        widget status. 
    """
    def _consolidate_conf_list(progress_callback):
        return_tup = build_final_conf_list(wf_path, org_tup, year_select,
                                           progress_callback=progress_callback)
        _, split_ratio, conf_nb = return_tup
    
        end_message = ("Consolidation of contributions to conferences "
                       f"performed for {year_select}")
        print(end_message)
        progress_callback(100)
        info_title = "- Information -"
        info_text = (f"Une liste consolidée de {conf_nb} contributions à conférence a été créée "
                     f"pour l'année {year_select} dans le dossier :\n\n '{results_folder_path}' "
                     f"\n\nsous le nom :   '{conf_file_name}'."
                     f"\n\nPar ailleurs, cette liste consolidée a été décomposée à {split_ratio} % "
                      "en deux fichiers disponibles dans le même dossier séparant les oraux des 'posters'."
                      "\n\nUne classe 'Autres' a été prévue en complément.")
        messagebox.showinfo(info_title, info_text)        
    
    # Setting parameters for final results
    paths_list, names_list = set_results_paths(wf_path, year_select, 'conferences')
    results_folder_path, conf_df_path = paths_list
    conf_file_name, _ = names_list

    # Setting dialogs and checking answers for ad-hoc use
    # of '_consolidate_conf_list' internal function
    ask_title = ("- Confirmation de la consolidation "
                 "de la liste des contributions à conférence -")
    ask_text = ("La création du fichier de la liste consolidée "
                f"a été lancée pour l'année {year_select}."
                "\n\nContinuer ?")
    answer = messagebox.askokcancel(ask_title, ask_text)
    if answer:
        progress_callback(10)
        conf_list_status = os.path.exists(conf_df_path)
        if not conf_list_status:
            _consolidate_conf_list(progress_callback)
        else:
            ask_title = ("- Reconstruction de la liste consolidée "
                         "des contributions à conférence -")
            ask_text = ("Le fichier de la liste consolidée  "
                        f"de l'année {year_select} est déjà disponible."
                        "\n\nReconstruire ce fichier ?")
            answer_1 = messagebox.askokcancel(ask_title, ask_text)
            if answer_1:
                _consolidate_conf_list(progress_callback)
            else:
                progress_callback(100)
                info_title = "- Information -"
                info_text = ("Le fichier de la liste consolidée "
                             "des contributions à conférence "
                             f"de l'année {year_select} dejà "
                             "disponible est conservé.")
                messagebox.showinfo(info_title, info_text)
    else:
        progress_callback(100)
        info_title = "- Information -"
        info_text = ("La création du fichier de la liste "
                     "consolidée des publications "
                     f"de l'année {year_select} est annulée.")
        messagebox.showinfo(info_title, info_text)


def build_conf_list(self, master, page_name, institute, wf_path):
    """Manages creation and use of widgets for corpus consolidation 
    through merge with Institute employees database.

    Args:
        self (instense): Instense where consolidation page will be created.
        master (class): `cmgui.main_page.AppMain` class.
        page_name (str): Name of consolidation page.
        institute (str): Institute name.
        wf_path (path): Full path to working folder.
    """

    # Internal functions
    def _set_step_label(self, step_num):
        """Sets the label and place of step-label widget in the page.

        Args:
            step_num (int): The order of the step in 'STEP_LABELS_LIST' global.
        """
        step_label = tk.Label(self,
                              text=cm_gg.STEP_LABELS_LIST[step_num],
                              justify=step_label_format,
                              font=step_label_font,
                              underline=step_underline)
        step_label.place(x=step_label_pos_x,
                   y=step_label_pos_y_list[step_num])
        return step_label

    def _edit_help(step_num):
        disable_buttons(build_conf_buttons_list)
        info_title = (f"{cm_gg.STEP_LABELS_LIST[step_num].split(' - ')[0]}"
                      " - Description")
        info_text = cm_gg.STEP_HELPS_LIST[step_num]
        messagebox.showinfo(info_title, info_text)
        enable_buttons(build_conf_buttons_list)
    
    def _set_step_help_button(self, step_num):
        help_label_font = tkFont.Font(family=bm_gg.FONT_NAME,
                                  size=eff_help_font_size)
        help_button = tk.Button(self,
                                text=cm_gg.HELP_BUTTON,
                                font=help_label_font,
                                command=partial(_edit_help, step_num))
        step_label = step_label_widget[step_num]
        step_help_dx = help_dx - step_label.winfo_reqwidth()
        place_after(step_label, help_button,
                    dx=step_help_dx, dy=help_dy)

    def _set_step_launch_button(self, step_num, step_start_funct):
        step_launch_font = tkFont.Font(family=bm_gg.FONT_NAME,
                                       size=eff_launch_font_size)
        step_launch_button = tk.Button(self,
                                       text=cm_gg.STEP_LAUNCHS_LIST[step_num],
                                       font=step_launch_font,
                                       command=step_start_funct)
        bm_gg.GUI_BUTTONS.append(step_launch_button)

        place_bellow(step_label_widget[step_num],
                     step_launch_button,
                     dy=step_button_dy / 2)
        return step_launch_button

    def _update_progress(value):
        progress_var.set(value)
        progress_bar.update_idletasks()
        if value>=100:
            enable_buttons(build_conf_buttons_list)

    # ********************* Function start

    # Setting useful local variables for positions modification
    # numbers are reference values in mm for reference screen
    eff_step_font_size = font_size(bm_gg.REF_ETAPE_FONT_SIZE+2, master.width_sf_min)
    eff_launch_font_size = font_size(bm_gg.REF_ETAPE_FONT_SIZE-1, master.width_sf_min)
    eff_year_label_font_size = font_size(bm_gg.REF_ETAPE_FONT_SIZE+3, master.width_sf_min)
    eff_year_button_font_size = font_size(bm_gg.REF_ETAPE_FONT_SIZE, master.width_sf_min)
    eff_help_font_size = font_size(bm_gg.REF_ETAPE_FONT_SIZE-2, master.width_sf_min)
    progress_bar_length_px = mm_to_px(100 * master.width_sf_mm, bm_gg.PPI)
    progress_bar_dx = 40
    step_label_pos_x = mm_to_px(bm_gg.REF_ETAPE_POS_X_MM * master.width_sf_mm,
                                bm_gg.PPI)
    step_label_pos_y_list = [mm_to_px( y * master.height_sf_mm, bm_gg.PPI)
                             for y in cm_gg.STEP_POS_Y_MM_REF_LIST]
    step_button_dx = mm_to_px(bm_gg.REF_ETAPE_BUT_DX_MM * master.width_sf_mm,
                              bm_gg.PPI)
    step_button_dy = mm_to_px(bm_gg.REF_ETAPE_BUT_DY_MM * master.height_sf_mm,
                              bm_gg.PPI)
    year_button_x_pos = mm_to_px(cm_gg.REF_YEAR_BUT_POS_X_MM * master.width_sf_mm,
                                 bm_gg.PPI)
    year_button_y_pos = mm_to_px(cm_gg.REF_YEAR_BUT_POS_Y_MM * master.height_sf_mm,
                                 bm_gg.PPI) + step_button_dy 
    dy_year = -3
    help_dx = mm_to_px(cm_gg.REF_HELP_BUT_POS_X_MM * master.width_sf_mm, bm_gg.PPI)
    help_dy = mm_to_px(cm_gg.REF_HELP_BUT_POS_Y_MM * master.width_sf_mm, bm_gg.PPI)

    # Setting useful paths independent from corpus year
    wf_root_path = wf_path.parent

    # Getting institute parameters
    org_tup = set_org_params(institute, wf_root_path)
    
    # initializing parameters
    empl_update_status = False
    hal_all_empl_dict = {}

    # Creating and setting widgets for page title and exit button
    page_label_alias = cm_gg.PAGES_LABELS[page_name]
    set_page_title(self, master, page_label_alias, institute)
    set_exit_button(self, master)

    # Initializing progress bar widget
    progress_var = tk.IntVar()  # Variable to keep track of the progress bar value
    progress_bar = ttk.Progressbar(self,
                                   orient="horizontal",
                                   length=progress_bar_length_px,
                                   mode="determinate",
                                   variable=progress_var)

    # Setting step-label widgets parameters
    step_label_font = tkFont.Font(family=bm_gg.FONT_NAME,
                                   size=eff_step_font_size,
                                   weight='bold')
    step_label_format = 'left'
    step_underline = -1
    steps_number = cm_gg.STEPS_NB
    step_label_widget = [_set_step_label(self, step_num) for step_num in range(steps_number)]


    # *********************** STEP 0 : Mise en conformité des données des effectifs
    def _launch_update_hal_employees_data(progress_callback):
        """Command of the 'empl_button' button.
        
        """
        # Updating employees file
        return_tup = _launch_update_hal_employees_try(wf_root_path, progress_callback)
        empl_update_status, hal_all_empl_dict = return_tup
        progress_bar.place_forget()
    
    def _start_launch_update_hal_employees_data():
        disable_buttons(build_conf_buttons_list)
        place_after(empl_button,
                    progress_bar, dx=progress_bar_dx, dy=0)
        progress_var.set(0)
        threading.Thread(target=_launch_update_hal_employees_data, args=(_update_progress,)).start()

    # Définition du bouton 'empl_button' et du bouton 'description'
    step_num = 0
    help_button = _set_step_help_button (self, step_num)
    empl_button = _set_step_launch_button(self, step_num, _start_launch_update_hal_employees_data)

 
    # *********************** Création du choix de l'année pour les traitements
    # Choix de l'année
    default_year = master.years_list[-1]
    variable_years = tk.StringVar(self)
    variable_years.set(default_year)

    # Création du bouton de sélection de l'année dans une liste déroulante    
    self.font_OptionButton_years = tkFont.Font(family=bm_gg.FONT_NAME,
                                               size=eff_year_button_font_size )
    self.OptionButton_years = tk.OptionMenu(self,
                                            variable_years,
                                            *master.years_list)
    self.OptionButton_years.config(font=self.font_OptionButton_years)
    bm_gg.GUI_BUTTONS.append(self.OptionButton_years)

    # Création du label de choix de l'année
    self.font_Label_years = tkFont.Font(family=bm_gg.FONT_NAME,
                                        size=eff_year_label_font_size,
                                        weight='bold')
    self.Label_years = tk.Label(self,
                                text=bm_gg.TEXT_YEAR_PI,
                                font=self.font_Label_years)
    self.Label_years.place(x=year_button_x_pos, y=year_button_y_pos)

    place_after(self.Label_years, self.OptionButton_years, dy=dy_year)


    # *********************** step 1 : Extraction des contributions à conférence de l'Institut
    def _launch_set_hal_to_conf(progress_callback):
        """Command of the 'merge_button' button.        
        """
        # Getting year selection
        year_select = variable_years.get()

        # Trying launch of recursive search for authors in employees file
        _launch_set_hal_to_conf_try(institute, wf_path,
                                    year_select, progress_callback)
        progress_bar.place_forget()

    def _start_launch_set_hal_to_conf():
        disable_buttons(build_conf_buttons_list)
        place_after(extract_button,
                    progress_bar, dx=progress_bar_dx, dy=0)
        progress_var.set(0)
        threading.Thread(target=_launch_set_hal_to_conf, args=(_update_progress,)).start()

    ### Définition du bouton 'extract_button'
    step_num = 1
    help_button = _set_step_help_button (self, step_num)
    extract_button = _set_step_launch_button(self, step_num, _start_launch_set_hal_to_conf)


    # *********************** step 3 : Croisement auteurs-effectifs
    def _launch_recursive_year_search(progress_callback):
        """Command of the 'merge_button' button.
        """
        # Getting year selection
        year_select = variable_years.get()

        # Trying launch of recursive search for authors in employees file
        _launch_recursive_year_search_try(institute, wf_root_path, wf_path,
                                          year_select,
                                          empl_update_status,
                                          hal_all_empl_dict,
                                          progress_callback)
        progress_bar.place_forget()

    def _start_launch_recursive_year_search():
        disable_buttons(build_conf_buttons_list)
        place_after(merge_button,
                    progress_bar, dx=progress_bar_dx, dy=0)
        progress_var.set(0)
        threading.Thread(target=_launch_recursive_year_search, args=(_update_progress,)).start()

    ### Définition du bouton 'merge_button'
    step_num = 2
    help_button = _set_step_help_button (self, step_num)
    merge_button = _set_step_launch_button(self, step_num, _start_launch_recursive_year_search)


    # ****************** step 4 : Liste consolidée des contributions à conférence
    def _launch_conf_list_conso(progress_callback):
        """Command of the 'conso_button' button.
        """
        # Renewing year selection and years
        year_select = variable_years.get()

        # Trying launch creation of consolidated publications lists
        _launch_conf_list_conso_try(institute, org_tup, wf_path,
                                    year_select, progress_callback)
        progress_bar.place_forget()


    def _start_launch_conf_list_conso():
        disable_buttons(build_conf_buttons_list)
        place_after(conso_button,
                    progress_bar, dx=progress_bar_dx, dy=0)
        progress_var.set(0)
        threading.Thread(target=_launch_conf_list_conso, args=(_update_progress,)).start()

    ### Définition du bouton 'conso_button'
    step_num = 3
    help_button = _set_step_help_button (self, step_num)
    conso_button = _set_step_launch_button(self, step_num, _start_launch_conf_list_conso)

    # Setting buttons list for status change
    build_conf_buttons_list = [empl_button,
                               self.OptionButton_years,
                               extract_button,
                               merge_button,
                               conso_button]
