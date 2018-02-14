import glob
import argparse
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import AutoMinorLocator
import warnings
warnings.filterwarnings('ignore')

##### Begin: User input #####

# Emission line to indicate
em_line=pd.DataFrame({'line': [r'$H_{\alpha}$', r'$H_{\beta}$', r'$H_{\gamma}$', r'$H_{\delta}$', r'OII', r'OIII', r'NII', r'NII', r'$Ly_{\alpha}$', r'$Ly_{\beta}$', r'C${\ IV}$', r'$Mg{\ II}$'],
                      'wavelength': [6562.8433, 4861.2786, 4340.462, 4101.74, 3727., 5007., 6549.8, 6585.3,1215.67,1025.72,1549.06,2798.75] })

# Set the files
# Prompt for new files if they need to be different ones
#tellurics_file = input("Enter telluric line file [default: atran0.85-2.4.dat] : ") or str("atran0.85-2.4.dat")
#skylines_file = input("Enter sky emission lines file [default: rousselot2000.txt] : ") or str("rousselot2000.txt")
tellurics_file = "atran0.85-2.4.dat"
skylines_file = "rousselot2000.txt"

##### End: User input #####
parser = argparse.ArgumentParser()

def evalcmlarg(text):
    return eval(text)

dw=0.155    # Full wavelength range at 2.4um. It will be rescaled below depending on CW

parser.add_argument("--dW",type=evalcmlarg, help='[Optional] Wavelength range or multiplte of the default 0.155 um in the K-band')
parser.add_argument("--CW",type=float, help='[Default: 2.1] Central wavelength of the observation in um .....')
parser.add_argument("--z",type=float, help='[Default: 2.2] Target redshift .................................')
parser.add_argument("--T",type=str, help='[Default: G2 ] A G2 spectrum reference template to plot ........\
                                          Stellar models: A3, F3, G2, K3 (lgg=3.4, Fe/H=0.0, nlte.mpia.de) \
                                          Galaxy type: Ell2, Ell5, Ell13, S0, Sa, Sb, Sc, Sd, Sdm, Spi4 ..\
                                          Starbursts: M82, N6090, N6240, Arp220, (IRAS:) I20551, I22491 ..\
                                          Seyfert: Mrk231, I19254, Sey18, Sey2 ...........................\
                                          QSOs: QSO, QSO1, TQSO1, QSO2, BQSO1, QSO2_Torus ................')
parser.add_argument("--L",type=float, help='[Optional] A line of your choice to be marked [in um], e.g. 2.12 for H2')
newinput=parser.parse_args()
if newinput.CW :
    CW=newinput.CW
else:
    CW=input("Enter central wavelength in um [default: 2.1 um]: ") or float(2.1); CW=float(CW)    # Central Wavelengt in micron
if newinput.dW :
    dw=newinput.dW
else:
    dw=dw*(CW/2.4)
if newinput.z :
    z=newinput.z
else:
    z=input("Enter target redshift [default: 2.2]: ") or float(2.2); z=float(z)      # Object redshift
if newinput.T :
    template_in=newinput.T
else:
    template_in=input("Enter a choice of reference template\n\
                      R=10k stellar models: A3, F3, G2, K3 (lgg=3.4, Fe/H=0.0, nlte.mpia.de)\n\
                      Low-res galaxy type: Ell2, Ell5, Ell13, S0, Sa, Sb, Sc, Sd, Sdm, Spi4\n\
                      Starbursts: M82, N6090, N6240, Arp220, (IRAS:) I20551, I22491\n\
                      Seyfert: Mrk231, I19254, Sey18, Sey2\n\
                      QSOs: QSO, QSO1, TQSO1, QSO2, BQSO1, QSO2_Torus\n\
                      [default: G2]: ") or str("G2")
if newinput.L:
    user_line=(1+z)*newinput.L

indicate_lines=0
if indicate_lines==1:
    template_line_file="NLTE_mod/"+str(template_in)+"_use_lines"

# Read the data files
tellurics = pd.read_table(tellurics_file, delim_whitespace=True, engine='c', 
                          header=None, names=['t_lam','t_flx'], usecols=[0,1])

skylines = pd.read_table(skylines_file, delim_whitespace=True, engine='c', 
                          header=None, names=['s_lam','s_flx'], comment='#', usecols=[0,1])

if str(template_in) in 'A3 F3 G2 K3':
    template_file="NLTE_mod/"+str(template_in)+"_L.gz"
    template_spec = pd.read_table(template_file, delim_whitespace=True, engine='c',\
                                  header=None, skiprows=8, names=['tspec_lam','tspec_flx'], usecols=[0,1])
elif str(template_in)=='QSO':
    template_file="Selsing2015.dat.gz"
    template_spec = pd.read_table(template_file, delim_whitespace=True, engine='c',\
                                  header=None, skiprows=1, names=['tspec_lam','tspec_flx','tspec_flx_err'], usecols=[0,1,2])
else:
    template_file=glob.glob('swire_library/'+str(template_in)+'*sed.gz')[0]
    template_spec = pd.read_table(template_file, delim_whitespace=True, engine='c',\
                                  header=None, names=['tspec_lam','tspec_flx'], usecols=[0,1])
#        str(template_in) in 'swire_library/swire_library_IDs'


if indicate_lines==1:
    template_lines = pd.read_table(template_line_file, delim_whitespace=True, engine='c', 
                              header=None, skiprows=1, names=['tspline_lam','tspline_ID','tspline_lgg','tspline_Elow','tspline_linstr'], usecols=[0,1,2,3,4])

lowlim=CW-dw/2.     #calclate lower limit
uplim=CW+dw/2.      #calclate upper limit

# Format the plot
plt.style.use('classic')
plt.figure(facecolor='white', figsize=plt.figaspect(0.5))
plt.rcParams["font.family"] = "serif"; plt.axes().ticklabel_format(useOffset=False)
# Set mnor tics
mxtics = AutoMinorLocator(10)
mytics = AutoMinorLocator(4)
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
if indicate_lines==1:
    TSPL_X=template_lines['tspline_lam'][((1+z)*template_lines['tspline_lam']>=lowlim*1e4) \
                     & ((1+z)*template_lines['tspline_lam']<=uplim*1e4) \
                     & (template_lines['tspline_lgg']>0.10)]
    TSPL_Y=template_lines['tspline_ID'][((1+z)*template_lines['tspline_lam']>=lowlim*1e4) \
                     & ((1+z)*template_lines['tspline_lam']<=uplim*1e4) \
                     & (template_lines['tspline_lgg']>0.10)]
symax=SY.max()
tsymax=TSY.max()

# Plot 
plt.plot(TX,TY, color='lightgray', linestyle='-', label='Telluric model, R=10 000 (ATRAN, Lord\'92)', linewidth=0.75, alpha=1)
if str(template_in) in 'A3 F3 G2 K3':
    plt.plot(TSX*(1+z)*1e-4,.5*TSY/tsymax, color='magenta', linestyle='-', label=template_in+', R=10 000 NLTE model (nlte.mpia.de)', linewidth=0.75, alpha=1)
elif str(template_in)=='QSO':
    plt.plot(TSX*(1+z)*1e-4,.5*TSY/tsymax, color='magenta', linestyle='-', label=template_in+', Selsing 2015 templ', linewidth=0.75, alpha=1)
else:
    plt.plot(TSX*(1+z)*1e-4,.5*TSY/tsymax, color='magenta', linestyle='-', label=template_in+', Low-res SWIRE templates (Polletta+\'07)', linewidth=0.75, alpha=1)

# Label the strongest model lines 
if indicate_lines==1:
    TSY=.5*TSY/tsymax; TSY=TSY[TSY<0.47]
    plt.vlines((TSPL_X-6)*1e-4*(1+z),0,.54, color='black', linestyle='--', linewidth=1.05)
    for m_line_loc, m_line_lable in zip(TSPL_X,TSPL_Y):
        m_line_loc=1e-4*(1+z)*(m_line_loc-6.); print(6+m_line_loc/(1e-4*(1+z)), m_line_loc,m_line_lable)
        plt.annotate(m_line_lable,xy=(m_line_loc,0.55),xytext=(.9995*m_line_loc,0.56),fontsize=8)

# Plot sky emission lines
plt.vlines(SX*1e-4,0,SY/symax, color='red', linestyle='-', linewidth=0.5, label='Sky emission lines (Rousselot\'00)', alpha=1,zorder=4)

# Label the sky emission lines
for k, y_val in zip(SX, SY):
    lab='{:.2f}'.format(k) #;print(lab)
    # y_val=float(skylines['s_flx'][(skylines['s_lam']==k)])
    if y_val/symax >= .19 :
        plt.annotate(lab,xy=(k*1e-4,y_val/symax),xytext=(.998*k*1e-4,y_val/symax),
                     fontsize=9)

# Indicate the location of the emission line
x_em_line=(1+z)*1e-4*em_line['wavelength'][((1+z)*em_line['wavelength']>=lowlim*1e4) & ((1+z)*em_line['wavelength']<=uplim*1e4)]
y_em_line=em_line['line'][((1+z)*em_line['wavelength']>=lowlim*1e4) & ((1+z)*em_line['wavelength']<=uplim*1e4)]
plt.vlines(x_em_line,0,1.03, color='black', linestyle='--', linewidth=1.05, alpha=1,zorder=5, label="Selected emission lines")
for em_line_loc, em_line_lable in zip(x_em_line,y_em_line):
    plt.annotate(em_line_lable,xy=(em_line_loc,1.03),xytext=(.999*em_line_loc,1.04))

if newinput.dW :
    cw_setup="CW = "+str(CW)+"$\mu$m ({:.3f}".format(lowlim)+" - {:.3f}".format(uplim)+")"+"; N3.75, G200"
else:
    cw_setup="CW = "+str(CW)+"$\mu$m ({:.3f}".format(lowlim)+" - {:.3f}".format(uplim)+")"+"; N3.75, G210"

print("\nFew emission lines for z= "+str(z)+" :")
shifted=em_line['wavelength'] * (1+z)*1e-4
em_line.insert(2,'z-shifted',shifted)
print(em_line)
plt.annotate(cw_setup,xy=(lowlim+.002,1.15),xytext=(lowlim+.002,1.15),fontsize=10)

# Indicate user line of choice
if newinput.L:
    plt.vlines(user_line,0,1.05, color='blue', linestyle='--', linewidth=1.3, alpha=1,zorder=5, label='') #"Your line {:}".format(newinput.L)+'$\mu$m')
    plt.annotate('Line {:}'.format(newinput.L)+' z-shifted to {:}'.format(user_line),xy=(user_line,1.03),xytext=(user_line*.995,1.04),fontsize=10)
    print('\nYour input line: {:}'.format(newinput.L)+' restframe is redshifted to: {:}'.format(user_line))
    
plt.legend(loc=1,fontsize=10,ncol=2,columnspacing=.5,markerscale=0.28,framealpha=0)

plt.tight_layout()

plt.savefig('NIR_ohlines.png', bbox_inches='tight')
plt.show()