""" The `main_page` module sets the `AppMain` class, its attributes and related secondary classes.
"""

__all__ = ['AppMain']

# Standard library imports
import os
import threading
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from tkinter import font as tkFont
from functools import partial
from pathlib import Path

# 3rd party imports
import bmfuncts.pub_globals as bm_pg
import bmgui.gui_globals as bm_gg
from bmgui.gui_utils import enable_buttons
from bmgui.gui_utils import font_size
from bmgui.gui_utils import general_properties
from bmgui.gui_utils import last_available_years
from bmgui.gui_utils import mm_to_px
from bmgui.gui_utils import place_after
from bmgui.gui_utils import show_frame
from bmgui.gui_utils import str_size_mm
from screeninfo import get_monitors

# Local imports# Local imports
import cmfuncts.conf_globals as cm_cg
import cmgui.cm_gui_globals as cm_gg
import cmfuncts.institute_globals as cm_ig
from cmfuncts.useful_functs import create_cm_archi
from cmgui.build_conf_page import build_conf_list


class AppMain(tk.Tk):
    """Main class of the ConfMeter application.

    Traces changes in institute selection to update page parameters. 
    'wf' stands for working folder.
    """
    # ======================== Class init - start =======================
    def __init__(self):

        # Internal functions - start
        def _display_path(inst_wf):
            """Shortening wf path for easy display"""
            p = Path(inst_wf)
            if len(p.parts)<=4:
                p_disp = p
            else:
                part_start = p.parts[0:2]
                part_end = p.parts[-3:]
                p_disp = ('/'.join(part_start)) / Path("...") / ('/'.join(part_end))
            return p_disp


        def _get_file(institute_select):
            # Getting new working directory
            dialog_title = "Choisir un nouveau dossier de travail"
            wf_str = filedialog.askdirectory(title=dialog_title)
            if wf_str=='':
                warning_title = "!!! Attention !!!"
                warning_text = "Chemin non renseigné."
                messagebox.showwarning(warning_title, warning_text)

            # Updating wf values using new working directory
            _set_wf_widget_param(institute_select, wf_str)            
            _update_corpi(wf_str)
            wf_path = Path(wf_str)
            SetLaunchButton(self, institute_select, wf_path, datatype_alias)


        def _set_wf_widget_param(institute_select, inst_wf):
            # Setting wf widgets parameters
            wf_font = tkFont.Font(family=bm_gg.FONT_NAME,
                                   size=eff_wf_font_size,
                                   weight='bold')
            wf_label = tk.Label(self,
                                 text=bm_gg.WF_TXT,
                                 font=wf_font,)
            wf_val = tk.StringVar(self)
            wf_val2 = tk.StringVar(self)
            wf_entree2 = tk.Entry(self, textvariable=wf_val2, width=eff_wf_width)
            wf_button_font = tkFont.Font(family=bm_gg.FONT_NAME,
                                          size=eff_buttons_font_size)
            wf_button = tk.Button(self,
                                   text=bm_gg.WF_CHANGE_TXT,
                                   font=wf_button_font,
                                   command=lambda: _get_file(institute_select))
            # Placing wf widgets
            wf_label.place(x=eff_wf_pos_x_px,
                            y=eff_wf_pos_y_px,)

            text_width_mm, _ = str_size_mm(bm_gg.WF_TXT, wf_font, bm_gg.PPI)
            eff_path_pos_x_px = mm_to_px(text_width_mm + space_mm_alias, bm_gg.PPI)
            wf_entree2.place(x=eff_path_pos_x_px,
                              y=eff_wf_pos_y_px,)

            wf_button.place(x=eff_path_pos_x_px,
                             y=eff_wf_pos_y_px + eff_button_dy_px,)
            wf_val.set(inst_wf)
            wf_val2.set((_display_path(inst_wf)))


        def _try_wf_access(wf_path):
            """Returns status of the default working folder as boolean: True, if exists 
            and access is authorized to the user; False, otherwise."""

            wf_access_status = False
            if os.access(wf_path, os.F_OK | os.R_OK | os.W_OK):
                wf_access_status = True
            else:
                warning_title = "!!! ATTENTION : Accés au dossier impossible !!!"
                warning_text = (f"Accès non autorisé ou absence du dossier \n   {wf_path}."
                                "\n\nChoisissez un autre dossier de travail.")
                messagebox.showwarning(warning_title, warning_text)
            return wf_access_status

        def _create_corpus(inst_wf):
            """Creates a new corpus folder in the working folder through `create_cm_archi`
            function imported from `cmfuncts.useful_functs` module.             
            Then, updates 'corpi' widget value with new list of available corpuses."""

            corpi_val = _set_corpi_widgets_param(inst_wf)
            wf_path = Path(inst_wf)
            wf_access_status = _try_wf_access(wf_path)
            if wf_access_status:
                # Setting new corpus year folder name
                corpuses_list = last_available_years(wf_path, corpuses_nb_alias)
                last_corpus_year = corpuses_list[-1]
                new_corpus_year_folder = str(int(last_corpus_year) + 1)

                # Creating required folders for new corpus year
                message = create_cm_archi(wf_path, new_corpus_year_folder, verbose=False)
                print("\n",message)

                # Getting updated corpuses list
                corpuses_list = last_available_years(wf_path, corpuses_nb_alias)

                # Setting corpi_val value to corpuses list
                corpi_val_to_set = str(corpuses_list)
                corpi_val.set(corpi_val_to_set)

                # Dispaying info
                info_title = "- Information -"
                info_text = (f"L'architecture du dossier pour l'année {new_corpus_year_folder} "
                             "a été créée dans le dossier de travail.")
                messagebox.showinfo(info_title, info_text)
            else:
                corpi_val.set("")

        def _set_corpi_widgets_param(inst_wf):
            """Sets 'corpi' widgets parameters and values accordingly 
            to the working folder and returns tkinter 'corpi' parameter 
            that is used to set for display the available corpuses list."""

            # Setting corpuses widgets parameters
            corpi_font = tkFont.Font(family=bm_gg.FONT_NAME,
                                     size=eff_corpi_font_size,
                                     weight='bold')
            corpi_val = tk.StringVar(self)
            corpi_entry = tk.Entry(self, textvariable=corpi_val, width=eff_list_width)
            corpi_button_font = tkFont.Font(family=bm_gg.FONT_NAME,
                                            size=eff_buttons_font_size)
            corpi_label = tk.Label(self,
                                   text=bm_gg.CORPUSES_TXT,
                                   font=corpi_font,)
            corpi_button = tk.Button(self,
                                     text=bm_gg.CREATE_CORPUS_BUTTON_TXT,
                                     font=corpi_button_font,
                                     command=lambda: _create_corpus(inst_wf))

            # Placing corpuses widgets
            corpi_label.place(x=eff_corpi_pos_x_px,
                              y=eff_corpi_pos_y_px,)

            text_width_mm, _ = str_size_mm(bm_gg.CORPUSES_TXT, corpi_font, bm_gg.PPI)
            eff_list_pos_x_px = mm_to_px(text_width_mm + space_mm_alias, bm_gg.PPI)
            corpi_entry.place(x=eff_list_pos_x_px,
                              y=eff_corpi_pos_y_px,)

            corpi_button.place(x=eff_list_pos_x_px,
                               y=eff_corpi_pos_y_px + eff_button_dy_px,)
            return corpi_val

        def _update_corpi(inst_wf):
            """Updates tkinter 'corpi' parameter with the available corpuses list 
            accordingly to working folder."""

            corpi_val = _set_corpi_widgets_param(inst_wf)
            corpi_val_to_set = ""
            wf_path = Path(inst_wf)
            wf_access_status = _try_wf_access(wf_path)
            if wf_access_status:
                # Getting updated corpuses list
                corpuses_list = last_available_years(wf_path, corpuses_nb_alias)

                # Setting corpi_val value to corpuses list
                corpi_val_to_set = str(corpuses_list)
            corpi_val.set(corpi_val_to_set)
        
        def _update_cm_page(*args, institute_widget=None):
            """Gets the selected Institute widgets parameters."""

            _ = args
            institute_select = institute_widget.get()

            # Managing working folder
            inst_default_wf = cm_ig.WORKING_FOLDERS_DICT[institute_select] + "-" + cm_gg.VERSION
            _set_wf_widget_param(institute_select, inst_default_wf)

            # Managing corpus list
            corpi_val = _set_corpi_widgets_param(inst_default_wf)

            # Setting and displaying corpuses list initial values
            corpi_val_to_set = ""
            default_wf_path = Path(inst_default_wf)
            info_title = "- Information -"
            info_text = ("Le test de l'accès au dossier de travail défini "
                         "par défaut peut prendre un peu de temps."
                         "\n\nMerci de patienter.")
            messagebox.showinfo(info_title, info_text)
            wf_access_status = _try_wf_access(default_wf_path)
            if wf_access_status:
                info_title = "- Information -"
                info_text = ("L'accès au dossier de travail défini "
                             "par défaut est autorisé mais vous pouvez "
                             "en choisir un autre.")
                messagebox.showinfo(info_title, info_text)
                init_corpuses_list = last_available_years(default_wf_path, corpuses_nb_alias)
                corpi_val_to_set = str(init_corpuses_list)
            corpi_val.set(corpi_val_to_set)

            # Managing analysis launch button
            SetLaunchButton(self, institute_select, default_wf_path, datatype_alias)

        def _except_hook(args):
            messagebox.showerror("Error", args)
            messagebox.showerror("Exception", traceback.format_exc())
            enable_buttons(bm_gg.GUI_BUTTONS)
        # ===================== Internal functions - end ====================

        # ============================== Main ===============================

        # Setting the link between "self" and "tk.Tk"
        tk.Tk.__init__(self)

        # Setting class attributes and methods
        _ = get_monitors() # Mandatory
        self.attributes("-topmost", True)
        self.after_idle(self.attributes,'-topmost', False)
        icon_path = Path(__file__).parent.parent / Path('cmfuncts') / Path(cm_cg.CONFIG_FOLDER)
        icon_path = icon_path / Path('CM-logo.ico')
        self.iconbitmap(icon_path)

        # Initializing AppMain attributes set after working folder definition
        AppMain.years_list = []
        AppMain.list_corpus_year = []

        # Setting pages classes and pages list
        AppMain.pages = (BuildConfPage,
                        )
        AppMain.pages_ordered_list = [x.__name__ for x in AppMain.pages][::-1]

        # Getting useful screen sizes and scale factors depending on displays properties
        sizes_tuple = general_properties(self)
        AppMain.win_width_px = sizes_tuple[0]
        AppMain.win_height_px = sizes_tuple[1]
        AppMain.width_sf_px = sizes_tuple[2]
        AppMain.height_sf_px = sizes_tuple[3]
        AppMain.width_sf_mm = sizes_tuple[4]
        AppMain.height_sf_mm = sizes_tuple[5]
        AppMain.width_sf_min = min(AppMain.width_sf_mm, AppMain.width_sf_px)

        # Setting common parameters for widgets
        corpuses_nb_alias = bm_gg.CORPUSES_NUMBER
        datatype_alias = cm_gg.HAL_DATATYPE
        space_mm_alias = bm_gg.ADD_SPACE_MM
        eff_buttons_font_size = font_size(bm_gg.REF_BUTTON_FONT_SIZE, AppMain.width_sf_min)

        # Setting widgets parameters for institute selection
        eff_select_font_size = font_size(bm_gg.REF_SUB_TITLE_FONT_SIZE, AppMain.width_sf_min)
        inst_button_x_pos = mm_to_px(bm_gg.REF_INST_POS_X_MM * AppMain.width_sf_mm, bm_gg.PPI)
        inst_button_y_pos = mm_to_px(bm_gg.REF_INST_POS_Y_MM * AppMain.height_sf_mm, bm_gg.PPI)
        dy_inst = -10

        # Setting widgets parameters for Working-folder selection
        eff_wf_width = int(bm_gg.REF_ENTRY_NB_CHAR * AppMain.width_sf_min)
        eff_wf_font_size = font_size(bm_gg.REF_SUB_TITLE_FONT_SIZE, AppMain.width_sf_min)
        eff_wf_pos_x_px = mm_to_px(bm_gg.REF_WF_POS_X_MM * AppMain.height_sf_mm, bm_gg.PPI)
        eff_wf_pos_y_px = mm_to_px(bm_gg.REF_WF_POS_Y_MM * AppMain.height_sf_mm, bm_gg.PPI)
        eff_button_dy_px = mm_to_px(bm_gg.REF_BUTTON_DY_MM * AppMain.height_sf_mm, bm_gg.PPI)

        # Setting widgets parameters for corpuses display
        eff_list_width = int(bm_gg.REF_ENTRY_NB_CHAR * AppMain.width_sf_min)
        eff_corpi_font_size = font_size(bm_gg.REF_SUB_TITLE_FONT_SIZE, AppMain.width_sf_min)
        eff_corpi_pos_x_px = mm_to_px(bm_gg.REF_CORPI_POS_X_MM * AppMain.height_sf_mm, bm_gg.PPI)
        eff_corpi_pos_y_px = mm_to_px(bm_gg.REF_CORPI_POS_Y_MM * AppMain.height_sf_mm, bm_gg.PPI)

        # Setting and placing widgets for title and copyright
        SetMasterTitle(self)
        SetAuthorCopyright(self)

        # Setting default values for Institute selection
        institutes_list = cm_ig.INSTITUTES_LIST
        default_institute = "   "
        institute_val = tk.StringVar(self)
        institute_val.set(default_institute)

        # Creating widgets for Institute selection
        self.inst_optionbutton_font = tkFont.Font(family=bm_gg.FONT_NAME,
                                                  size=eff_buttons_font_size)
        self.inst_optionbutton = tk.OptionMenu(self,
                                               institute_val,
                                               *institutes_list)
        self.inst_optionbutton.config(font = self.inst_optionbutton_font)
        self.inst_label_font = tkFont.Font(family=bm_gg.FONT_NAME,
                                           size=eff_select_font_size,
                                           weight='bold')
        self.inst_label = tk.Label(self,
                                   text=bm_gg.INSTITUTE_TXT,
                                   font=self.inst_label_font)

        # Placing widgets for Institute selection
        self.inst_label.place(x = inst_button_x_pos, y = inst_button_y_pos)
        place_after(self.inst_label, self.inst_optionbutton, dy=dy_inst)

        # Tracing Institute selection
        institute_val.trace('w', partial(_update_cm_page, institute_widget=institute_val))

        # Handling exception
        threading.excepthook = _except_hook       


class SetMasterTitle():
    """Displays title in main window."""

    def __init__(self, master):

        # Setting widget parameters for page title
        eff_page_title_font_size = font_size(bm_gg.REF_PAGE_TITLE_FONT_SIZE, master.width_sf_min)
        eff_page_title_pos_y_px  = mm_to_px(bm_gg.REF_PAGE_TITLE_POS_Y_MM * master.height_sf_mm,
                                            bm_gg.PPI)
        mid_page_pos_x_px = master.win_width_px * 0.5

        # Creating widget for page title
        page_title = tk.Label(master,
                              text=cm_gg.MAIN_PAGE_TITLE,
                              font=(bm_gg.FONT_NAME, eff_page_title_font_size),
                              justify="center")

        # Placing widget for page title
        page_title.place(x=mid_page_pos_x_px,
                         y=eff_page_title_pos_y_px,
                         anchor="center")

class SetAuthorCopyright():
    """Displays authors and copyright in main window."""

    def __init__(self, master):

        # Setting widgets parameters for copyright
        eff_copyright_font_size = font_size(bm_gg.REF_COPYRIGHT_FONT_SIZE, master.width_sf_min)
        eff_version_font_size = font_size(bm_gg.REF_VERSION_FONT_SIZE, master.width_sf_min)
        eff_copyright_x_px = mm_to_px(bm_gg.REF_COPYRIGHT_X_MM * master.width_sf_mm, bm_gg.PPI)
        eff_copyright_y_px = mm_to_px(bm_gg.REF_COPYRIGHT_Y_MM * master.height_sf_mm, bm_gg.PPI)
        eff_version_x_px = mm_to_px(bm_gg.REF_VERSION_X_MM * master.width_sf_mm, bm_gg.PPI)
        eff_version_y_px = mm_to_px(bm_gg.REF_COPYRIGHT_Y_MM * master.height_sf_mm, bm_gg.PPI)

        # Creating widgets for copyright
        auteurs_font_label = tkFont.Font(family=bm_gg.FONT_NAME,
                                         size=eff_copyright_font_size,)
        auteurs_label = tk.Label(master,
                                 text=cm_gg.APP_COPYRIGHT,
                                 font=auteurs_font_label,
                                 justify="left")
        version_font_label = tkFont.Font(family=bm_gg.FONT_NAME,
                                         size=eff_version_font_size,
                                         weight='bold')
        version_label = tk.Label(master,
                                 text=cm_gg.APP_VERSION,
                                 font=version_font_label,
                                 justify="right")

        # Placing widgets for copyright
        auteurs_label.place(x=eff_copyright_x_px,
                            y=eff_copyright_y_px,
                            anchor="sw")
        version_label.place(x=eff_version_x_px,
                            y=eff_version_y_px,
                            anchor="sw")

class SetLaunchButton(tk.Tk):
    """Displays corpuses analysis launch button in main window."""

    def __init__(self, master, institute, wf_path, datatype):

        # Setting font size for launch button
        eff_launch_font_size = font_size(bm_gg.REF_LAUNCH_FONT_SIZE, master.width_sf_min)

        # Setting x and y position in pixels for launch button
        launch_but_pos_x_px = master.win_width_px * 0.5
        launch_but_pos_y_px = master.win_height_px * 0.8

        # Setting launch button
        launch_font = tkFont.Font(family=bm_gg.FONT_NAME,
                                  size=eff_launch_font_size,
                                  weight='bold')
        launch_button = tk.Button(master,
                                  text=bm_gg.LAUNCH_BUTTON_TXT,
                                  font=launch_font,
                                  command=lambda: self._generate_pages(master,
                                                                       institute,
                                                                       wf_path,
                                                                       datatype))
        # Placing launch button
        launch_button.place(x=launch_but_pos_x_px,
                            y=launch_but_pos_y_px,
                            anchor="s")

    def _generate_pages(self, master, institute, wf_path, datatype):
        """Generates pages after working folder setting."""

        if wf_path=='':
            warning_title = "!!! Attention !!!"
            warning_text =  "Chemin non renseigné."
            warning_text += "\nL'application ne peut pas être lancée."
            warning_text += "\nVeuillez le définir."
            messagebox.showwarning(warning_title, warning_text)

        else:
            # Setting years list
            master.years_list = last_available_years(wf_path,
                                                     bm_gg.CORPUSES_NUMBER)

            if datatype:
                # Setting rawdata for datatype
                for database in bm_pg.BDD_LIST:
                    _ = set_rawdata(wf_path, datatype,
                                    master.years_list, database)

                # Setting existing corpuses status
                files_status = existing_corpuses(wf_path)
                master.list_corpus_year = files_status[0]
                master.list_wos_rawdata = files_status[1]
                master.list_wos_parsing = files_status[2]
                master.list_scopus_rawdata = files_status[3]
                master.list_scopus_parsing = files_status[4]
                master.list_dedup = files_status[5]

            # Creating two frames in the tk window
            pagebutton_frame = tk.Frame(master, bg='red',
                                        height=bm_gg.PAGEBUTTON_HEIGHT_PX)
            pagebutton_frame.pack(side="top", fill="both", expand=False)

            page_frame = tk.Frame(master)
            page_frame.pack(side="top", fill="both", expand=True)
            page_frame.grid_rowconfigure(0, weight=1)
            page_frame.grid_columnconfigure(0, weight=1)

            self.frames = {}
            for page in master.pages:
                page_name = page.__name__
                if datatype:
                    frame = page(master, pagebutton_frame, page_frame,
                                 institute, wf_path, datatype)
                else:
                    frame = page(master, pagebutton_frame, page_frame,
                                 institute, wf_path)
                self.frames[page_name] = frame

                # Putting all of the pages in the same location
                # The one visible is the one on the top of the stacking order
                frame.grid(row=0, column=0, sticky="nsew")
            master.frames = self.frames

class PageButton(tk.Frame):
    """Sets button of 'page_name' page."""

    def __init__(self, master, page_name, pagebutton_frame):

        # Setting page num
        label_text = cm_gg.PAGES_LABELS[page_name]
        page_num = master.pages_ordered_list.index(page_name)

        # Setting widgets parameters for page button
        eff_button_font_size = font_size(bm_gg.REF_BUTTON_FONT_SIZE, master.width_sf_min)

        # Creating widgets for page button
        button_font = tkFont.Font(family=bm_gg.FONT_NAME,
                                  size=eff_button_font_size)
        button = tk.Button(pagebutton_frame,
                           text=label_text,
                           font=button_font,
                           command=lambda: show_frame(master, page_name))

        # Placing widgets for page button
        button.grid(row=0, column=page_num)


class BuildConfPage(tk.Frame):
    """Sets corpuses-consolidation page widgets through `create_consolidate_corpus` function 
    imported from `bmgui.consolidate_corpus_page` module."""

    def __init__(self, master, pagebutton_frame, page_frame, institute, wf_path):
        super().__init__(page_frame)
        self.controller = master

        # Setting page name
        page_name = self.__class__.__name__

        # Creating and setting widgets for page button
        PageButton(master, page_name, pagebutton_frame)

        # Creating and setting widgets for page frame
        build_conf_list(self, master, page_name, institute, wf_path)
