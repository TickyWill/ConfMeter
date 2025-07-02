"""Module for setting globals specific to conferences
management and analysis.
"""

__all__ = ['CM_ARCHI',
           'CONF_ADD_COLS',
           'CONF_COLS',
           'CONF_DF_TITLE',
           'CONF_NAMES_DIC',
           'CONF_TYPES',
           'CONF_TYPES_DIC',
           'CONFIG_FOLDER',
           'DEDUP_COLS_LIST',
           'HAL_USE_COLS',
           'HASH_COL',
           'INDISPONIBLE',
           'ORPHAN_ARCHI',
           'ORPHAN_SHEET_NAMES',
           'ORTHO_COLS',
           'PUB_ID_SHIFT',
           'ROW_COLORS',
           'XL_INDEX_BASE',
          ]


# 3rd party imports
import bmfuncts.pub_globals as bm_pg

INDISPONIBLE = "indisponible"


CONFIG_FOLDER = 'ConfigFiles'


PUB_ID_SHIFT = 500


XL_INDEX_BASE = bm_pg.XL_INDEX_BASE


ROW_COLORS = bm_pg.ROW_COLORS


CM_ARCHI = {'corpus_folder'        : "0- HAL corpus",
            'conf_empl_folder'     : "1- Croisement avec effectifs",
            'final_results_folder' : "2- Résultats finaux",
            'country_iso_file'     : "Country_ISO_code.xlsx",
            'country_iso_sheet'    : "Base",
            'country_iso_usecols'  : ["Code", "English name"], 
            'hal_full_file_base'   : " HAL full.xlsx",
            'hal_conf_file_base'   : " HAL conf.xlsx",
            'hal_corr_file_base'   : " HAL corr.xlsx",
            'hash_id_file_name'    : "Hash ID.xlsx",
            'valid_authors'        : "Auteurs identifiés.xlsx",
            'orphan_authors'       : "Orphan.xlsx",
            'conf_list_file_base'  : bm_pg.ARCHI_YEAR["pub list file name base"],
           }


CONF_NAMES_DIC = {'conferences'    : "Conférences",
                  'communications' : "Oraux",
                  'posters'        : "Posters",
                  'others'         : "Autres",}

CONF_TYPES_DIC = {'communications' : ['COMM'],
                  'posters'        : ['POSTER'],}


CONF_TYPES = sum(list(CONF_TYPES_DIC.values()), [])


HAL_USE_COLS = {'authors'     : 'Auteurs',
                'title'       : 'Titres',
                'pub_date'    : 'Date de publication',
                'journal'     : 'Journal',
                'eissn'       : 'e-ISSN',
                'issn'        : 'ISSN',
                'conf_name'   : 'Conference',
                'conf_date'   : 'Date de conference',
                'commitee'    : 'Comite de lecture',
                'proceedings' : 'Acte de conference',
                'affiliations': 'Affiliations',
                'institutions': 'Institutions',
                'depts'       : 'Depts',
                'organisms'   : 'Organismes',
                'doctype'     : 'Type de document',
                'keywords'    : 'Mots clefs',
                'doi'         : 'DOI',
                'url'         : 'Lien url',
                'country'     : 'Pays',
                'full_ref'    : '01',
               }


CONF_COLS = {'pub_id'      : "Pub_id",
             'author_idx'  : "Idx_author",
             'co_author'   : "Co_author", 
             'first_author': "Premier auteur",
             'pub_year'    : "Année de publication",
             'conf_year'   : "Année de conférence",
             'conf_date'   : HAL_USE_COLS['conf_date'],
             'conf_name'   : HAL_USE_COLS['conf_name'],
             'town'        : "Ville",
             'country'     : HAL_USE_COLS['country'],
             'doctype'     : HAL_USE_COLS['doctype'],
             'commitee'    : HAL_USE_COLS['commitee'],
             'title'       : HAL_USE_COLS['title'],
             'doi'         : HAL_USE_COLS['doi'],
             'keywords'    : HAL_USE_COLS['keywords'],
             'proceedings' : HAL_USE_COLS['proceedings'],
             'url'         : HAL_USE_COLS['url'],
             'conf_date'   : HAL_USE_COLS['conf_date'],
             'pub_date'    : HAL_USE_COLS['pub_date'],
             'authors'     : HAL_USE_COLS['authors'],
             'affiliations': HAL_USE_COLS['affiliations'],
             'institutions': HAL_USE_COLS['institutions'],
             'depts'       : HAL_USE_COLS['depts'],
             'organisms'   : HAL_USE_COLS['organisms'],             
            }

HASH_COL = {'hash_id' : "Hash_id",}

ORTHO_COLS = {'pub_fullname'  : "Nom pub complet",
              'empl_fullname' : "Nom eff complet",
             }


ORPHAN_ARCHI = bm_pg.ARCHI_ORPHAN


ORPHAN_SHEET_NAMES = bm_pg.SHEET_NAMES_ORPHAN


CONF_ADD_COLS = {'author_type' : bm_pg.COL_NAMES_BONUS['author_type'],
                 'full_ref': bm_pg.COL_NAMES_BONUS['liste biblio'],
                 'inst_authors' : bm_pg.COL_NAMES_BONUS['nom prénom liste'],
                 'all_authors'  : bm_pg.COL_NAMES_BONUS['liste auteurs'],
                }

DEDUP_COLS_LIST = [CONF_COLS['pub_id'],
                   CONF_COLS['conf_year'],
                   CONF_COLS['first_author'],
                   CONF_COLS['title'],
                   CONF_COLS['conf_name'],   
                   CONF_COLS['doctype'],
                   CONF_COLS['country'],
                   CONF_COLS['commitee'],]

CONF_DF_TITLE = bm_pg.DF_TITLES_LIST[0]
