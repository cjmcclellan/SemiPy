"""
Some simple plotting functions
"""
import matplotlib.pyplot as plt


def create_scatter_plot(x_data, y_data, scale='log', fig=None, show=False, autoscale=False):
    if x_data is None:
        x_data = range(0, len(y_data))
    no_fig = fig
    if fig is None:
        fig = plt.figure()
    if scale == 'log':
        ax = plt.gca()
        ax.set_yscale('log')
        ax.set_ylim([1e-9, 1e-2])
    plt.scatter(x_data, y_data)
    if autoscale:
        ax = plt.gca()
        ax.set_ylim([min(y_data)*0.95, max(y_data)*1.1])
    if show:
        plt.show()
    return fig
