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


# modeling_keys = {'Id': 'DrainI (after 20 months)', 'Vgs': 'GateV (after 20 months)'}


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


def compute_diff_current(mu, Vgs, Vt, Cox, Cit, Cq, Vds, L, ksemi, tsemi):
    Cd = compute_cd(tsemi, ksemi)

    Cr = 1 + (Cq + Cit)/Cox

    coefficent = q * mu * calculate_N2D() / L
    term1 = np.log(np.exp((Vgs - Vt)/(Cr*kT)) + 1)
    term2 = np.log(np.exp((Vgs - Vt - Vds) / (Cr * kT)) + 1)

    Idiff = coefficent * (term1 - term2)

    return Idiff


def compute_cd(tsemi, ksemi):
    return compute_cox(tsemi, ksemi)


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

    return interp.UnivariateSpline(x, y, k=5)

    # a, b, c, d = np.polyfit(x, y, 3)
    #
    # return lambda x: d + a*x**3 + b*x**2 + c*x
    #
    # def fit(x, a, b, c, d, e):
    #     return a * np.exp(b * x) + c * np.exp(d * x) + e
    #
    # popt, pcov = opt.curve_fit(fit, x, y, p0=(1.0,1.0,1.0,1.0,1.0), maxfev=10000)
    # new_fit = lambda x: fit(x, *popt)
    # return new_fit


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


def fit_data(data, modeling_keys, cq_extraction_keys, Dits, Eits, Vt, mu, L, vsat, Vds, diff_vt_shift, ksemi, tsemi):

    Cox = compute_cox(tox, k)

    Ef = np.array([calculate_ef(Dits, Eits, Vgs, Vt, 2.0, Cox) for Vgs in data[modeling_keys['Vgs']]])

    Cq = extract_Cq(data[cq_extraction_keys['Id']], data[cq_extraction_keys['Vgs']], Cox)

    # alpha = np.exp((Ef)/kT)
    #
    # adjusted_Cq = q**2 * calculate_N2D() * alpha / ((1 + alpha) * kT)

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
        betas = [np.exp(-Eit / kT) for Eit in Eits]

        n_mos2 = calculate_N2D() * np.log(1 + alpha)

        cit = sum([q * Dit * alpha * beta / (kT * (alpha + beta)) for Dit, beta in zip(Dits, betas)])

        Idiff.append(compute_diff_current(mu=mu, Vgs=Vgs, Vt=Vt + diff_vt_shift, Cq=cq, Cox=Cox, Cit=cit,
                                          L=L, Vds=Vds, ksemi=ksemi, tsemi=tsemi))

        Idrift.append(drift_current(Vgs=Vgs, Vt=Vt, Vds=Vds, Cox=Cox, L=L, mu=mu, vsat=vsat, n=n_mos2))

        current.append(Idrift[-1] + Idiff[-1])
        # current.append(np.average(Idrift[-1], Idiff[-1])


    return np.array(current), Idrift, Idiff, data


def previous_run():

    params = {'Dits': [0e12, 5e12],
              'Eits': [-0.1, 0.05], 'Vt': 20, 'L': 1,
              'mu': 35, 'vsat': 4e6, 'Vds': 1,
              'diff_vt_shift': -15, 'ksemi': 4, 'tsemi': 1.2e-7}
    # import the data
    modeling_keys = {'Id': 'DrainI2', 'Vgs': 'GateV2'}
    cq_extraction_keys = {'Id': 'DrainI1', 'Vgs': 'GateV1'}
    tmp = csv.DictReader(open('./WS2 AlOx Doping.csv', 'r'))
    input_data = {name: [] for name in tmp.fieldnames}
    for row in tmp:
        for key, entry in row.items():
            try:
                input_data[key].append(float(entry))
            except ValueError:
                pass
    # convert all data to np.ndarray
    input_data = {name: np.array(entry) for name, entry in input_data.items()}


    current, Idrift, Idiff, data = fit_data(input_data, modeling_keys, cq_extraction_keys, **params)

    Vgs = data[modeling_keys['Vgs']]

    plt.yscale('log')
    plt.plot(Vgs, Idrift, 'b')
    plt.plot(Vgs, Idiff, 'y')
    plt.scatter(data[modeling_keys['Vgs']], data[modeling_keys['Id']])
    plt.scatter(data[cq_extraction_keys['Vgs']], data[cq_extraction_keys['Id']])
    plt.plot(data[modeling_keys['Vgs']], current, 'r')
    plt.ylim([1e-10, 1e-3])
    plt.show()


def optimize_func(input_data, modeling_keys, cq_extraction_keys, params):
    def optfunc(x):
        dits = x[0:2]
        params['Dits'] = dits * 1e12
        params['diff_vt_shift'] = x[4]
        params['Eits'] = x[2:4]
        current, Idrift, Idiff, data = fit_data(input_data, modeling_keys, cq_extraction_keys, **params)

        first = np.abs(np.log(np.abs(data[modeling_keys['Id']][:60])))
        second = np.abs(np.log(current[:60]))
        loss = np.abs(np.average((first - second) / second))
        # Vgs = data[modeling_keys['Vgs']]
        # plt.yscale('log')
        # # plt.plot(Vgs, Idrift, 'b')
        # # plt.plot(Vgs, Idiff, 'y')
        # plt.scatter(Vgs, data[modeling_keys['Id']])
        # # plt.scatter(data[cq_extraction_keys['Vgs']], data[cq_extraction_keys['Id']], label='extraction')
        # plt.plot(Vgs, current, 'r')
        # plt.legend()
        # plt.ylim([1e-12, 1e-3])
        # plt.show()
        return loss

    init_dits = params['Dits']/1e12
    init_eit = params['Eits']
    vt = [params['diff_vt_shift']]

    result = opt.minimize(optfunc, np.concatenate((init_dits, init_eit, vt)), bounds=[(0, 7), (0, 7), (-0.15, 0.1), (0.0, 0.2), (-25, 10)])
    dits = result['x'][0:2]
    vt = result['x'][4]
    params['Dits'] = dits * 1e12
    params['Eits'] = result['x'][2:4]
    params['diff_vt_shift'] = vt
    print('Dits: {0} \n Eits: {1} \n Vt: {2}'.format(params['Dits'], params['Eits'], vt))
    current, Idrift, Idiff, data = fit_data(input_data, modeling_keys, cq_extraction_keys, **params)
    return current, Idrift, Idiff, data



def new_data():

    #TODO: need to automate diff_vt_shift extraction

    params = {'Dits': np.array([0e12, 2e12]),
              'Eits': [-0.0, 0.2], 'Vt': 20, 'L': 1,
              'mu': 35, 'vsat': 4e6, 'Vds': 0.2,
              'diff_vt_shift': -15, 'ksemi': 4, 'tsemi': 1.2e-7}
    # import the data
    # cq_extraction_keys = {'Id': 'DrainI Before AlOx', 'Vgs': 'GateV Before AlOx'}
    # modeling_keys = {'Id': 'DrainI after 21 months', 'Vgs': 'GateV after 21 months'}
    modeling_keys = {'Id': 'DrainI After AlOx', 'Vgs': 'GateV After AlOx'}

    cq_extraction_keys = {'Id': 'DrainI After AlOx', 'Vgs': 'GateV After AlOx'}
    tmp = csv.DictReader(open('./ara_data/WS2 AlOx Doping.csv', 'r'))
    input_data = {name: [] for name in tmp.fieldnames}
    for row in tmp:
        for key, entry in row.items():
            try:
                input_data[key].append(float(entry))
            except ValueError:
                pass
    # convert all data to np.ndarray
    input_data = {name: np.array(entry) for name, entry in input_data.items()}

    current, Idrift, Idiff, data = optimize_func(input_data, modeling_keys, cq_extraction_keys, params)

    # current, Idrift, Idiff, data = fit_data(input_data, modeling_keys, cq_extraction_keys, **params)

    Vgs = data[modeling_keys['Vgs']]

    plt.yscale('log')
    # plt.plot(Vgs, Idrift, 'b')
    # plt.plot(Vgs, Idiff, 'y')
    plt.scatter(Vgs, data[modeling_keys['Id']])
    plt.scatter(data[cq_extraction_keys['Vgs']], data[cq_extraction_keys['Id']], label='extraction')
    plt.plot(Vgs, current, 'r')
    plt.legend()
    plt.ylim([1e-12, 1e-3])
    plt.show()



if __name__ == "__main__":

    previous_run()
    # new_data()
    # modeling_keys = {'Id': 'DrainI2', 'Vgs': 'GateV2'}
    # cq_extraction_keys = {'Id': 'DrainI1', 'Vgs': 'GateV1'}
    # tmp = csv.DictReader(open('./WS2 AlOx Doping.csv', 'r'))

    # data = {name: [] for name in tmp.fieldnames}
    # for row in tmp:
    #     for key, entry in row.items():
    #         try:
    #             data[key].append(float(entry))
    #         except ValueError:
    #             pass
    # # convert all data to np.ndarray
    # data = {name: np.array(entry) for name, entry in data.items()}
    #
    # Cox = compute_cox(tox, k)
    #
    # Ef = np.array([calculate_ef(Dits, Eits, Vgs, Vt, 2.0, Cox) for Vgs in data[modeling_keys['Vgs']]])
    #
    # Cq = extract_Cq(data[cq_extraction_keys['Id']], data[cq_extraction_keys['Vgs']], Cox)
    #
    # # alpha = np.exp((Ef)/kT)
    # #
    # # adjusted_Cq = q**2 * calculate_N2D() * alpha / ((1 + alpha) * kT)
    # diff_vt_shift = -11
    #
    # Vgs_cq_shifted = data[cq_extraction_keys['Vgs']] + diff_vt_shift
    #
    # current = []
    # Idiff = []
    # Idrift = []
    # for i_Vg in range(len(data[modeling_keys['Vgs']])):
    #     Vgs = data[modeling_keys['Vgs']][i_Vg]
    #
    #
    #
    #     # there is a size isue with Cq. Find the Cq with the closest Vgs value after the diff vt shift
    #     i_cq_vg = np.argmin(np.abs(Vgs_cq_shifted - Vgs))
    #     cq = Cq[i_cq_vg]
    #
    #     alpha = np.exp((Ef[i_Vg]) / kT)
    #     betas = [np.exp(-Eit/kT) for Eit in Eits]
    #
    #     n_mos2 = calculate_N2D() * np.log(1 + alpha)
    #
    #     cit = sum([q*Dit*alpha*beta / (kT * (alpha+beta)) for Dit, beta in zip(Dits, betas)])
    #
    #     Idiff.append(compute_diff_current(mu=mu, Vgs=Vgs, Vt=Vt+diff_vt_shift, Cq=cq, Cox=Cox, Cit=cit, L=L, Vds=Vds))
    #
    #     Idrift.append(drift_current(Vgs=Vgs, Vt=Vt, Vds=Vds, Cox=Cox, L=L, mu=mu, vsat=vsat, n=n_mos2))
    #
    #     current.append(Idrift[-1] + Idiff[-1])

    # plt.plot(Vgs, Idiff)

    # plt.plot(data[modeling_keys['Vgs']], Idrift, 'r')
    # plt.scatter(data[modeling_keys['Vgs']], data[modeling_keys['Id']])
    # plt.plot(data[modeling_keys['Vgs']], current, 'r')
    # plt.show()
