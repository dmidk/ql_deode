#!/bin/bash

# change here to submit with sbatch
# mem > 8000 can be necessary for high reslution domains
#SBATCH --job-name=py_mv_plotting
#SBATCH --qos=nf
#SBATCH --time=01:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --mem=16000

module load python3/3.8.8-01           #3.10.10-01
module load ecmwf-toolbox/2021.08.3.0  #2023.04.1.0

# ecType: needed to identify location of grib files 
# ecType: ec, ectmp --> search in 'ec:/'+userId+'/deode'
# ecType: none      --> search in '/ec/res4/scratch/'+userId+'/deode'
ecType=none

# userId: needed to identify location of grib files
# your user id on atos; otherwise specify other user id
userId=nhac

# List name of experiment and the corresponding domain 
# necessary to pick up location and grib file name

domNames=(DK_300x300_2500m DK_500x500_1500m DK_1000x1000_750m DK_1500x1500_500m)
expNames=(DK_2500m_20210708_harmonie DK_1500m_20210708_harmonie DK_750m_20210708_harmonie DK_500m_20210708_harmonie)


# List of AN times
hours=(00) 
# Start and end year
year1=2021
year2=2021
# Start and end month
month1=7
month2=7
# Start and end day
day1=8
day2=8
# Start and end fc length
fc1=15
fc2=22


# --> Adjust dates/time (YEAR, MONTH, DAY, FC STEP) in loops below 

# Before running, check/configure the yml file for your plotting
myYmlFile=py_mv_config.yml

# name of python script to run
myPyFile=py_mv_plotting_deode.py
#######################################

nE=${#expNames[@]}
nHH=${#hours[@]}

# Loop over experimets
for (( i=0; i<${nE}; i++ ));
  do

  expID=${expNames[$i]}
  domID=${domNames[$i]}

# Set --> YEAR
for YYYY in $(seq -f "%04g" $year1 $year2); do
 # Set --> MONTH
 for MM in $(seq -f "%02g" $month1 $month2); do
  # Set --> DAY
  for DD in $(seq -f "%02g" $day1 $day2); do
  # Loop over AN times
  for (( j=0; j<${nHH}; j++ ));
    do
     anHH=${hours[$j]}
      if [[ ${anHH} == "06" ]] || [[ ${anHH} == "18" ]] ; then
        # Set --> FC STEP 
        for fcHHH in $(seq -f "%04g" $fc1 $fc2); do
          python3 ${myPyFile} $YYYY $MM $DD $anHH $fcHHH $expID $ecType $domID $userId $myYmlFile
        done
      fi

      if [[ ${anHH} == "00" ]] || [[ ${anHH} == "12" ]] ; then
        # Set --> FC STEP    
        for fcHHH in $(seq -f "%04g" $fc1 $fc2); do
          python3 ${myPyFile} $YYYY $MM $DD $anHH $fcHHH $expID $ecType $domID $userId $myYmlFile
        done
      fi

    done  #AN
   done #DAY
  done #MONTH
done  #YEAR

done # EXP
