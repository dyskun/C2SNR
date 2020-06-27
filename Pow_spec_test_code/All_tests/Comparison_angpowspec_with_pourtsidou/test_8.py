import numpy as np
import math
import cosmolopy.distance as cd
import cosmolopy.perturbation as cp
import scipy.integrate as integrate
import matplotlib.pyplot as plt
from scipy import interpolate
from tqdm.auto import tqdm
import camb
from camb import model, initialpower, get_matter_power_interpolator

###############################################################################
# Constant factor; integration over distance
###############################################################################
def d_constantfactor(redshift):
    return 2 * 3.14 * (9/4) * (H0/c)**4 * omegam0**2
#------------------------------------------------------------------------------

###############################################################################
# Constant factor; Integration over redshift
###############################################################################
def z_constantfactor(redshift):
   return 2 * 3.14 * (9/4) * (H0/c)**3 * omegam0**2
#------------------------------------------------------------------------------

###############################################################################
## Ang dia distance between z = 0 and some redshift
###############################################################################
def a_distance(var):
    return cd.angular_diameter_distance(var, **cosmo)
#------------------------------------------------------------------------------

###############################################################################
## Comoving distance between z = 0 and some redshift
###############################################################################
def c_distance(var):
    return cd.comoving_distance(var, **cosmo)
#------------------------------------------------------------------------------

###############################################################################
## Hubble ratio H(z)/H0
###############################################################################
def hubble_ratio(var):
    return (omegam0 * (1 + var)**3 + omegal)**0.5
#------------------------------------------------------------------------------

###############################################################################
## Integration over distance
###############################################################################
def d_angpowspec_integrand(dist, ell, dist_s, constf):
    z = np.interp(dist, dist_red, red)
    return constf * (1 - dist/dist_s)**2 * PK.P(z, ell * (1 + z)/dist)

def d_angpowspec_integration(ell, redshift):
    constf = d_constantfactor(redshift)
    dist_s = c_distance(redshift)
    return integrate.quad(d_angpowspec_integrand, 0.00001, dist_s, args = (ell, dist_s, constf))[0]

def d_angpowspec_integrand_nl(dist, ell, dist_s, constf):
    z = np.interp(dist, dist_red, red)
    return constf * (1 - dist/dist_s)**2 * PK_nl.P(z, ell * (1 + z)/dist)

def d_angpowspec_integration_nl(ell, redshift):
    constf = d_constantfactor(redshift)
    dist_s = c_distance(redshift)
    return integrate.quad(d_angpowspec_integrand_nl, 0.00001, dist_s, args = (ell, dist_s, constf))[0]
#------------------------------------------------------------------------------

###############################################################################
## Integration over redshift
###############################################################################
def z_angpowspec_integrand(z, ell, dist_s, constf):
    dist = a_distance(z)
    return constf * (1 - dist/dist_s)**2 * PK.P(z, ell/dist) / (hubble_ratio(z))

def z_angpowspec_integration(ell, redshift):
    constf = z_constantfactor(redshift)
    dist_s = a_distance(redshift)
    return integrate.quad(z_angpowspec_integrand, 0.00001, redshift, args = (ell, dist_s, constf))[0]

def z_angpowspec_integrand_nl(z, ell, dist_s, constf):
    dist = a_distance(z)
    return constf * (1 - dist/dist_s)**2 * PK_nl.P(z, ell/dist) / (hubble_ratio(z))

def z_angpowspec_integration_nl(ell, redshift):
    constf = z_constantfactor(redshift)
    dist_s = a_distance(redshift)
    return integrate.quad(z_angpowspec_integrand_nl, 0.00001, redshift, args = (ell, dist_s, constf))[0]
#------------------------------------------------------------------------------

##############################################################################
# Constants
###############################################################################

omegam0 = 0.315
omegal = 0.685
c = 3 * 10**8
H0 = 100 * 1000
h = 0.673
cosmo = {'omega_M_0': omegam0, 'omega_lambda_0': omegal, 'omega_k_0': 0.0, 'h': 0.673}
l_plot_low_limit = 10
l_plot_upp_limit = 600
redshift = 2                                                                                 
l_max = 600

pars = model.CAMBparams(NonLinear = 0, WantTransfer = True, H0=67.3, omch2=0.1199, ombh2=0.02205, YHe = 0.24770)
pars.DarkEnergy.set_params(w=-1.13)
pars.set_for_lmax(lmax = l_max)
pars.InitPower.set_params(ns=0.9603, As = 2.196e-09)
results = camb.get_background(pars)
k = 10**np.linspace(-6,1,1000) * h
PK = get_matter_power_interpolator(pars, nonlinear=False, kmax = 1, k_hunit = True, hubble_units = True)


pars_nl = model.CAMBparams(NonLinear = 1, WantTransfer = True, H0=67.3, omch2=0.1199, ombh2=0.02205, YHe = 0.24770)
pars_nl.DarkEnergy.set_params(w=-1.13)
pars_nl.set_for_lmax(lmax = l_max)
pars_nl.InitPower.set_params(ns=0.9603, As = 2.196e-09)
results = camb.get_background(pars_nl)
k = 10**np.linspace(-6,1,1000) * h
PK_nl = get_matter_power_interpolator(pars_nl, nonlinear=True, kmax = 1, k_hunit = True, hubble_units = True)

#------------------------------------------------------------------------------

###############################################################################
# To store the data
###############################################################################
d_file = open("./Text_files/test_8_linear_distance.txt", 'w')
z_file = open("./Text_files/test_8_linear_redshift.txt", 'w')

d_file_nl = open("./Text_files/test_8_nonlinear_distance.txt", 'w')
z_file_nl = open("./Text_files/test_8_nonlinear_redshift.txt", 'w')
#------------------------------------------------------------------------------

# Variation of comoving distance with redshift
red, dist_red = np.loadtxt("/home/dyskun/Documents/Utility/Academics/Cosmology_project/C2SNR/Pow_spec_test_code/Data_files/Distances/comov_dist_vs_z.txt", unpack = True)


###############################################################################
# Plot from this work
###############################################################################
for L in tqdm(range(10, l_max)):
    d_file.write('{}    {}\n'.format(L, d_angpowspec_integration(L, redshift)))
    z_file.write('{}    {}\n'.format(L, z_angpowspec_integration(L, redshift)))

for L in tqdm(range(10, l_max)):
    d_file_nl.write('{}    {}\n'.format(L, d_angpowspec_integration_nl(L, redshift)))
    z_file_nl.write('{}    {}\n'.format(L, z_angpowspec_integration_nl(L, redshift)))

d_file.close()
z_file.close()

d_file_nl.close()
z_file_nl.close()


plt.subplots()
###############################################################################
# Plot from Pourtsidou et al. 2014
###############################################################################
h = 0.67
x_2 = np.zeros(50)
y_2 = np.zeros(50)
dxl_2 = np.zeros(50)
dxh_2 = np.zeros(50)
dyl_2 = np.zeros(50)
dyh_2 = np.zeros(50)
x_2, y_2, dxl_2, dxh_2, dyl_2, dyh_2 = np.loadtxt("/home/dyskun/Documents/Utility/Academics/Cosmology_project/C2SNR/Pow_spec_test_code/Data_files/pourtsidou_xyscan_z_2_no_errors.txt", unpack=True)

plt.plot(x_2, (x_2**2 * 2 * 3.14) * (2 * 3.14 *  2 * 3.14) * y_2 / (4 ) ,color='black', label='Pou z = 2.0')
#------------------------------------------------------------------------------


L , d_CL = np.loadtxt('./Text_files/test_8_linear_distance.txt', unpack = True)
L , z_CL = np.loadtxt('./Text_files/test_8_linear_redshift.txt', unpack = True)

L_nl , d_CL_nl = np.loadtxt('./Text_files/test_8_nonlinear_distance.txt', unpack = True)
L_nl , z_CL_nl = np.loadtxt('./Text_files/test_8_nonlinear_redshift.txt', unpack = True)


plt.plot(L, 2 * 3.14 * L**2 * d_CL, label='L Sah. Distance')
plt.plot(L, 2 * 3.14 * L**2 * z_CL, label='L Sah. Redshift')

plt.plot(L_nl, 2 * 3.14 * L_nl**2 * d_CL_nl,  label='NL Sah. Distance')
plt.plot(L_nl, 2 * 3.14 * L_nl**2 * z_CL_nl,  label='NL Sah. Redshift')


plt.xlabel('L')
plt.ylabel(r'$2 \pi \; L^2\; C_{L}$')
plt.suptitle("z = 2")
plt.xscale("log")
plt.yscale("log")
plt.xlim(l_plot_low_limit, l_plot_upp_limit)
plt.legend(loc = 1)
plt.savefig("./Plots/test_8.pdf")
plt.show()
#------------------------------------------------------------------------------
