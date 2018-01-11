import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import AutoMinorLocator
import warnings
warnings.filterwarnings('ignore')

##### Begin: User input #####

CW=input("Enter central wavelength in um [default: 2.1]: ") or float(2.1); CW=float(CW)    # Central Wavelengt in micron

z=input("Enter target redshift [default: 2.2]: ") or float(2.2); z=float(z)      # Object redshift

# Emission line to indicate
em_line=pd.DataFrame({'line': [r'$H_{\alpha}$', r'$H_{\beta}$', r'$H_{\gamma}$', r'$H_{\delta}$', r'OII', r'OIII', r'NII', r'NII'],
                      'wavelength': [6562.8433, 4861.2786, 4340.462, 4101.74, 3727., 5007., 6549.8, 6585.3] })

# Set the files
# Prompt for new files if they need to be different ones
#tellurics_file = input("Enter telluric line file [default: atran0.85-2.4.dat] : ") or str("atran0.85-2.4.dat")
#skylines_file = input("Enter sky emission lines file [default: rousselot2000.txt] : ") or str("rousselot2000.txt")
tellurics_file = "atran0.85-2.4.dat"
skylines_file = "rousselot2000.txt"
template_in=input("Enter choice a (A3, F3, G2, K3) of reference template (lgg=3.4, Fe/H=0.0) spectrum [default: G2]: ") or str("G2")
template_file="NLTE_mod/"+str(template_in)+"_L"
template_lines="NLTE_mod/"+str(template_in)+"_use_lines"

##### End: User input #####

dw=0.155    # Full wavelength range at 2.4um. It will be rescaled below depending on CW
dw=dw*(CW/2.4)

# Read the data files
tellurics = pd.read_table(tellurics_file, delim_whitespace=True, engine='c', 
                          header=None, names=['t_lam','t_flx'], usecols=[0,1])

skylines = pd.read_table(skylines_file, delim_whitespace=True, engine='c', 
                          header=None, names=['s_lam','s_flx'], skiprows=28, usecols=[0,1])

template_spec = pd.read_table(template_file, delim_whitespace=True, engine='c', 
                              header=None, skiprows=8, names=['tspec_lam','tspec_flx'], usecols=[0,1])

lowlim=CW-dw/2.     #calclate lower limit
uplim=CW+dw/2.      #calclate upper limit

# Format the plot
plt.style.use('classic')
plt.figure(facecolor='white', figsize=plt.figaspect(0.5))
# Set mnor tics
mxtics = AutoMinorLocator(10)
mytics = AutoMinorLocator(5)
plt.axes().xaxis.set_minor_locator(mxtics)
plt.axes().yaxis.set_minor_locator(mytics)
plt.axes().tick_params(axis='both', direction='in')
plt.axes().tick_params(which='minor', axis='both', direction='in')

#Set plot limits
plt.xlim(lowlim,uplim); plt.xticks(fontsize=10)
plt.ylim(0,1.2); plt.yticks(fontsize=10)
plt.xlabel('Wavelength [$\mu$m]', fontsize=12)
plt.ylabel('Flux [fractional]', fontsize=12)

#Trim the data
TX=tellurics['t_lam'][(tellurics['t_lam']>=lowlim) & (tellurics['t_lam']<=uplim)]
TY=tellurics['t_flx'][(tellurics['t_lam']>=lowlim) & (tellurics['t_lam']<=uplim)]
SX=skylines['s_lam'][(skylines['s_lam']>=lowlim*1e4) & (skylines['s_lam']<=uplim*1e4)]
SY=skylines['s_flx'][(skylines['s_lam']>=lowlim*1e4) & (skylines['s_lam']<=uplim*1e4)]
TSX=template_spec['tspec_lam'][((1+z)*template_spec['tspec_lam']>=lowlim*1e4) & ((1+z)*template_spec['tspec_lam']<=uplim*1e4)]
TSY=template_spec['tspec_flx'][((1+z)*template_spec['tspec_lam']>=lowlim*1e4) & ((1+z)*template_spec['tspec_lam']<=uplim*1e4)]
symax=SY.max()
tsymax=TSY.max()

plt.plot(TX,TY, color='lightgray', linestyle='-', 
         label='Telluric model, R=10 000', linewidth=0.75, alpha=1)
plt.plot(TSX*(1+z)*1e-4,.5*TSY/tsymax, color='magenta', linestyle='-', 
         label=template_in+', R=10 000 NLTE model', linewidth=0.75, alpha=1)
plt.vlines(SX*1e-4,0,SY/symax, color='red', linestyle='-', linewidth=0.5, 
           label='Sky emission lines', alpha=1,zorder=4)

for k, y_val in zip(SX, SY):
    lab='{:.2f}'.format(k) #;print(lab)
    # y_val=float(skylines['s_flx'][(skylines['s_lam']==k)])
    if y_val/symax >= .19 :
        plt.annotate(lab,xy=(k*1e-4,y_val/symax),xytext=(.998*k*1e-4,y_val/symax),
                     fontsize=9)

# Indicate the location of the emission line
x_em_line=(1+z)*1e-4*em_line['wavelength'][((1+z)*em_line['wavelength']>=lowlim*1e4) & ((1+z)*em_line['wavelength']<=uplim*1e4)]
y_em_line=em_line['line'][((1+z)*em_line['wavelength']>=lowlim*1e4) & ((1+z)*em_line['wavelength']<=uplim*1e4)]
plt.vlines(x_em_line,0,1.05, color='black', linestyle='--', linewidth=1.05, alpha=1,zorder=5, label="Emission lines")
for em_line_loc, em_line_lable in zip(x_em_line,y_em_line):
    plt.annotate(em_line_lable,xy=(em_line_loc,1.05),xytext=(.999*em_line_loc,1.06))

cw_setup="CW = "+str(CW)+"$\mu$m ({:.3f}".format(lowlim)+" - {:.3f}".format(uplim)+")"+"; N3.75, G210"
plt.annotate(cw_setup,xy=(lowlim+.002,1.15),xytext=(lowlim+.002,1.15),fontsize=10)

plt.legend(loc=1,fontsize=10,ncol=2,columnspacing=.5,markerscale=0.28,framealpha=0)

plt.tight_layout()

print("\nFew emission lines for z= "+str(z)+" :")
shifted=em_line['wavelength'] * (1+z)*1e-4
em_line.insert(2,'z-shifted',shifted)
print(em_line)

plt.savefig('NIR_ohlines.png', bbox_inches='tight')
plt.show()
