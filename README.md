# ql_deode (Quick Look for deode outputs)

Basic scripting to plot variables from grib files generated by the Deode-Prototype.
Python relies on the metview package. Scripts (bash/python) work on ATOS (e.g. expected directory structure where to search for the grib files).

To run:

1) configure bash script 's_run_py_mv_plotting_deode.sh' (follow comments provided in the script)

2) configure 'py_mv_config.yml' to customise your plots (e.g. choose variables to plot, scale of colorbar, change geographical domain)

3) run './s_run_py_mv_plotting_deode.sh'. You can submit the script using 'sbatch s_run_py_mv_plotting_deode.sh' just when you need more memory to deal with grib files for high resolution domain (e.g. 500m resolution)


