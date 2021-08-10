import matplotlib.pyplot as plt


def plot_local_ouliter_factor(names, segmants, corupt_points, clear_points):
    fig = plt.figure()
    tuple_plot = plt.subplot2grid((3, 3), (0, 1), rowspan=2, colspan=2)
    cercle_plot = plt.subplot2grid((3, 3), (2, 0))
    first_boxplot = plt.subplot2grid((3, 3), (0, 0), rowspan=2, sharey=tuple_plot)
    second_bocplot = plt.subplot2grid((3, 3), (2, 1), colspan=2, sharex=tuple_plot)

    plt.setp(tuple_plot.get_xticklabels(), visible=False)
    plt.setp(tuple_plot.get_yticklabels(), visible=False)

    tuple_plot.set_xlabel(names[0])
    tuple_plot.set_ylabel(names[1])


    tuple_plot.set_xlim(segmants[0])
    tuple_plot.set_ylim(segmants[1])

    cercle_plot.set_xticks([])
    cercle_plot.set_yticks([])

    plt.setp(first_boxplot.get_xticklabels(), visible=False)
    plt.setp(second_bocplot.get_yticklabels(), visible=False)

    cercle_plot.pie([len(corupt_points), len(corupt_points)],
                    autopct=lambda pct: str(round(pct, 2)) + '%',
                    textprops=dict(color="gray"), colors=['r', 'b'])

    first_boxplot.boxplot( [point[0] for point in corupt_points + clear_points])
    second_bocplot.boxplot([point[1] for point in corupt_points + clear_points])

    tuple_plot.plot([point[0] for point in corupt_points], [point[1] for point in corupt_points], '.r', alpha=0.2)
    tuple_plot.plot([point[0] for point in clear_points], [point[1] for point in clear_points], '.b', alpha=0.2)

    return fig

def drow_3d_plot(names, segmants,corupt_points, clear_points):
    fig = plt.figure(figsize=(15, 15))
    ax =  fig.add_subplot(111, projection='3d')

    ax.set_xlim(segmants[0])
    ax.set_ylim(segmants[1])
    ax.set_zlim(segmants[2])

    ax.set_xlabel(names[0])
    ax.set_ylabel(names[1])
    ax.set_zlabel(names[2])

    ax.plot([point[0] for point in corupt_points],
            [point[1] for point in corupt_points],
            [point[2] for point in corupt_points], '.r', alpha=0.2)
    ax.plot([point[0] for point in clear_points],
            [point[1] for point in clear_points],
            [point[2] for point in clear_points],'.b', alpha=0.2)

    return fig
