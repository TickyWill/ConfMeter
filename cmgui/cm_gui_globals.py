"""Sets globals for GUI."""

__all__ = ['APP_COPYRIGHT',
           'APP_VERSION',
           'HAL_DATATYPE',
           'HELP_BUTTON',
           'PAGES_LABELS',
           'PAGE_TITLE',
           'REF_HELP_BUT_POS_X_MM',
           'REF_HELP_BUT_POS_Y_MM',
           'REF_STEP_POS_Y_MM_LIST',
           'REF_YEAR_BUT_POS_X_MM',
           'REF_YEAR_BUT_POS_Y_MM',
           'STEP_HELPS_LIST',
           'STEP_LABELS_LIST',
           'STEP_LAUNCHS_LIST',
           'STEPS_NB',
           ]


# Standard library imports
import math

# ========================= General globals =========================

# Setting application version value (internal)
VERSION ='0.0.0'

HAL_DATATYPE = None

# Setting label for each gui page
PAGES_LABELS = {'BuildConfPage' : "Consolidation annuelle des corpus",
               }

# =================== Cover Page (launching Page) ===================

# Titre de la page
PAGE_TITLE = "- ConfMeter -\nInitialisation de l'analyse"

# Copyright and contacts
APP_COPYRIGHT  =   "Contributeurs et contacts :"
APP_COPYRIGHT +=  "\n- Amal Chabli : amal.chabli@orange.fr"
APP_VERSION = f"\nVersion {VERSION}"


# ======================== Building conferences page ========================

# Setting label of help button
HELP_BUTTON = "Description"

# Setting reference positions in mm for help buttons
REF_HELP_BUT_POS_X_MM = 180
REF_HELP_BUT_POS_Y_MM = 0

# Setting reference positions in mm for button of year selection 
REF_YEAR_BUT_POS_X_MM = 10
REF_YEAR_BUT_POS_Y_MM = 50

# Setting parameters for each step
STEPS_NB = 4
REF_STEP_POS_Y_MM_LIST = [20, 74, 101, 129]
STEP_LABEL, STEP_HELP, STEP_LAUNCH = [], [], []

# Step 0
STEP_LABEL.append("Effectifs - Mise en conformité des données")
STEP_HELP.append("Une copie du fichier original des effectifs va être créée "
                 "en ajoutant une colonne pour les noms complets "
                 "au format <Prénom Nom> pour simplifier "
                 "le croisement avec les extractions de HAL."
                 "\n\nCette mise en conformité n'a besoin d'être effectuée "
                 "que si le fichier original des effectifs a été modifié.")
STEP_LAUNCH.append("Lancer la mise en conformité")

# Step 1
STEP_LABEL.append("Étape 1 - Extraction des contributions à conférence")
STEP_HELP.append("Deux fichiers avec une ligne par contribution vont être créés à "
                 "cette étape :"
                 "\n\n - Un fichier avec l'extraction de toutes les publications ;"
                 "\n - Un fichier avec la sélection des contributions à conférence "
                 "dans l'extraction.")
STEP_LAUNCH.append("Effectuer l'extraction")

# Step 2
STEP_LABEL.append("Étape 2 - Croisement auteurs-efffectifs")
STEP_HELP.append("Deux fichiers avec une ligne par auteur de l'institut "
                 "et par contribution vont être créés à cette étape :"
                 "\n\n - Un fichier avec les auteurs trouvés dans les effectifs "
                 "qui permettra de construire la liste consolidée ;"
                 "\n - Un fichier avec les auteurs non trouvés dans les effectifs "
                 "dont l'examen permet d'alimenter les fichiers de correction.")
STEP_LAUNCH.append("Effectuer le croisement auteurs-efffectifs")

# Step 3
STEP_LABEL.append("Étape 3 - Consolidation de la liste des contributions à conférence")
STEP_HELP.append("Un fichier avec une ligne par contribution va être créé après "
                 "construction des informations utiles.")
STEP_LAUNCH.append("Créer la liste consolidée des contributions à conférence")

# Building lists of steps parameters 
STEP_LABELS_LIST = [STEP_LABEL[step] for step in range(STEPS_NB)]
STEP_HELPS_LIST = [STEP_HELP[step] for step in range(STEPS_NB)]
STEP_LAUNCHS_LIST = [STEP_LAUNCH[step] for step in range(STEPS_NB)]
