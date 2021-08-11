import matplotlib.pyplot as plt

def plot_local_ouliter_factor(names, segments, corupt_points, clear_points):
    """
    пострение графика визвуально отоброажающего методов локального выброса и метода тьюки для двух измерений

    Args:
         names: название выборок
         segments: границы графика
         corupt_points: значения выброса
         clear_points: нормальные значение
    Returns:
         фигура matplotlib с нарисованным графиком
    """
    fig = plt.figure()
    tuple_plot = plt.subplot2grid((3, 3), (0, 1), rowspan=2, colspan=2)
    cercle_plot = plt.subplot2grid((3, 3), (2, 0))
    first_boxplot = plt.subplot2grid((3, 3), (0, 0), rowspan=2, sharey=tuple_plot)
    second_bocplot = plt.subplot2grid((3, 3), (2, 1), colspan=2, sharex=tuple_plot)

    plt.setp(tuple_plot.get_xticklabels(), visible=False)
    plt.setp(tuple_plot.get_yticklabels(), visible=False)

    tuple_plot.set_xlabel(names[0])
    tuple_plot.set_ylabel(names[1])

    tuple_plot.set_xlim(segments[0])
    tuple_plot.set_ylim(segments[1])

    cercle_plot.set_xticks([])
    cercle_plot.set_yticks([])

    plt.setp(first_boxplot.get_xticklabels(), visible=False)
    plt.setp(second_bocplot.get_yticklabels(), visible=False)

    cercle_plot.pie([len(corupt_points[0]), len(clear_points[0])],
                    autopct=lambda pct: str(round(pct, 2)) + '%',
                    textprops=dict(color="gray"), colors=['r', 'b'])

    first_boxplot.boxplot(corupt_points[1] + clear_points[1])
    second_bocplot.boxplot( corupt_points[0] + clear_points[0], vert=False)

    tuple_plot.plot(corupt_points[0], corupt_points[1], '.r', alpha=0.2)
    tuple_plot.plot(clear_points[0], clear_points[1], '.b', alpha=0.2)

    return fig

def drow_3d_plot(names, segments, corupt_points, clear_points):
    """
    пострение графика визвуально отоброажающего методов локального выброса  для трех измерений

    Args:
         names: название выборок
         segments: границы графика
         corupt_points: точки выброса
         clear_points: нормальные точки
    Returns:
          фигура matplotlib с нарисованным графиком
    """
    fig = plt.figure(figsize=(15, 15))
    ax =  fig.add_subplot(111, projection='3d')

    ax.set_xlim(segments[0])
    ax.set_ylim(segments[1])
    ax.set_zlim(segments[2])

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
