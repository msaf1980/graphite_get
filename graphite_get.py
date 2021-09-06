#!/usr/bin/env python

import argparse
import requests
import json


class Point:
    def __init__(self, timestamp, value):
        self.timestamp = int(timestamp)
        self.value = float(value)

    def __str__(self):
        return "{ %d, %f }" % (self.timestamp, self.value)


def graphite_render(url, user, password, targets, from_time, until_time):
    u = url+"/render/?format=json&from=%s&until=%s" % (from_time, until_time)
    for target in targets:
        u += "&target=" + target
    
    print(u)
    resp = requests.get(u, auth=(user, password))

    metrics = dict()
    if resp.status_code == 404:
        return metrics
    if resp.status_code == 200:
        data = json.loads(resp.text)
        for r in data:
            target = r.get('target')
            datapoints = r.get('datapoints')
            if target is None or datapoints is None:
                continue

            points = list()
            for point in datapoints:
                # print(point)
                points.append(Point(point[1], point[1]))

            metrics[target] = points

        return metrics

    raise RuntimeError("request failed with %s" % resp.status_code)

        
    


def parse_cmdline():
    parser = argparse.ArgumentParser(description='Get graphite metrics')

    #parser.add_argument('pos', action='store', type=str, help='positional parameter')

    parser.add_argument('-a', '--address', dest='address', action='store', type=str, required=True,
                        help='URL of carbonapi server')

    parser.add_argument('-F', '--from', dest='from_time', action='store', type=str, default="now-5s",
                        help='From timestamp (relative or absolute)')

    parser.add_argument('-U', '--until', dest='until_time', action='store', type=str, default="now",
                        help='Until timestamp (relative or absolute)')

    parser.add_argument('-u', '--user', dest='user', action='store', type=str, default="",
                        help='Username (basic auth), also GRAPHITE_USER env variable can be used')

    parser.add_argument('-p', '--password', dest='password', action='store', type=str, default="",
                        help='Password (basic auth), also GRAPHITE_PASSWORD env variable can be used')

    parser.add_argument('targets', metavar='T', type=str, nargs='+',
                        help='Targets')

    return parser.parse_args()


def main():
    args = parse_cmdline()
    if len(args.targets) == 0:
        sys.exit("No targets specified")

    result = graphite_render(args.address, args.user, args.password, args.targets,
                             args.from_time, args.until_time)

    print(result)

if __name__ == "__main__":
    main()
