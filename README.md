# ConfMeter
## Description
Python application for metrics purpose of contributions to conferences based on analysis of publications metadata extracted from HAL database.<br />
More specifically:<br />
- Selects conference data from data resulting from HAL extraction;
- Take care of the authors misspelling of authors names based on misspelling records;
- Recursively dispatch the conference data per department using the employees data;
- Take care of the authors affiliated to the Institute but not found in the employees database based on complementary data to the employees ones.

## Installation
Run the following command to get a repository clone of the main branch:
```
git clone https://github.com/TickyWill/ConfMeter.git@main
```

## Requirements
Ensure that your environment complies with the requirements given in the following file:
<p><a href=https://github.com/TickyWill/ConfMeter/blob/main/requirements.txt>ConfMeter requirements file
</a></p>

## Documentation building
Run the following commands to build the sphinx documentation:
- Only in case of a previous building
```
docs\make.bat clean
```
- Then
```
docs\make.bat html
```

## Documentation edition
Open the following ConfMeter sphinx-documentation html file:
>docs/docbuild/html/index.html

## Building executable
Either run the following batch file:
<p><a href=https://github.com/TickyWill/ConfMeter/blob/main/ConfMeterBuildExe.bat>ConfMeter executable-building batch file
</a></p>
Or refer to the following manual:
<p><a href=https://github.com/TickyWill/ConfMeter/blob/main/ConfMeterBuildExeManual-Fr.pdf>ConfMeter executable-building manual
</a></p>
<span style="color:red">BEWARE:</span> Some security softwares (eg. McAfee) could place the .exe file in quarantine. If so you have to manually authorized the .exe file.

## Usage example
```python
# Local imports
from cmgui.main_page import AppMain

app = AppMain()
app.mainloop()
```

**for more details on application usage refer to the user manual:** 
<p><a href=https://github.com/TickyWill/ConfMeter/blob/main/confMeterUserManual-Fr.pdf>ConfMeter user manual
</a></p>

# Release History
- 0.0.0 first release

# Meta
	- authors: BiblioMeter team

Distributed under the [MIT license](https://mit-license.org/)
