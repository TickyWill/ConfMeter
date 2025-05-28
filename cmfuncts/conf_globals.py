"""Module for setting globals specific to conferences
management and analysis.
"""

__all__ = ['CM_ARCHI',
           'CONF_TYPES',
           'CONF_COLS',
           'CONFIG_FOLDER',
           'HAL_USE_COLS',
          ]

# 3rd party imports
import BiblioParsing as bp

CONFIG_FOLDER = 'ConfigFiles'

CM_ARCHI = {'corpus'             : "HAL corpus",
            'country_iso_file'   : "Country_ISO_code.xlsx",    #"Code ISO.xlsx" => "Country_ISO_code.xlsx"
            'country_iso_sheet'  : "Base",
            'country_iso_usecols': ["Code", "English name"], 
            'hal_full_file_base' : " HAL full.xlsx",
            'hal_conf_file_base' : " HAL conf.xlsx"
           }

CONF_TYPES = ['COMM', 'POSTER']

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
                'country'     : 'Pays',}


CONF_COLS = {'pub_id'      : bp.COL_NAMES['authors'][0],      # "Pub_id"
             'author_idx'  : bp.COL_NAMES['authors'][1],      # 'Idx_author'
             'co_author'   : bp.COL_NAMES['authors'][2],      # "Co_auteur" => 'Co_author'
             'first_author': "Premier auteur",
             'pub_year'    : "Année de publication",
             'conf_year'   : "Année de conférence",
             'conf_name'   : HAL_USE_COLS['conf_name'],
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
