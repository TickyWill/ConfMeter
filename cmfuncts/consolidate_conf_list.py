"""Module of functions for the consolidation of the list of Institute contributions 
to conferences by adding useful informations such as authors :

- effective affiliation of the authors to the Institute;
- attributing department affiliation to the Institute authors.

"""

__all__ = ['build_final_conf_list',
          ]

# Standard Library imports
from pathlib import Path

# 3rd party imports
import pandas as pd
from bmfuncts.useful_functs import set_year_pub_id

# Local imports
import cmfuncts.conf_globals as cm_cg
import cmfuncts.employees_globals as cm_eg
from cmfuncts.cols_rename import build_hal_col_conversion_dic
from cmfuncts.hal_hash_id import create_hal_hash_id
from cmfuncts.format_files import format_hal_page
from cmfuncts.merge_conf_employees import read_merged_data
from cmfuncts.merge_conf_employees import save_merged_data


def _add_hal_author_job_type(merged_df):
    """Adds a new column containing the job type for each author 
    of the conferences list with one row per author.

    The job type is got from the employee information available 
    in 3 columns which names are given by 'category_col_alias', 
    'status_col_alias' and 'qualification_col_alias'. 
    The name of the new column is given by 'author_type_col_alias'.

    Args:
        merged_df (dataframe): The list of Institute contributions \
        to conferences with one row per Institute-affiliated author \
        merged with employees data.
    Returns:
        (dataframe): The updated data.
    """
    # internal functions:
    def _get_author_type(row):
        author_type = '-'
        for col_name, dic in author_types_dic.items():
            for key,values_list in dic.items():
                values_status = [True for value in values_list if value in row[col_name]]
                if any(values_status):
                    author_type = key
        return author_type

    # Setting useful aliases
    category_col_alias = cm_eg.EMPLOYEES_USEFUL_COLS['category']
    status_col_alias = cm_eg.EMPLOYEES_USEFUL_COLS['status']
    qualification_col_alias = cm_eg.EMPLOYEES_USEFUL_COLS['qualification']
    author_type_col_alias = cm_cg.CONF_ADD_COLS['author_type']

    author_types_dic = {category_col_alias      : cm_eg.CATEGORIES_DIC,
                        status_col_alias        : cm_eg.STATUS_DIC,
                        qualification_col_alias : cm_eg.QUALIFICATION_DIC}

    merged_df[author_type_col_alias] = merged_df.apply(_get_author_type, axis=1)
    
    return merged_df


def _set_hal_full_ref(title, first_author, conf_name, conf_year, conf_country, pub_year, doi):
    """Builds the full reference of a publication.

    Args:
        title (str): Title of the publication.
        first_author (str): First author of the publication formated as 'NAME IJ' \
        with 'NAME' the lastname and 'IJ' the initials of the firstname of the author.
        journal_name (str): Name of the journal where the publication is published.
        pub_year (str): Publication year defined by 4 digits.
        doi (str): Digital identification of the publication.
    Returns:
        (str): Full reference of the publication.
    """
    full_ref  = f'{title}, '                     # add the reference's title
    full_ref += f'{first_author}. et al., '      # add the reference's first author
    full_ref += f'{conf_name}, '                 # add the reference's conference name
    full_ref += f'{conf_country}-{conf_year}, '  # add the reference's conference country and year
    full_ref += f'{pub_year}'                    # add the reference's publication year
    full_ref += f'{doi}'                         # add the reference's DOI if available
    return full_ref


def _add_conf_full_ref(merged_df):
    """Adds a new column containing the full reference of each conference
    of the data with one row per author.

    The full reference is built by concatenating the folowing items: 
    title, first author, conference name, conference year, conference country, 
    publication year and DOI through the `_set_hal_full_ref` internal function.  
    These items are got from the columns which names are given by 
    'title_alias', 'first_author_alias', 'conf_name_alias', 'conf_year_alias', 
    'country_alias', 'pub_year_alias' and 'pub_doi_alias', respectively. 
    The name of the new column is given by 'conf_full_ref_alias'.

    Args:
        merged_df (dataframe): The list of Institute contributions to conferences \
        with one row per Institute-affiliated author merged with employees data.
    Returns:
        (dataframe): The updated data.
    """
    # Setting useful aliases
    unknown_alias = cm_cg.INDISPONIBLE
    pub_id_alias = cm_cg.CONF_COLS['pub_id']                    # 'Pub_id'
    first_author_alias = cm_cg.CONF_COLS['first_author']        # "Premier auteur
    pub_year_alias = cm_cg.CONF_COLS['pub_year']                # "Année de publication"
    conf_year_alias = cm_cg.CONF_COLS['conf_year']              # "Année de conférence"
    conf_name_alias = cm_cg.CONF_COLS['conf_name']              # 'Conference'
    country_alias = cm_cg.CONF_COLS['country']                  # "Pays"
    doi_alias = cm_cg.CONF_COLS['doi']                          # "DOI"
    title_alias = cm_cg.CONF_COLS['title']                      # "Titres"
    conf_full_ref_alias = cm_cg.CONF_ADD_COLS['full_ref']       # "Référence bibliographique complète"

    # Splitting the frame into subframes with same Pub_id
    conf_plus_full_ref_df = pd.DataFrame()
    for _, pub_id_df in merged_df.groupby(pub_id_alias):
        # Select the first row and build the full reference
        pub_id_first_row = pub_id_df.iloc[0]
        title        = str(pub_id_first_row[title_alias])
        first_author = str(pub_id_first_row[first_author_alias])
        conf_name    = str(pub_id_first_row[conf_name_alias])
        conf_year    = str(pub_id_first_row[conf_year_alias])
        conf_country = str(pub_id_first_row[country_alias])
        pub_year     = str(pub_id_first_row[pub_year_alias])
        doi = ""
        if pub_id_first_row[doi_alias]!=unknown_alias:
            doi = ", " + str(pub_id_first_row[doi_alias])
        pub_id_df[conf_full_ref_alias] = _set_hal_full_ref(title, first_author, conf_name,
                                                          conf_year, conf_country, pub_year, doi)
        conf_plus_full_ref_df = pd.concat([conf_plus_full_ref_df, pub_id_df])

    return conf_plus_full_ref_df


def _add_hal_authors_name_list(org_tup, merged_df):
    """Adds to the list of Institute contributions to conferences with 
    one row per Institute-affiliated author merged with employees data, 
    a column with the institute co-authors list with attributes of each author.

    The column contains at each row a string built as follows:

        - "NAME1, Firstame1 (matricule,job type,department affiliation, \
        service affiliation, laboratoire affiliation);
        - NAME2, Firstame2 (matricule,job type,department affiliation, \
        service affiliation, laboratoire affiliation);
        - ...".

    Args:
        org_tup (tup): Contains Institute parameters.
        merged_df (dataframe): The list of Institute contributions \
        to conferences with one row per Institute-affiliated author \
        merged with employees data.
    Returns:
        (dataframe): The updated data.
    """
    # Internal functions
    def _get_dpt_key(dpt_raw):
        return_key = None
        for key, values in dpt_label_dict.items():
            if dpt_raw in values:
                return_key = key
        return return_key

    # Setting institute parameters
    dpt_label_dict = org_tup[1]

    # Setting useful aliases
    unknown_alias = cm_cg.INDISPONIBLE
    pub_id_alias = cm_cg.CONF_COLS['pub_id']                    # 'Pub_id'
    auth_idx_alias = cm_cg.CONF_COLS['author_idx']              # 'Idx_author'
    author_type_alias = cm_cg.CONF_ADD_COLS['author_type']      # "Type de l'auteur"    
    inst_auth_list_alias = cm_cg.CONF_ADD_COLS['inst_authors']  # "Liste ordonnée des auteurs de l'institut"
    nom_alias = cm_eg.EMPLOYEES_USEFUL_COLS['name']             # "Nom"
    prenom_alias = cm_eg.EMPLOYEES_USEFUL_COLS['first_name']    # "Prénom"
    matricule_alias = cm_eg.EMPLOYEES_USEFUL_COLS['matricule']  # "Matricule"
    dept_alias = cm_eg.EMPLOYEES_USEFUL_COLS['dpt']             # "Dpt/DOB (lib court)"
    serv_alias = cm_eg.EMPLOYEES_USEFUL_COLS['serv']            # "Service (lib court)"
    lab_alias = cm_eg.EMPLOYEES_USEFUL_COLS['lab']              # "Laboratoire (lib court)"
    
    # Setting intermediate col name
    names_temp_col = "Nom, Prénom"

    # Reading the excel file
    init_df = merged_df.copy()

    # Adding the column 'names_temp_col' that will be used to create the authors fullname list
    init_df[prenom_alias] = init_df[prenom_alias].apply(lambda x: x.capitalize())
    init_df[names_temp_col] = init_df[nom_alias] + ', ' + init_df[prenom_alias]

    out_df = pd.DataFrame()
    for _, pub_id_df in init_df.groupby(pub_id_alias):
        raw_depts_list = pub_id_df[dept_alias].to_list()
        depts_list = [_get_dpt_key(x) for x in raw_depts_list]
        for dept in dpt_label_dict.keys():
            pub_id_df[dept] = 0
            if dept in depts_list:
                pub_id_df[dept] = 1
        
        authors_tup_list = sorted(list(set(zip(pub_id_df[auth_idx_alias],
                                               pub_id_df[names_temp_col],
                                               pub_id_df[matricule_alias],
                                               pub_id_df[author_type_alias],
                                               pub_id_df[dept_alias],
                                               pub_id_df[serv_alias],
                                               pub_id_df[lab_alias]))))

        authors_str_list = [(f'{x[1]} ({x[2]},'
                             f'{x[3]},{_get_dpt_key(x[4])},{x[5]},{x[6]})')
                            for x in authors_tup_list]
        authors_full_str = "; ".join(authors_str_list)
        pub_id_df[inst_auth_list_alias] = authors_full_str

        out_df = pd.concat([out_df, pub_id_df])
    return out_df


def _build_useful_names(base_name, key_name, corpus_year):
    """Builds the file name and the sheet name for saving data of a corpus year.

    ex:
       base_name = "Liste"   | 
                             |    file_name = "Liste 2019_Posters.xlsx"
       key_name = "Posters"  | => 
                             |    sheet_name = "Posters 2019"
       corpus_year = "2019"  |
    
    Args:
        base_name (str): The first part of the file name to build.
        key_name (str): The specific part of the file name and \
        of the sheet name to build.
        corpus_year (str): 4 digits year of the corpus.
    Returns:
        (tup): (the built file name, the built sheet name).
    """
    corpus_str = " " + corpus_year
    file_name = base_name + corpus_str + "_" + key_name +".xlsx"
    sheet_name = key_name +corpus_str
    return file_name, sheet_name


def set_results_paths(wf_path, corpus_year, key):
    """Sets the parameters of the files resulting from merge of data of 
    the contributions to conferences with the data of employees.

    Args:
        wf_path (path): The full path to the working folder.
        corpus_year (str): 4 digits year of the corpus.
    Returns:
        (tup): (The list composed of the full path (path) to the folder  \
        where are located the two files generated by the merge \
        and of the full paths (path) to these two files, \
        the list of the names (str) of these two files).
    """
    # Setting useful aliases
    results_folder_alias = cm_cg.CM_ARCHI['final_results_folder']
    base_name_alias = cm_cg.CM_ARCHI['conf_list_file_base']
    key_name_alias = cm_cg.CONF_NAMES_DIC[key]

    # Building file name
    key_file_name, key_sheet_name = _build_useful_names(base_name_alias,
                                                        key_name_alias,
                                                        corpus_year)

    # Setting useful paths
    year_cmf_path = wf_path / Path(corpus_year)
    results_folder_path = year_cmf_path / Path(results_folder_alias)
    key_df_path = results_folder_path / Path(key_file_name)

    # Setting return lists
    paths_list = [results_folder_path, key_df_path]
    names_list = [key_file_name, key_sheet_name]
    
    return paths_list, names_list


def _save_final_df(wf_path, corpus_year, key,
                   key_df, cols_rename_dict):
    """Saves the final list of Institute contributions to conferences.

    The data are saved as an openpyxl workbook formatted through 
    the `format_hal_page` imported from the`cmfuncts.format_files` 
    module.

    Args:
        wf_path (path): The full path to the working folder.
        corpus_year (str): 4 digits year of the corpus.
        conf_list_df (dataframe): The data of the Institute \
        contributions to conferences.
        cols_rename_dict (dict): The dict for using the renamed columns \
        of the data of the Institute contributions to conferences.
    """
    paths_list, names_list = set_results_paths(wf_path, corpus_year, key)
    _, key_df_path = paths_list
    _, key_sheet_name = names_list

    # Formating and saving data as workbook
    wb, ws = format_hal_page(key_df, cols_rename_dict)
    ws.title = key_sheet_name
    wb.save(key_df_path)


def _split_conf_list_by_doc_type(wf_path, corpus_year,
                                 full_conf_list_df, cols_rename_dict):
    """Splits the dataframe of the final list of contributions 
    to conferences into data corresponding to different documents types.

    This is done for the 'corpus_year' corpus. 
    These data are saved through the `_save_final_df` internal function.

    Args:
        wf_path (path): Full path to working folder.
        corpus_year (str): 4 digits year of the corpus.
        full_conf_list_df (dataframe): The data to be split
        cols_rename_dict (dict): The dict for using the renamed columns \
        of the data of the Institute contributions to conferences.
    Returns:
        (tup): (split ratio in % of the final list (int), 
        consolidated number (int) of the contributions to conferences).
    """
    # Setting useful column names
    pub_id_col = cols_rename_dict[cm_cg.CONF_COLS['pub_id']]
    doc_type_col = cols_rename_dict[cm_cg.CONF_COLS['doctype']]
    
    others_dg = full_conf_list_df.copy()
    conf_nb = len(full_conf_list_df)
    key_conf_nb = 0
    for key, doctype_list in cm_cg.CONF_TYPES_DIC.items():
        doctype_list = [x.upper() for x in doctype_list]
        key_dg = pd.DataFrame(columns=full_conf_list_df.columns)
        for doc_type, dg in full_conf_list_df.groupby(doc_type_col):
            if doc_type.upper() in doctype_list:
                key_dg = pd.concat([key_dg, dg])
                others_dg = others_dg.drop(dg.index)
        key_dg = key_dg.sort_values(by=[pub_id_col])
        key_conf_nb += len(key_dg)
        
        # saving key data
        _save_final_df(wf_path, corpus_year, key,
                       key_dg, cols_rename_dict)

    others_dg = others_dg.sort_values(by=[pub_id_col])
    
    # saving others data
    _save_final_df(wf_path, corpus_year, 'others',
                   others_dg, cols_rename_dict)

    split_ratio = 100
    if conf_nb!=0:
        split_ratio = round(key_conf_nb / conf_nb * 100)
    return split_ratio, conf_nb


def build_final_conf_list(wf_path, org_tup, corpus_year, merged_df=pd.DataFrame(),
                          verbose=False, progress_callback=None):
    """Builds the final list of Institute contributions to conferences.

    First, The list of contributions, with one row per Institute-affiliated 
    author, merged with employees data is added with:

    - The job type of each author through the `_add_hal_author_job_type` 
    internal function.
    - The full-reference of each contribution through the `_add_conf_full_ref` 
    internal function.
    - The list of Institute co-authors of each contribution through the 
    `_add_hal_authors_name_list` internal function.

    Then, a year conference-ID is set in place of the initial one. 
    After that, the useful columns for the final list are selected using 
    the keys of the dict 'cols_rename_dict' built through the 
    `build_hal_col_conversion_dic` function imported from the 
    `cmfuncts.cols_rename` module. 
    Then, the duplicate rows are dropped in the obtained data. 
    Finally, the final list of contributions to conferences is saved 
    through the `_save_final_conf_list` internal function.

    Args:
        wf_path (path): The full path to the working folder.
        corpus_year (str): 4 digits year of the corpus.
        org_tup (tup): Contains Institute parameters.
        merged_df (dataframe): Optional list of Institute contributions \
        to conferences with one row per Institute-affiliated author \
        merged with employees data (default=empty dataframe).
        verbose (bool): Status for intermediate data saving and \
        prints (default=False).
    Returns:
        (dataframe): The final list of Institute contributions \
        to conferences.
    """
    # Setting useful aliases
    pub_id_alias = cm_cg.CONF_COLS['pub_id']
    pub_year_alias = cm_cg.CONF_COLS['pub_year']
    shift_alias = cm_cg.PUB_ID_SHIFT
    
    # Setting the initial list of Institute contributions to conferences
    if merged_df.empty:
        merged_df = read_merged_data(wf_path, corpus_year)

    # Adding author job type
    merged_df = _add_hal_author_job_type(merged_df)
    if verbose:
        save_merged_data(wf_path, corpus_year, merged_df, step="Job_")
        print(("\nColumn with author job-type is added to the contributions "
               "list to conferences, with one row per Institute-affiliated "
               "author, merged with employees data."))

    # Adding full reference of each contribution to a conference
    merged_df = _add_conf_full_ref(merged_df)
    if verbose:
        save_merged_data(wf_path, corpus_year, merged_df, step="Fullref_")
        print(("\nColumn with contribution full-reference is added "
               "to the contributions list to conferences, with one row "
               "per Institute-affiliated author, merged with employees data."))

    # Adding list of Institute authors with attributes
    merged_df = _add_hal_authors_name_list(org_tup, merged_df)
    if verbose:
        save_merged_data(wf_path, corpus_year, merged_df, step="Authlist_")
        print(("\nColumn with the list of Institute co-authors is added "
               "to the list of contributions to conferences, with one row "
               "per Institute-affiliated author, merged with employees data."))

    # Setting year pub ID
    merged_df[pub_id_alias] = merged_df[pub_id_alias].apply(lambda x: str(int(x) + shift_alias))
    year = int(merged_df[pub_year_alias].iloc[0])
    set_year_pub_id(merged_df, year, pub_id_alias)
    
    # Adding hash ID data
    merged_df = create_hal_hash_id(wf_path, corpus_year, merged_df)
    if verbose:
        save_merged_data(wf_path, corpus_year, merged_df, step="Hash_")
        print(("\nColumn with the hash IDs is added to the list of contributions "
               "to conferences, with one row per Institute-affiliated author, "
               "merged with employees data."))

    # Getting the dict for renaming columns
    cols_rename_dict = build_hal_col_conversion_dic(org_tup)

    # Selecting columns for final list
    select_cols_list = cols_rename_dict.keys()
    sub_merged_df = merged_df[select_cols_list]
    conf_list_df = sub_merged_df.drop_duplicates(cm_cg.DEDUP_COLS_LIST)
    conf_list_df = conf_list_df.rename(columns=cols_rename_dict)
    
    # Saving final conferences list
    _save_final_df(wf_path, corpus_year, 'conferences',
                   conf_list_df, cols_rename_dict)
    
    # Splitting conferences list by document types and saving the sub-lists
    split_ratio, conf_nb = _split_conf_list_by_doc_type(wf_path, corpus_year,
                                                        conf_list_df, cols_rename_dict)

    return conf_list_df, split_ratio, conf_nb

