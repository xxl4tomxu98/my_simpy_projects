import sys
import simpy
import cv2
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import simulation

import simulation.statistics as stats
from simulation.roadnetwork import RoadNetwork
from simulation.simulation import Simulation
from simulation.siouxfalls import SiouxFalls

plt.style.use('ggplot')

def f(x):
    return int(x)


def main():
    #################################
    # initialize discrete event env #
    #################################
    env = simpy.Environment()  # use instant simulation
    # env = simpy.rt.RealtimeEnvironment(factor=1.)  # use real time simulation

    # initialize Sioux Falls network
    siouxfalls = SiouxFalls(0.0025)

    # create simulation enviromment
    img = np.zeros((900, 800, 3), dtype=np.uint8)
    sim = Simulation(env, img)

    # create Sioux Fall network by enumerating across all links
    for linkid, t0 in enumerate(siouxfalls.t0):

        # calculate length of link with sqrt((x1 - x2)^2 + (y1 - y2)^2)
        length = np.sqrt(
            np.power(siouxfalls.x1[linkid] - siouxfalls.x2[linkid], 2)
          + np.power(siouxfalls.y1[linkid] - siouxfalls.y2[linkid], 2)) / 600.
        mu = siouxfalls.mu[linkid]

        # assign nodeID to each link if check pass in node list
        for i, node in enumerate(siouxfalls.nodes):
            if linkid+1 in node:
                nodeID = i

        # assign turn ratio to each link
        turns = {}
        for j, turn in enumerate(siouxfalls.turns[linkid]):
            turns[j + 1] = turn

        # assign exit probability from last item in turn list ([-1])
        turns['exit'] = turns.pop(list(turns.keys())[-1])

        # generate coordinates of each link (for visualization)
        pt1 = (np.float32(siouxfalls.x1[linkid] / 600.),
               np.float32(siouxfalls.y1[linkid] / 600.))

        pt2 = (np.float32(siouxfalls.x2[linkid] / 600.),
               np.float32(siouxfalls.y2[linkid] / 600.))

        c = (pt1, pt2)

        # draw link on map
        sim.networkLines.append(c)

        # add link to sim.network
        sim.network.addLink(linkID=linkid+1, turns=turns,
                            type='link',  length=length,
                            t0=t0, MU=mu, nodeID=nodeID,
                            coordinates=c)

        # initialize car generation
        if linkid % 3 == 0:
            env.process(sim.source(10,
                                   LAMBDA=siouxfalls.flambda[linkid],
                                   linkid=linkid+1))

    # draw initial network
    for i in sim.networkLines:
        cv2.line(sim.img, (int(i[0][0]), int(i[0][1])), (int(i[1][0]), int(i[1][1])), (255, 255, 255), 2)

    for linkid in sim.network.links:
        loc = (0.25 * np.asarray(sim.network.links[linkid]['coordinates'][1]) +
               0.75 * np.asarray(sim.network.links[linkid]['coordinates'][0]))
        f2 = np.vectorize(f)
        cv2.putText(sim.img, str(linkid), tuple(f2(loc)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

    name = 'Sioux Falls Network'
    cv2.imshow(name, sim.img)

    # start visualization update process
    # frequency is the visualization poll rate, smaller = faster polling
    env.process(sim.visualization(frequency=0.2, name=name))

    # wait for keypress to start simulation
    print('press space to start')
    k = cv2.waitKey(0)
    if k == 27:
        sys.exit()

    # run simulation
    env.run()

    ######################################
    # simulation statistics and graphing #
    ######################################
    df = pd.DataFrame(sorted(sim.data, key=lambda x: x[3]),
                      columns=['carID', 'link', 'event', 'time', 'queue',
                               't_queue'])
    print(df)

    # cars statistics
    totalTravelTime = (df[['carID', 'time']].groupby(['carID']).max()
                       - df[['carID', 'time']].groupby(['carID']).min())
    totalTravelTime.columns = ['totalTravelTime']

    totalSegments = df.loc[df['event'] == 'arrival'][['carID', 'link']]
    totalSegments = totalSegments.groupby(['carID']).count()
    totalSegments.columns = ['totalSegments']

    meanWaitTime = df.loc[df['event'] == 'departure'][['carID', 't_queue']]
    meanWaitTime = meanWaitTime.groupby(['carID']).mean()
    meanWaitTime.columns = ['meanWaitTime']

    carStatistics = pd.concat([totalTravelTime, totalSegments, meanWaitTime],
                              axis=1)

    # links statistics
    stats.meanQueueLength(plt, df)
    plt.figure(2)

    for link in sim.network.links.keys():
        df2 = df.loc[(df['link'] == link) & (df['event'] != 'entry')]
        if df2.empty is False and df2['t_queue'].sum() > 0.:
            plt.plot(df2[['time']], df2[['queue']], label='link %s' % link)

    plt.title('Queueing Simulation')
    plt.ylabel('queue length')
    plt.xlabel('time (s)')
    plt.legend()
    plt.show()

    print('Press any key to exit')
    cv2.waitKey(0)


# Standard boilerplate to call the main() function to begin
# the program.
if __name__ == '__main__':
    main()