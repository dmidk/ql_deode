import metview as mv
import sys
import os
import subprocess
import numpy as np
import yaml

yourUserId = os.environ['USER']
scratchDir = os.environ['SCRATCH']
permDir    = os.environ['PERM']

if __name__ == '__main__':
    
    if len(sys.argv) != 11:
        print ("ERROR: Incorrect number of arguments!")
        print (" Command line: " + str(sys.argv[:]))
        print (" Expected: py_mv_plotting.py $YYYY $MM $DD $anHH $fcHHH $expID $ecType $domId $userIdIn yamlConfig")
        sys.exit(1)

YYYY = sys.argv[1]
MM   = sys.argv[2]
DD   = sys.argv[3]
HH   = sys.argv[4]
FC_HHH = sys.argv[5]
expId  = sys.argv[6]
ecType = sys.argv[7]
domId = sys.argv[8]
userIdIn = sys.argv[9]
yamlConfig = sys.argv[10]

with open(yamlConfig, 'r') as confile:
    mycofig = yaml.safe_load(confile)

# get config
varList          = mycofig['shortNameList']
int_accum_hour   = mycofig['int_accum_hour']
lat_lon_map_area = mycofig['lat_lon_map_area']
lat_inc          = mycofig['lat_inc']
lon_inc          = mycofig['lon_inc']

basedate = YYYY + MM + DD + HH

userId = userIdIn
    
#print('User id is:     ' + userId)    
#print('PERM DIR is:    ' + permDir)    
#print('SCRATCH DIR is: ' + scratchDir)    

print('Date/AN/FC: ' + YYYY + MM + DD + ' ' + HH + ' T+' +FC_HHH)    

getFromEc = False
if ecType == 'ec':
    sourcePath = 'ec:/'+userId+'/deode'
    getFromEc =  True
elif ecType == 'ectmp':
    sourcePath = 'ectmp:/'+userId+'/deode'    
    getFromEc = True
else:
    sourcePath = '/ec/res4/scratch/'+userId+'/deode'
    
# plot path
outPath  = os.path.join(permDir,'diag_plots')
if not os.path.exists(outPath):
    os.makedirs(outPath) 

# grib path    
destPath = os.path.join(scratchDir,'tmp_grib',expId)
if not os.path.exists(destPath):
    os.makedirs(destPath)       

fc_int = int(FC_HHH)
FC_step = str(fc_int)
FC_step_1 = str(fc_int-1)

if fc_int < 10:
   FC_HHH_str = '000'+str(fc_int)
elif fc_int < 100:
    FC_HHH_str = '00'+str(fc_int)
else:
    FC_HHH_str = '0'+str(fc_int)

FC_H_deacc = 0
# this is for calculating deacumulated previpitation every int_accum_hour hours
if fc_int > int_accum_hour:
    FC_H_deacc = fc_int - int_accum_hour
    
if FC_H_deacc < 10:
    prevFC_str = '000'+str(FC_H_deacc)
elif FC_H_deacc < 100:
    prevFC_str = '00'+str(FC_H_deacc)
else:
    prevFC_str = '0'+str(FC_H_deacc)
    
# expected grib file name: 'GRIBPFDEOD+' domId + FC_HHH_str + strGrib_min_sec

# Logic for now works to plot only hourly fc
strGrib_min_sec = 'h00m00s'

myGribFile = 'GRIBPFDEOD{0}+{1}{2}'.format(domId,FC_HHH_str,strGrib_min_sec)

if FC_H_deacc > 0:
    myGribFile_prevFC     = 'GRIBPFDEOD{0}+{1}{2}'.format(domId,prevFC_str,strGrib_min_sec)

print('--> Source path for grib file is: ' + sourcePath)
print('--> Searching for grib file: ' + myGribFile)
    
if getFromEc:
    
    cmd ='ecp -u ' + sourcePath + '/{0}/{1}/{2}/{3}/{4}/{5}'.format(expId,YYYY,MM,DD,HH, myGribFile) + ' ' + destPath
    print('Executing cmd ' + cmd)    
    subprocess.run(cmd, shell=True)
    
    gbFile = destPath + '/{0}'.format(myGribFile)    

    #this is for deaccumulated precipitation
    if FC_H_deacc > 0:
        cmd ='ecp -u ' + sourcePath + '/{0}/{1}/{2}/{3}/{4}/{5}'.format(expId,YYYY,MM,DD,HH, myGribFile_prevFC) + ' ' + destPath
        print('Executing cmd ' + cmd)    
        subprocess.run(cmd, shell=True)
    
        gbFile_prevFC = destPath + '/{0}'.format(myGribFile_prevFC)    
    
else:
    
    gbFile  = sourcePath + '/{0}/archive/{1}/{2}/{3}/{4}/{5}'.format(expId,YYYY,MM,DD,HH, myGribFile)
    #this is for deaccumulated precipitation
    if FC_H_deacc > 0:    
        gbFile_prevFC = sourcePath + '/{0}/archive/{1}/{2}/{3}/{4}/{5}'.format(expId,YYYY,MM,DD,HH, myGribFile_prevFC)
    
    
print('--> Grib file found: ' + gbFile)
myFC = mv.read(gbFile) 
# this is necesary because mv complains about gridType = lambert_lam
myFC = mv.grib_set(myFC,["gridType",'lambert'])

# loop over shorName variables

for shortName in varList:

    dynamic = False

    typeOfLevel                    = mycofig[shortName]['typeOfLevel']
    level                          = mycofig[shortName]['level']
    accumulated                    = mycofig[shortName]['accumulated']
    contour_shade_min_level_colour = mycofig[shortName]['contour_shade_min_level_colour']
    contour_shade_max_level_colour = mycofig[shortName]['contour_shade_max_level_colour']
    countList                      = mycofig[shortName]['countList']

    if accumulated and FC_H_deacc == 0:
        continue

    if accumulated and FC_H_deacc > 0:    
        print('--> Grib file for calculating accumulated field: ' + gbFile_prevFC) 
    
    print('--> Plotting variable ' + shortName) 
    print('    - typeOfLevel: ' + typeOfLevel) 
    print('    - level: ' + level) 

    if accumulated:
        var = myFC.select(shortName=shortName, typeOfLevel=typeOfLevel, level=level, stepRange='0-'+FC_step)
        myFC_prevFC = mv.read(gbFile_prevFC) 
        myFC_prevFC = mv.grib_set(myFC_prevFC,["gridType",'lambert'])
        var_prevFC = myFC_prevFC.select(shortName=shortName, typeOfLevel=typeOfLevel, level=level, stepRange='0-'+str(FC_H_deacc))
        var_deacc = var - var_prevFC
        myMin  = mv.minvalue(var_deacc)    
        myMean = mv.average(var_deacc)   
        myMax  = mv.maxvalue(var_deacc)
        myStd = mv.stdev_a(var_deacc)
    else:
    
        if shortName == '10mw':
            u_10m =  myFC.select(shortName='10u', typeOfLevel=typeOfLevel, level=level, stepRange=FC_step)
            v_10m =  myFC.select(shortName='10v', typeOfLevel=typeOfLevel, level=level, stepRange=FC_step)
            var = mv.sqrt(u_10m*u_10m + v_10m*v_10m)
            var = mv.grib_set_long(var, ['paramId', 10])
            # calculate also direction
            dir_wind = mv.direction(u_10m, v_10m)
            dir_wind = mv.grib_set_long(dir_wind, ["paramId", 3031])
        elif shortName == 'wgst':
            ugst_10m =  myFC.select(shortName='10efg', typeOfLevel=typeOfLevel, level=level, stepRange=FC_step_1+'-'+FC_step)
            vgst_10m =  myFC.select(shortName='10nfg', typeOfLevel=typeOfLevel, level=level, stepRange=FC_step_1+'-'+FC_step)
        #    print(ugst_10m)
        #    print('v',vgst_10m)
            var = mv.sqrt(ugst_10m*ugst_10m + vgst_10m*vgst_10m)
            var = mv.grib_set_long(var, ['paramId', 260065])
        #    # calculate also direction
        #    #dir_wgst = mv.direction(ugst_10m, vgst_10m)
        #    #dir_wgst = mv.grib_set_long(dir_wgst, ["paramId", 303132])
        elif shortName == 'u' or shortName == 'v':
            u_10m =  myFC.select(shortName='u', typeOfLevel=typeOfLevel, level=level, stepRange=FC_step)
            v_10m =  myFC.select(shortName='v', typeOfLevel=typeOfLevel, level=level, stepRange=FC_step)
            var = mv.sqrt(u_10m*u_10m + v_10m*v_10m)
            var = mv.grib_set_long(var, ['paramId', 10])
            # calculate also direction
            dir_wind = mv.direction(u_10m, v_10m)
           # dir_wind = mv.grib_set_long(dir_wind, ['paramId', 3031])
        else:
            var = myFC.select(shortName=shortName, typeOfLevel=typeOfLevel, level=level, stepRange=FC_step)

        myMin  = mv.minvalue(var)    
        myMean = mv.average(var)   
        myMax  = mv.maxvalue(var)
        myStd = mv.stdev_a(var)
 

    print('     min/mean/max/std {0}/{1}/{2}/{3}: '.format(myMin,myMean,myMax,myStd))
    
    if len(countList) == 0:
        dynamic = True

        # need to rescale to the expected units, metview automatically does it for some variables 
        # (find a way independed from shortName?)
        # temperature
        if shortName == '2t' or shortName == 't':
            int_min = np.floor(myMin-273.15)    
            int_max = np.ceil(myMax-273.15) 
    	# geopotential
        elif shortName == 'z':
            int_min = np.floor(myMin/100.0)    
            int_max = np.ceil(myMax/100.0) 
    	# surface pressure
        elif shortName == 'sp' or shortName == 'msl':
            int_min = np.floor(myMin/100.0)    
            int_max = np.ceil(myMax/100.0) 
        else:
            int_min = np.floor(myMin)    
            int_max = np.ceil(myMax)         
            # This is for accumulated precipitation (force min = 1)
            if accumulated:
                int_min = 1
                if int_max <= 1:
                    int_max = 2

        interval = int_max - int_min     
        
        #print('interval ' + str(interval))

        if interval < 20:
            interval_step = 1 
        elif interval < 40:
            interval_step = 2 
        elif interval < 60:
            interval_step = 3 
        elif interval < 80:
            interval_step = 4
        elif interval < 100:
           interval_step = 5
        elif interval < 200:
           interval_step = 10
        elif interval < 500:
           interval_step = 25
        elif interval < 1000:
           interval_step = 50
        elif interval < 2000:
           interval_step = 100
        else:
           interval_step = 250
 

    coastlines = mv.mcoast(
        map_coastline_land_shade        = "on",
        map_coastline_land_shade_colour = "RGB(0.9448,0.8819,0.765)",
        map_coastline_sea_shade         = "on",
        map_coastline_sea_shade_colour  = "RGB(0.8178,0.9234,0.9234)", 
        map_coastline_thickness         =  2,
        map_boundaries                  = "on",
        map_boundaries_thickness        =  2, 
        map_boundaries_colour           = "charcoal",
        map_cities                      = "on", 
        map_grid_colour                 = "charcoal",
        map_grid_latitude_increment     = lat_inc,    
        map_grid_longitude_increment    = lon_inc
        )
    
    view = mv.geoview(
        #map_projection      = projection,
        map_area_definition = "corners",
        area                = lat_lon_map_area,    
        coastlines          = coastlines,
    )
    
    if dynamic == False:
        xs_shade = mv.mcont(
            legend                         = "on",
            contour_line_style             = "dash",
            contour_line_colour            = "charcoal",
            contour_highlight              = "off",
            contour_label                  = "off",
            contour_shade                  = "on",
            contour_shade_method           = "area_fill",
            contour_shade_min_level_colour = contour_shade_min_level_colour,
            contour_shade_max_level_colour = contour_shade_max_level_colour, 
            contour_shade_colour_direction = "clockwise",
            contour_level_selection_type   = "LEVEL_LIST",
            contour_level_list = countList
            )
    else:    
        xs_shade = mv.mcont(
            legend="on",
            contour_line_style = "dash", 
            contour_line_colour = "charcoal",
            contour_highlight   = "off",
            contour_label       = "off",
            contour_shade="on",
            contour_level_selection_type="interval",
            contour_max_level=int_max,
            contour_min_level=int_min,
            contour_interval=interval_step,
            contour_shade_method="area_fill",
            contour_shade_min_level_colour = contour_shade_min_level_colour,
            contour_shade_max_level_colour = contour_shade_max_level_colour, 
        )    


            #contour_shade_colour_list_policy="dynamic",
    
#contour_automatic_setting      = "ecmwf"
        #contour_line_style = "dash", 
        #contour_line_colour = "charcoal",
        #contour_highlight   = "off",
        #contour_label       = "off",
        #contour_shade="on",
        #contour_level_selection_type="interval",
        #contour_max_level=int_max,
        #contour_min_level=int_min,
        #contour_interval=interval_step,
        #contour_shade_method="area_fill",
        #contour_shade_min_level_colour = contour_shade_min_level_colour,
        #contour_shade_max_level_colour = contour_shade_max_level_colour, 
        #contour_shade_colour_direction = "clockwise",'''

    mydir = os.path.join(outPath, expId,basedate)
    if not os.path.exists(mydir):
        os.makedirs(mydir)
    
    if typeOfLevel == 'isobaricInhPa':
        plotName = expId + '.' + shortName + '.' + str(level) + '.' + YYYY+MM+DD+HH+'T'+FC_step    
    else:
        plotName = expId + '.' + shortName + '.' + YYYY+MM+DD+HH+'T'+FC_step
    
    mv.setoutput(mv.png_output(output_name=plotName,output_width=1200))
    # define legend
    legend = mv.mlegend(
        legend_automatic_position ="top",
        legend_text_font_size=0.4,
    )
    if accumulated and FC_H_deacc > 0:
        
        title = mv.mtext(
            text_line_1 = "<grib_info key='name'/> [<grib_info key='units'/>];   <grib_info key='base-date' format='%Y%m%d %HUTC'/> Step: +<grib_info key='step'/>h [<grib_info key='valid-date' format='%Y%m%d %HUTC'/>]" + ' Deaccumulated: Step +' + FC_step + 'h minus Step +' + str(FC_H_deacc) + 'h',
            text_font_size=0.6,
        )

        mv.plot(view,
                var_deacc, 
                xs_shade,
                legend,
                title)
    
        cmd = 'mv ' + plotName + '* ' + mydir
        subprocess.run(cmd, shell=True)
        print('--> Plot saved in ' + os.path.join(mydir,plotName))    
    
    else:
    
        title = mv.mtext(
            text_line_1 = "<grib_info key='name'/> [<grib_info key='units'/>]; <grib_info key='typeOfLevel'/> Level: <grib_info key='level'/>; <grib_info key='base-date' format='%Y%m%d %HUTC'/> Step: +<grib_info key='step'/>h [<grib_info key='valid-date' format='%Y%m%d %HUTC'/>]",
            text_font_size= 0.6
        )
    
        mv.plot(view,
                var, 
                xs_shade,
                legend,
                title)
    
        cmd = 'mv ' + plotName + '* ' + mydir
        subprocess.run(cmd, shell=True)
        print('     Plot saved in ' + os.path.join(mydir,plotName))    

