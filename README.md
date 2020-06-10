# COVID_analysis
Set of Python utilities to generate easily understandable charts and graphs from the daily infection data available on the COVID Tracking Project

The COVID Tracking Project (https://covidtracking.com/data) offers daily data on the covid infection progress. The data is available for download or the tables can be studied on their website. I had a hard time getting a good understanding on the overall pandemic progress in the United States, so developed these tools to process, analyze and plot the data.

I am making all the code here available with no restrictions whatsoever. You are welcome to copy, use, modify and share as you see fit. I welcome bug reports and new functions, but any contributions must be under the same licence. If you'd like to contribute, but are uncomfortable with this, you are more than welcome to put everything into your own repository and manage licencing as you deem necessary.

Usage

To use the code, you need a machine that has python3. All the modules identify /usr/bin/python3 as the interpreter. If your environment is different, either edit this or call your python3 with a program as the argument. All .py and .json files must be put into a single directory. You will also need to have png subdirectory to store any generated PNG images.

By default, programs produce multipage PDF files. If PNG is selected as the output type (-o png), one file will be produced for each page.

US has 56 states and territories and at this moment 55 (all except American Samoa) have reported covid cases. File states.json has name, id and population for each. You should not have to regenerate it, but if you do, get_states.py will download the list of states from the COVID project. This list will be missing population numbers for some territories, edit the file and put them in by hand. Most current numbers are 2019, but some of the manually entered numbers are 2019.

Start by running get_curr_json.py, which will get the current cumulative data file from The COVID project. Processing ignores any today's data in the file, since it's likely to be partial. This will produce latest.json file.

Both .json files have one line per record. Parser relies on this, so don't change it.

To make numbers comparable across states, everything is reported in cases per million inhabitants.

The following programs are available. Both support -h to see usage

mksummary.py - makes summary tables with latest per state data, sorted worst-to-best. It provides total number of cases, new number of daily cases, the rate of change of the new number of daily cases and the acceleration of that rate.

analyze_pos.py - makes two charts for each state. One plots the raw and smoothed number of total reported cases. The other reports the rate of change and the acceleration. In PDF, they are put in positive.pdf and pos_d1d2.pdf (I use d1, d2 and d3 since these are first, second and third derivatives of the number of cases).

All the other modules are called by these two programs.

There is an extraordinary amount of noise in the data, especially between the days of the week. Weekends see much less testing and thus much fewer cases, only to have a spike on Monday and Tuesday. Almost all analysis is done on the smoothed data - 7 day running average serves as a lowpass filter. In particular, smoothed data is used to generate the derivatives, which are again smoothed a bit.

Note that this smoothing makes the reported state of affairs lag a bit after the raw data.

I hope you will find these utilities useful.