import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import AutoMinorLocator
# %matplotlib inline

##### Begin: User input #####

CW=2.1    # Central Wavelengt in micron
dw=0.16    # Full wavelength range at 2.4um. It will be rescaled below depending on CW

z=2.2      # Object redshift
em_line=[r'$H_{\alpha}$', 6564.0] # Emission line to indicate

# Set the files
tellurics_file = "atran0.85-2.4.dat"
skylines_file = "rousselot2000.txt"

##### End: User input #####


dw=dw*(CW/2.4)
# Read the data files
tellurics = pd.read_table(tellurics_file, delim_whitespace=True, 
                          header=None, names=['t_lam','t_flx'])

skylines = pd.read_table(skylines_file, delim_whitespace=True, 
                          header=None, names=['s_lam','s_flx'], skiprows=28)

lowlim=CW-dw/2.     #calclate lower limit
uplim=CW+dw/2.      #calclate upper limit

# Set aspec ratio
plt.axes().set_aspect(aspect=0.07)
# Set mnor tics
mxtics = AutoMinorLocator(5)
mytics = AutoMinorLocator(5)
plt.axes().xaxis.set_minor_locator(mxtics)
plt.axes().yaxis.set_minor_locator(mytics)
plt.axes().tick_params(axis='both', direction='in')
plt.axes().tick_params(which='minor', axis='both', direction='in')

#Set plot limits
plt.xlim(lowlim,uplim); plt.xticks(fontsize=9)
plt.ylim(0,1.2); plt.yticks(fontsize=9)
plt.xlabel('Wavelength [$\mu$m]', fontsize=10)
plt.ylabel('Flux [%]', fontsize=10)

#Trim the data
SX=skylines['s_lam'][(skylines['s_lam']>=lowlim*1e4) & (skylines['s_lam']<=uplim*1e4)]
SY=skylines['s_flx'][(skylines['s_lam']>=lowlim*1e4) & (skylines['s_lam']<=uplim*1e4)]
symax=SY.max()
#symax=skylines['s_flx'].max()

plt.plot(tellurics['t_lam'],tellurics['t_flx'], color='lightgray', linestyle='-', 
         label='Telluric model, R=10 000', linewidth=0.75, alpha=1)
plt.vlines(SX*1e-4,0,SY/symax, color='red', linestyle='-', linewidth=0.5, 
           label='Sky emission lines', alpha=1,zorder=4)

for k in SX:
    lab='{:.2f}'.format(k) #;print(lab)
    y_val=float(skylines['s_flx'][(skylines['s_lam']==k)])
    if y_val/symax >= .19 :
        plt.annotate(lab,xy=(k*1e-4,y_val/symax),xytext=(.998*k*1e-4,y_val/symax),
                     fontsize=7)

# Indicate the location of the emission line
em_line_loc=(1+z)*1e-4*em_line[1]
plt.vlines(em_line_loc,0,1.05, color='black', linestyle='--', linewidth=1.05, alpha=1,zorder=5)
plt.annotate(em_line[0],xy=(em_line_loc,1.05),xytext=(.999*em_line_loc,1.06))

cw_setup="CW = "+str(CW)+"$\mu$m ({:.3f}".format(lowlim)+" - {:.3f}".format(uplim)+")" #; print(cw_setup)
plt.annotate(cw_setup,xy=(lowlim+.002,1.15),xytext=(lowlim+.002,1.15),fontsize=7)

plt.legend(loc=1,fontsize=7,ncol=2,columnspacing=.5,markerscale=0.15,framealpha=0)

plt.tight_layout()
plt.savefig('NIR_ohlines.pdf')
plt.show()
print("LUCI N3.75, G210\n For a target at z= "+str(z)+" has Halpa at "+format(em_line_loc)+" um")
