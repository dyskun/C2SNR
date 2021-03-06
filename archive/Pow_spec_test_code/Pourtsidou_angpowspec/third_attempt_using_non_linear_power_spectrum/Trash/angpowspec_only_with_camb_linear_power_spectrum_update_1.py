import numpy as np
import math
import cosmolopy.distance as cd
import cosmolopy.perturbation as cp
import scipy.integrate as integrate
import matplotlib.pyplot as plt
from cosmolopy.perturbation import fgrowth  
from scipy import interpolate
from tqdm.auto import tqdm
import camb
from camb import model, initialpower




###############################################################################
# Constant factor in the expression of angular power spectrum
###############################################################################
def constantfactor(redshift):
    return 9 * (H0/c)**3 * omegam0**2 
#------------------------------------------------------------------------------

###############################################################################
## Comoving distance between z = 0 and some redshift
###############################################################################
def distance(variable):
    return cd.angular_diameter_distance(variable, **cosmo)
#------------------------------------------------------------------------------

#########################################################
## Hubble ratio H(z)/H0
#######################################################
def hubble_ratio(variable):
    return (omegam0 * (1 + variable)**3 + omegal)**0.5
#----------------------------------------------------------

###############################################################################
## To calculate the angular power spectrum using the linear matter power spectrum
###############################################################################
def angpowspec_integrand_without_j(z, ell):
    dist = distance(z)
    return (1 - dist/chi_s[redshift])**2 * np.interp(ell/dist, PS,dPS) * (fgrowth(z, omegam0, unnormed=False))**2/ hubble_ratio(z)
#return (1 - distance(z)/chi_s[redshift])**2 * np.interp(ell/distance(z), PS,dPS) * (fgrowth(z, omegam0, unnormed=False))**2/ hubble_ratio(z)

def angpowspec_integration_without_j(ell):
    return integrate.quad(angpowspec_integrand_without_j, 0, redshift, args = (ell, ))[0]
#------------------------------------------------------------------------------

###############################################################################
# Constants
###############################################################################

omegam0 = 0.315
omegal = 0.685
c = 3 * 10**8
H0 = 67.3 * 1000
cosmo = {'omega_M_0': omegam0, 'omega_lambda_0': omegal, 'omega_k_0': 0.0, 'h': 0.673}
C_l = 1.6*10**(-16)
delta_l = 36
f_sky = 0.2
l_plot_low_limit = 10
l_plot_upp_limit = 550
err_stepsize = 36
n_err_points = 1 + int((l_plot_upp_limit - l_plot_low_limit)/err_stepsize)
mass_moment_1 = 0.3
mass_moment_2 = 0.21
mass_moment_3 = 0.357
mass_moment_4 = 46.64
j_low_limit = 1
j_upp_limit = 2
j_max = 126
two_pi_squared = 2 * 3.14 * 2 * 3.14
eta = 0
eta_D2_L = 5.94 * 10**12 / 10**eta
redshift = 2
l_max = 600

nz = 100
kmax = 10
pars = camb.CAMBparams()
pars.set_cosmology(H0=70, ombh2=0.0224, omch2=0.120)
pars.InitPower.set_params(As=2.46e-9, ns=0.965)
pars.set_for_lmax(2500, lens_potential_accuracy=1);

results = camb.get_background(pars)
chistar = results.conformal_time(0)- results.tau_maxvis
chis = np.linspace(0,chistar,nz)
zs=results.redshift_at_comoving_radial_distance(chis)
dchis = (chis[2:]-chis[:-2])/2
chis = chis[1:-1]
zs = zs[1:-1]
PK = camb.get_matter_power_interpolator(pars, nonlinear=True,
    hubble_units=False, k_hunit=False, kmax=kmax,
    var1=model.Transfer_Weyl,var2=model.Transfer_Weyl, zmax=zs[-1])

#------------------------------------------------------------------------------

###############################################################################
# Arrays
###############################################################################
chi_s = np.zeros(11)
fgrow = np.zeros(11)
angpowspec_without_j_error_bar = np.zeros(n_err_points)
L_array = np.arange(0, l_plot_upp_limit)

eta_array = [0]
x_junk = np.zeros(l_max)
y_junk = np.zeros(l_max)
N_L = np.zeros(n_err_points)

noise_denominator_sum = np.zeros(n_err_points)
N0_sum = np.zeros(n_err_points)
N1_sum = np.zeros(n_err_points)
N2_sum = np.zeros(n_err_points)
N3_sum = np.zeros(n_err_points)

angpowspec_without_j = np.zeros(int(2**0.5 * l_max))
angpowspec_without_j_signal_in_final_plot = np.zeros(l_plot_upp_limit)
angpowspec_with_j = np.zeros((int(2**0.5 * l_max), j_upp_limit))
N4_array = np.zeros(n_err_points)
delta_C_L = np.zeros(n_err_points)
#------------------------------------------------------------------------------

###############################################################################
# CAMB linear power spectrum
###############################################################################
PS,dPS = np.loadtxt("/home/dyskun/Documents/Utility/Academics/Cosmology_project/C2SNR/Pow_spec_test_code/Data_files/CAMB_linear_update_1.txt", unpack=True)
#----------------------------------------------------------------------------

plt.subplots()

###############################################################################
# Plot from Pourtsidou et al. 2014 (with error bars)
###############################################################################
x_2 = np.zeros(50)
y_2 = np.zeros(50)
dxl_2 = np.zeros(50)
dxh_2 = np.zeros(50)
dyl_2 = np.zeros(50)
dyh_2 = np.zeros(50)
x_2, y_2, dxl_2, dxh_2, dyl_2, dyh_2 = np.loadtxt("/home/dyskun/Documents/Utility/Academics/Cosmology_project/C2SNR/Pow_spec_test_code/Data_files/pourtsidou_xyscan_z_2_no_errors.txt", unpack=True)

xplot_2 = np.arange(10, x_2[int(np.size(x_2))-1], x_2[int(np.size(x_2))-1]/2000)
tck_2 = interpolate.splrep(x_2,y_2, s=0)
tckerr_2 = interpolate.splrep(x_2,dyh_2,s=0)
yploterr_2 = interpolate.splev(xplot_2, tckerr_2, der=0)
yplot_2 = interpolate.splev(xplot_2, tck_2, der=0)
plt.errorbar(xplot_2,yplot_2, yerr=yploterr_2,color='black', ecolor='yellow', label='Pourtsidou et al. 2014 (z=2)')
#------------------------------------------------------------------------------

###############################################################################
# Plot from this work
###############################################################################
# Comoving distance between z = 0 and z = source redshift
chi_s[redshift] = cd.comoving_distance(redshift, **cosmo)

for L in tqdm(range(1, int(l_plot_upp_limit))):
    angpowspec_without_j[L] = constantfactor(redshift) * angpowspec_integration_without_j(L) / (2 * 3.14)

plt.plot(L_array[l_plot_low_limit:l_plot_upp_limit], angpowspec_without_j[l_plot_low_limit:l_plot_upp_limit], color='blue', label='This work (z = {})'.format(redshift))


#print(constantfactor(redshift) * angpowspec_integration_without_j(18) / (18 * 19))
#print(constantfactor(redshift) * angpowspec_integration_without_j(18) / (2 * 3.14))

plt.xlabel('L')
plt.ylabel(r'$C_{L} L(L+1)/2\pi$')
plt.suptitle("Angular Power Spectrum")
plt.xscale("log")
plt.yscale("log")
plt.xlim(l_plot_low_limit, l_plot_upp_limit)
plt.legend()
plt.ylim(1E-9,1E-7)
#plt.savefig("./J_plots/gaussian_plus_poisson_full_plot_integration_over_redshift__j_upp_limit_{}_lmax_{}_eta_{}_trial_after_lambda_corrections.pdf".format(j_upp_limit - 1, l_max, eta))
plt.show()
#------------------------------------------------------------------------------
