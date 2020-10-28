import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import matplotlib
import matplotlib.gridspec as gridspec
import xlrd

def derive_VC_data(file_name, test_name):
    df = pd.read_excel('{}'.format(file_name), sheet_name=test_name)    # Can also index sheet by name or fetch all sheets
    penetration = df['PENETRATION']
    current = df['CURRENT']
    penetration_rate = df['MOV_AVG+EXP_RATE']
    return penetration, current, penetration_rate

def derive_VC_sinkage(file_name, test_name):
    df = pd.read_excel('{}'.format(file_name), sheet_name=test_name)    # Can also index sheet by name or fetch all sheets
    median_sinkage = np.median(df['ECHO'])
    df = df[(df['ECHO'] < 1.05*median_sinkage) & (df['ECHO'] > 0.95*median_sinkage)
            & (df['ECHO'] > 0.4) & (df['ECHO'] > 0.4) & (df['ECHO'] < 0.6)]
    sinkage_penetration = df['PENETRATION']
    sinkage_echosounder = df['ECHO']
    # time = df['TIME']
    return sinkage_penetration, sinkage_echosounder #, time

def derive_for_interpolation_PR(file_name, test_name, start, lower_bound_PR):
    df = pd.read_excel('{}'.format(file_name), sheet_name=test_name, skiprows=range(1, start+1)) # can also index sheet by name or fetch all sheets
    df = df[df['PENETRATION'] > lower_bound_PR]
    penetration = df['PENETRATION']
    penetration_rate = df['MOV_AVG+EXP_RATE']
    return penetration, penetration_rate

def derive_for_interpolation_MC(file_name, test_name, start, lower_bound_MC, relative_low, relative_high, abs_low_MC, abs_high_MC):
    df = pd.read_excel('{}'.format(file_name), sheet_name=test_name, skiprows=range(1, start+1)) # can also index sheet by name or fetch all sheets
    # median_current = np.median(df['CURRENT'])
    median_current = np.mean(df['CURRENT'])
    df = df[(df['CURRENT'] < relative_high*median_current) & (df['CURRENT'] > relative_low*median_current)
            & (df['CURRENT'] > lower_bound_MC) & (df['CURRENT'] > abs_low_MC) & (df['CURRENT'] < abs_high_MC)]
    penetration = df['PENETRATION']
    current = df['CURRENT']
    return penetration, current

def filtering(x, option, diff_perc, diff_value, abs_low_MC, abs_high_MC):
    median = np.median(x[:, 1])
    dummy = np.array([], dtype=np.float64)
    if option == 1:
        for i in range(0, len(x)):
            if x[i, 1] < (1 - diff_perc) * x[i - 1, 1] \
                    or x[i, 1] > (1 + diff_perc) * x[i - 1, 1] \
                    or x[i, 1] < x[i - 1, 1] - diff_value \
                    or x[i, 1] > x[i - 1, 1] + diff_value \
                    or x[i, 1] < abs_low_MC \
                    or x[i, 1] > abs_high_MC:
                dummy = np.append(dummy, i)
            else:
                pass
    if option == 2:
        for i in range(0, len(x)):
            if x[i, 1] < (1 - diff_perc) * x[i - 1, 1] \
                    or x[i, 1] > (1 + diff_perc) * x[i - 1, 1] \
                    or x[i, 1] < median - diff_value \
                    or x[i, 1] > median + diff_value:
                dummy = np.append(dummy, i)
            else:
                pass
    filtered_x = np.delete(x, dummy, 0)
    return filtered_x

def print_MC_PR(test_name, penetration, current, penetration_rate, xy_line_rate, xy_line_current, d_p_MC, d_v_MC, d_p_PR, d_v_PR, abs_low_MC, abs_high_MC):
    fig, ax1 = plt.subplots(figsize=(8.27, 11.69))

    color = 'tab:red'
    ax1.scatter(current, penetration, label='Motor Current', color=color, alpha=0.2)
    xy_line_current = filtering(xy_line_current, 1, d_p_MC, d_v_MC, abs_low_MC, abs_high_MC)
    ax1.plot(xy_line_current[:, 1], xy_line_current[:, 0], c=color)
    ax1.set_xlabel('Motor Current [A]', color=color)
    ax1.set_ylabel('Penetration depth [m]')
    ax1.tick_params(axis='x', labelcolor=color)

    ax2 = ax1.twiny()
    color = 'tab:blue'
    ax2.scatter(penetration_rate, penetration, label='Penetration rate', color=color, alpha=0.2)
    xy_line_rate = filtering(xy_line_rate, 2, d_p_PR, d_v_PR, abs_low_MC, abs_high_MC)
    ax2.plot(xy_line_rate[:, 1], xy_line_rate[:, 0], c=color)
    ax2.set_xlabel('Penetration Rate [m/s]', color=color)
    ax2.tick_params(axis='x', labelcolor=color)

    plottitle = 'Evolution of motor current and penetration rate during test {}'.format(test_name)
    ax1.grid(linestyle=':', linewidth='1')
    plt.title(plottitle)
    fig.tight_layout()  # otherwise the right y-label is slightly clipped
    ax1.set_ylim(0, 6)
    ax1.set_xlim(0, 50)
    min_rate = np.min(penetration_rate)
    max_rate = np.max(penetration_rate)
    ax2.set_xlim(max_rate, min_rate)
    plt.gca().invert_yaxis()
    plt.savefig('{}.pdf'.format(test_name))
    plt.close('all')

def print_sinkage(test_name, sinkage_penetration, sinkage_echosounder):
    fig, ax = plt.subplots(figsize=(8.27, 11.69))

    color = 'tab:blue'
    ax.scatter(100*(0.55-sinkage_echosounder), sinkage_penetration, label='Sinkage', color=color, alpha=0.2)
    ax.set_xlabel('Sinkage [mm]', color=color)
    ax.set_ylabel('Penetration depth [m]')
    ax.tick_params(axis='x', labelcolor=color)

    plottitle = 'Evolution of sinkage during test {}'.format(test_name)
    ax.grid(linestyle=':', linewidth='1')
    plt.title(plottitle)
    fig.tight_layout()  # otherwise the right y-label is slightly clipped
    ax.set_ylim(0, 6)
    plt.gca().invert_yaxis()
    plt.savefig('Sinkage_{}.pdf'.format(test_name))
    plt.close('all')

def print_both(test_name, sinkage_penetration, sinkage_echosounder, penetration, current, penetration_rate, xy_line_rate, xy_line_current, d_p_MC, d_v_MC, d_p_PR, d_v_PR, abs_low_MC, abs_high_MC):
    fig = plt.figure(1)
    gridspec.GridSpec(3, 1)     # Set up subplot grid

    # Motor Current and Penetration Rate Plot
    ax1 = plt.subplot2grid((3, 1), (0, 0), colspan=1, rowspan=2)
    plottitle = 'Evolution of motor current, penetration rate and sinkage during test {}'.format(test_name)
    plt.title(plottitle)
    color = 'tab:red'
    ax1.scatter(current, penetration, label='Motor Current', color=color, alpha=0.2)
    xy_line_current = filtering(xy_line_current, 1, d_p_MC, d_v_MC, abs_low_MC, abs_high_MC)
    ax1.plot(xy_line_current[:, 1], xy_line_current[:, 0], c=color)
    ax1.set_xlabel('Motor Current [A]', color=color)
    ax1.set_ylabel('Penetration depth [m]')
    ax1.tick_params(axis='x', labelcolor=color)

    ax2 = ax1.twiny()
    color = 'tab:blue'
    ax2.scatter(penetration_rate, penetration, label='Penetration rate', color=color, alpha=0.2)
    xy_line_rate = filtering(xy_line_rate, 2, d_p_PR, d_v_PR, abs_low_MC, abs_high_MC)
    ax2.plot(xy_line_rate[:, 1], xy_line_rate[:, 0], c=color)
    ax2.set_xlabel('Penetration Rate [m/s]', color=color)
    ax2.tick_params(axis='x', labelcolor=color)

    ax1.grid(linestyle=':', linewidth='1')
    ax1.set_ylim(0, 6)
    ax1.set_xlim(0, 50)
    min_rate = np.min(penetration_rate)
    max_rate = np.max(penetration_rate)
    ax2.set_xlim(max_rate, min_rate)
    plt.gca().invert_yaxis()

    # Sinkage plot
    ax3 = plt.subplot2grid((3, 1), (2, 0), colspan=1, rowspan=1)
    color = 'tab:green'
    ax3.scatter(1000 * (0.55 - sinkage_echosounder), sinkage_penetration, label='Sinkage', color=color, alpha=0.2)
    ax3.set_xlabel('Sinkage [mm]', color=color)
    ax3.set_ylabel('Penetration depth [m]')
    ax3.tick_params(axis='x', labelcolor=color)

    ax3.grid(linestyle=':', linewidth='1')
    ax3.set_xlim(-50, 150)
    ax3.set_ylim(0, 6)
    plt.gca().invert_yaxis()

    # Fit subplots and save fig
    # fig.tight_layout()
    fig.set_size_inches(w=8.27, h=11.69)
    fig.savefig('Sinkage_{}.pdf'.format(test_name))
    plt.close('all')

def dawaj_linie(penetration, value, degrees):
    linialista = list(zip(penetration, value))
    liniaarray = np.asarray(linialista)
    esolinia = estimating_lines(liniaarray, degrees)
    return esolinia

def estimating_lines(a1, degrees):
    # Find the range of x values in a1
    min_a1_x, max_a1_x = min(a1[:, 0]), max(a1[:, 0])
    # Create an evenly spaced array that ranges from the minimum to the maximum
    # I used 1000 elements, but you can use more or fewer.
    # This will be used as your new x coordinates
    new_a1_x = np.linspace(min_a1_x, max_a1_x, 1000)
    # Fit a XXXth degree polynomial to your data 0 - set XXX as high as possible, but lower than convergence (LS) error
    a1_coefs = np.polyfit(a1[:, 0], a1[:, 1], degrees)
    # Get your new y coordinates from the coefficients of the above polynomial
    new_a1_y = np.polyval(a1_coefs, new_a1_x)

    new_a1 = list(zip(new_a1_x, new_a1_y))
    reversed_a1 = new_a1[::-1]
    new_a1 = np.asarray(reversed_a1)
    return new_a1