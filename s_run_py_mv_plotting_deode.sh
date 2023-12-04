#!/bin/bash

# change here to submit with sbatch
# mem > 8000 can be necessary for high reslution domains
#SBATCH --job-name=py_mv_plotting_ita
#SBATCH --qos=nf
#SBATCH --time=02:00:00
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
userId=nhad

# List name of experiment and the corresponding domain 
# necessary to pick up location and grib file name

#expNames=(arome_2500 arome_1500 arome_750)
#expNames=(harmonie_DK_2500 harmonie_DK_1500 harmonie_DK_750)

#domNames=(DK_500x500_1500m)
#expNames=(DK_1500m_Quad_20210708)

#domNames=(ITA_800x800_500m ITA_800x800_750m) 
#expNames=(harmonie_ita_500_ciaran_HRES harmonie_ita_750_ciaran_HRES) 
domNames=(brtny_800x800_500m brtny_800x800_500m brtny_800x800_750m brtny_800x800_750m ) 
expNames=(harmonie_brittany_500_ciaran harmonie_brittany_500_ciaran_HRES harmonie_brittany_750_ciaran harmonie_brittany_750_ciaran_HRES) 
#domNames=(brtny_800x800_500m)
#expNames=(harmonie_brittany_500_ciaran)
#domNames=(NL_800x800_500m NL_800x800_750m NL_800x800_750m)
#expNames=(harmonie_AQ_500_arome harmonie_AQ_750_arome harmonie_AQ_750_summer_case)


# List of AN times
#hours=(00 12) 
hours=(00) # Brittany Ciaran 11-2023
# Start and end year
year1=2023 # Ciaran
year2=2023 # Ciaran
#year1=2018 # AQ Benelux
#year2=2018 # AQ Benelux
# Start and end month
month1=11
month2=11
#month1=07 # AQ Benelux
#month2=07 # AQ Benelux
# Start and end day
day1=01
day2=01
day1=24 # AQ Benelux
day2=25 # AQ Benelux
# Start and end fc length
fc1=00
fc2=48
inc=3

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
        for fcHHH in $(seq -f "%04g" $fc1 $inc $fc2); do
          python3 ${myPyFile} $YYYY $MM $DD $anHH $fcHHH $expID $ecType $domID $userId $myYmlFile
        done
      fi

    done  #AN
   done #DAY
  done #MONTH
done  #YEAR

done # EXP
