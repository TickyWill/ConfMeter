"""The `app` module launch the 'ConfMeter' application through `AppMain` class
of `main_page` module of `cmgui` package.
"""


# Local imports
from cmgui.main_page import AppMain

def run_cm():
    """Main function used for starting the ConfMeter application.
    """
    try:
        app = AppMain()
        app.mainloop()
    except Exception as err:
        print(err)

if __name__=="__main__":
    run_cm()
