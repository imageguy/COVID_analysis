# COVID_analysis
Set of Python utilities to generate easily understandable charts and graphs from the daily infection data available on the COVID Tracking Project

The COVID Tracking Project (https://covidtracking.com/data) offers daily data on the covid infection progress. The data is available for download or the tables can be studied on their website. I had a hard time getting a good understanding on the overall pandemic progress in the United States, so developed these tools to process, analyze and plot the data.

I am making all the code here available with no restrictions whatsoever. You are welcome to copy, use, modify and share as you see fit. I welcome bug reports and new functions, but any contributions must be under the same licence. If you'd like to contribute, but are uncomfortable with this, you are more than welcome to put everything into your own repository and manage licencing as you deem necessary.

Usage

To use the code, you need a machine that has python3. All the modules identify /usr/bin/python3 as the interpreter. If your environment is different, either edit this or call your python3 with a program as the argument. All .py and .json files must be put into a single directory. You will also need to have png subdirectory to store any generated PNG images.

Code requires requests, matplotlib and reportlib packages.

By default, programs produce multipage PDF files. If PNG is selected as the output type (-o png), one file will be produced for each page.

US has 56 states and territories and at this moment 55 (all except American Samoa) have reported covid cases. File states.json has name, id and population for each. You should not have to regenerate it, but if you do, get_states.py will download the list of states from the COVID project. This list will be missing population numbers for some territories, edit the file and put them in by hand. Most current numbers are 2019, but some of the manually entered numbers are 2018.

Start by running get_curr_json.py, which will get the current cumulative
data file from The COVID Tracking Project. Processing ignores any today's data in the file, since it's likely to be partial. This will produce latest.json file.

Both .json files have one line per record. Parser relies on this, so don't change it.

To make numbers comparable across states, everything is reported in cases per million inhabitants.

The following programs are available. All support -h to see usage:

mksummary.py :

Makes summary tables with latest per state data, sorted worst-to-best. It provides total number of cases, estimated number of active cases, new number of daily cases, the rate of change of the new number of daily cases and the acceleration of that rate. It also predicts the number of days until total, active and new double and gives how many days it took for the totals and actives to double until the last day of data.

Estimated number of active cases is a 7 day running average of the sum of the last 21 days of new cases. 

Makes the tables of state trends. Each state has a line with total number of cases per million, estimated number of active cases per million, daily new cases per million, change rate of the new cases, number of days to double the number of cases, number of days to double the daily number of new cases and number of days to double the number of active cases. It uses a model tha is just a quadratic taking into account change rate of new cases. Finally each line lists the number of days it took for the total positives and actives to double to the latest value. This is always in trends.pdf, regardless of any -o value. Use pdftopng to get PNG images.

Makes the mortality tables, along similar lines to trends, listing deaths per million and mortality rates per reported infected, per reported infected 14 days ago (it takes a while for the cases to become serious) and per population. Total positives per million and active cases per million are added for context.

Prints the list of the states at risk (meaningfully rising rate of new cases) and d2 summary analysis to stdout.

analyze_pos.py :

Makes two plots for each state. One plots the raw and smoothed number of total reported cases. The other reports the rate of change and the acceleration.

By default, these two are combined on the same page, though this can be changed by specifying pos,d1d2 to -a option.

In PDF, output is combined in a single multipage file, pos_combined.pdf (or two files, positive.pdf and pos_d1d2.pdf if separate output is chosen). (I use d1, d2 and d3 since these are first, second and third derivatives of the number of cases). For PNG output, each plot page (one or two per state) is stored in a separate file in the png directory.

Finally, a plot of d3 for all states over the last 15 days is produced to give a sense of current trends. Lines sloping up on the right are indication the infection is intensifying in these states.

analyze_tst.py:

Makes a plot of the number of daily tests, combined with the percentage of positive tests. It builds either a single PDF file, tests.pdf, or, for PNG, one file per state in png directory. Test data is even noisier than number of cases data, so plots are 7 day moving averages.

analyze_sev.py:

Makes charts of "severe" cases, namely hospitalizations, ICU admissions, ventilator usage and mortality. Makes two plots per state, one on daily hospital/ICU/ventilator, together with cumulative mortality and daily active cases for scale. The other is mortality rate vs. daily number of deaths per million.

Except for deaths, other data are sparsely reported and sometimes obviously wrong.

All the other modules are called by these programs.

There is an extraordinary amount of noise in the data, especially between the days of the week. Weekends see much less testing and thus much fewer cases, only to have a spike on Monday and Tuesday. Almost all analysis is done on the smoothed data - 7 day running average serves as a lowpass filter. In particular, smoothed data is used to generate the derivatives, which are again smoothed a bit.

Note that this smoothing makes the reported state of affairs lag a bit after the raw data.

Current code can also process opening and closing actions for each state (if any). The close and open actions are represented as dashed vertical lines in the positives and new cases graphs. Events are given in actions.json file, which is currently only partially populated. The parsing code in process.py has been commented out, since the actions did not seem to provide any useful insight. The data on actions is diverse and hard to gather and the delay in case tracking due to smoothing makes it harder to correlate with the real time government actions. 

I tried to compute infection numbers normalized by the number of tests, but
was unsuccessful. There is so much noise in the data that the normalized
numbers are garbage. Smoothing didn't really help, one would have to go into
data fitting, which I didn't have time for. The code is still in process.py,
just not called.

I hope you will find these utilities useful.
