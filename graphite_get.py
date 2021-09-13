#!/usr/bin/env python

import argparse
import requests
import urllib.parse
import json


class Point:
    def __init__(self, timestamp, value):
        self.timestamp = int(timestamp)
        self.value = float(value)

    def str(self):
        return "{ %d, %f }" % (self.timestamp, self.value)

    def __str__(self):
        return self.str()


def graphite_render(url, user, password, targets, from_time, until_time):
    u = url+"/render/?format=json&from=%s&until=%s" % (from_time, until_time)
    for target in targets:
        u += "&target=" + urllib.parse.quote(target)

    resp = requests.get(u, auth=(user, password))

    metrics = dict()
    if resp.status_code == 404:
        if len(resp.text) == 0:
            # valid carbonapi responce
            return metrics

        raise RuntimeError("request '%s' failed with %s (%s)" % (u, resp.status_code, resp.text))
    if resp.status_code == 200:
        content_type = resp.headers['content-type']
        if content_type != 'application/json':
            raise RuntimeError("request '%s' failed, content type mismatch: '%s' (%s)" % (u, content_type, resp.text))        
        try:
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
        except Exception as e:
            raise RuntimeError("request '%s' responce mismatched: %s" % (u, resp.text))        

        return metrics

    raise RuntimeError("request '%s' failed with %s (%s)" % (u, resp.status_code, resp.text))


def parse_cmdline():
    parser = argparse.ArgumentParser(description='Get graphite metrics')

    # parser.add_argument('pos', action='store', type=str, help='positional parameter')

    parser.add_argument('-a', '--address', dest='address', action='store', type=str, required=True,
                        help='URL of carbonapi server')

    parser.add_argument('-F', '--from', dest='from_time', action='store', type=str, default="-5m",
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

    for target, points in result.items():
        print("%s: %s" % (target, ', '.join(map(str, points))))


if __name__ == "__main__":
    main()
