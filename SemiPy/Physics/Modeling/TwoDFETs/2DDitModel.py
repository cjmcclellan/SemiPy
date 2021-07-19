import numpy as np
import csv
import matplotlib.pyplot as plt
import scipy.optimize as opt
import scipy.interpolate as interp

q = 1.6e-19
epsilon = 8.85e-14
kT = 8.617e-5*300
kbolt_j = 1.38e-23
hbar = 1.054e-34

m0 = 9.11e-31
meff = 0.48*m0
gk = 2
T = 300
DOS_Factor = 1

tox = 9e-6 # 90 nm in cm
k = 3.9 # SiO2

Dits = [1e12, 2e12]
Eits = [-0.05, 0.25]
Vt = 30

L = 1  # in um
mu = 30
vsat = 4e6
Vds = 0.5

# modeling_keys = {'Id': 'DrainI (after 20 months)', 'Vgs': 'GateV (after 20 months)'}
modeling_keys = {'Id': 'DrainI2', 'Vgs': 'GateV2'}

cq_extraction_keys = {'Id': 'DrainI1', 'Vgs': 'GateV1'}


def compute_cox(t, k):
    return k * epsilon / t


def compute_n(Cox, Vgs, Vt, Vds):
    return Cox * (Vgs - Vt - Vds/2)/q


def compute_velocity(mu, Vds, L, vsat, gamma=5):
    F = Vds / L
    return mu * F / ((1 + (mu * F / vsat)**gamma)**1/gamma)


def drift_current(Vgs, Vt, Vds, Cox, L, mu, vsat, n=None):
    if n is None:
        n = compute_n(Cox, Vgs, Vt, Vds)
    return compute_velocity(mu, Vds, L, vsat) * n * q


def compute_diff_current(mu, Vgs, Vt, Cox, Cit, Cq, Vds, L):

    Cr = 1 + (Cq + Cit)/Cox

    coefficent = q * mu * calculate_N2D() / L
    term1 = np.log(np.exp((Vgs - Vt)/(Cr*kT)) + 1)
    term2 = np.log(np.exp((Vgs - Vt - Vds) / (Cr * kT)) + 1)

    Idiff = coefficent * (term1 - term2)

    return Idiff


def extract_Cq(Id, Vgs, Cox, Vt=35, plot=False):
    log_id = np.log10(np.abs(Id))

    fit = curve_fit(Vgs, log_id)
    fit_log_id = fit(Vgs)

    if plot:
        plt.plot(Vgs, fit_log_id)
        plt.plot(Vgs, log_id)
        plt.show()
    # plot_idVgs(fit_id, Vgs, log=False)

    ss = np.diff(Vgs) / np.diff(fit_log_id)

    if plot:
        plt.plot(Vgs[:-1], ss)
        plt.show()

    # now extract Cq
    Cq_max = q * calculate_N2D()/kT

    Cq = (ss/(np.log(10) * kT) - 1) * Cox

    Cq[Vgs[:-1] > Vt] = Cq_max

    # append one Cq_max at the end to make the shape the same
    Cq = np.append(Cq, Cq_max)

    if plot:
        plt.plot(Vgs, Cq)
        plt.show()

    return Cq


def calculate_N2D():
    return (kbolt_j * T * gk * meff / (np.pi * hbar ** 2) + kbolt_j * T * 6 * meff / (np.pi * hbar ** 2) * np.exp(-0.11 / kT)) * 1e-4 * DOS_Factor;


def smooth(y, box_pts):
    box = np.ones(box_pts)/box_pts
    y_smooth = np.convolve(y, box, mode='same')
    return y_smooth


def curve_fit(x, y):
    # plot_idvg(np.log10(np.abs(y)), x, log=False)

    # return interp.UnivariateSpline(x, y)

    # a, b, c, d = np.polyfit(x, y, 3)
    #
    # return lambda x: d + a*x**3 + b*x**2 + c*x
    #
    def fit(x, a, b, c, d, e):
        return a * np.exp(b * x) + c * np.exp(d * x) + e

    popt, pcov = opt.curve_fit(fit, x, y, p0=(1.0,1.0,1.0,1.0,1.0), maxfev=10000)
    new_fit = lambda x: fit(x, *popt)
    return new_fit

def plot_idvg(id, Vgs, log=True):
    plt.plot(Vgs, id)
    if log:
        plt.yscale('log')
    plt.show()


def calculate_ef(Dits, Eits, Vgs, Vt, Vds, Cox):

    n_gate = compute_n(Cox, Vgs, Vt, Vds)
    N2d = calculate_N2D()

    def solve(Ef):
        result = n_gate - N2d * np.log(1 + np.exp(Ef/kT))

        for Dit, Eit in zip(Dits, Eits):
            result = result + compute_nit(Dit, Eit, Ef)

        return result

    Ef = opt.fsolve(solve, [0.1])

    return Ef[0]


def compute_nit(Dit, Eit, Ef):
    return Dit / (1 + np.exp(-(Eit-Ef)/kT))


if __name__ == "__main__":

    # import the data

    tmp = csv.DictReader(open('/home/connor/Documents/Stanford_Projects/SemiPy/SemiPy/Physics/Modeling/TwoDFETs/WS2 AlOx Doping.csv', 'r'))
    data = {name: [] for name in tmp.fieldnames}
    for row in tmp:
        for key, entry in row.items():
            try:
                data[key].append(float(entry))
            except ValueError:
                pass
    # convert all data to np.ndarray
    data = {name: np.array(entry) for name, entry in data.items()}

    Cox = compute_cox(tox, k)

    Ef = np.array([calculate_ef(Dits, Eits, Vgs, Vt, 2.0, Cox) for Vgs in data[modeling_keys['Vgs']]])

    Cq = extract_Cq(data[cq_extraction_keys['Id']], data[cq_extraction_keys['Vgs']], Cox)

    # alpha = np.exp((Ef)/kT)
    #
    # adjusted_Cq = q**2 * calculate_N2D() * alpha / ((1 + alpha) * kT)
    diff_vt_shift = -45

    Vgs_cq_shifted = data[cq_extraction_keys['Vgs']] + diff_vt_shift

    current = []
    Idiff = []
    Idrift = []
    for i_Vg in range(len(data[modeling_keys['Vgs']])):
        Vgs = data[modeling_keys['Vgs']][i_Vg]



        # there is a size isue with Cq. Find the Cq with the closest Vgs value after the diff vt shift
        i_cq_vg = np.argmin(np.abs(Vgs_cq_shifted - Vgs))
        cq = Cq[i_cq_vg]

        alpha = np.exp((Ef[i_Vg]) / kT)
        betas = [np.exp(-Eit/kT) for Eit in Eits]

        n_mos2 = calculate_N2D() * np.log(1 + alpha)

        cit = sum([q*Dit*alpha*beta / (kT * (alpha+beta)) for Dit, beta in zip(Dits, betas)])

        Idiff.append(compute_diff_current(mu=mu, Vgs=Vgs, Vt=Vt+diff_vt_shift, Cq=cq, Cox=Cox, Cit=cit, L=L, Vds=Vds))

        Idrift.append(drift_current(Vgs=Vgs, Vt=Vt, Vds=Vds, Cox=Cox, L=L, mu=mu, vsat=vsat, n=n_mos2))

        current.append(Idrift[-1] + Idiff[-1])

    # plt.plot(data[modeling_keys['Vgs']], Idiff)
    plt.yscale('log')
    # plt.plot(data[modeling_keys['Vgs']], Idrift, 'r')
    plt.scatter(data[modeling_keys['Vgs']], data[modeling_keys['Id']])
    plt.plot(data[modeling_keys['Vgs']], current, 'r')
    plt.ylim([1e-10, 1e-3])
    plt.show()

