import sys
import os
import io
import urllib
import collections

import lxml.etree
import slumber


class XMLSerializer(slumber.serialize.BaseSerializer):
    content_types = [
        "application/xml",
        "text/xml",
    ]
    key = "xml"

    def loads(self, data):
        if type(data) == unicode and data.strip().startswith('<?xml'):
            _header, data = data.split('\n', 1)
        return lxml.etree.fromstring(data)

    def dumps(self, data):
        return lxml.etree.tostring(data)


class JenkinsResource(slumber.Resource):
    def url(self):
        return super(JenkinsResource, self).url() + '/api/json'


class JenkinsConfigResource(slumber.Resource):
    def url(self):
        return super(JenkinsConfigResource, self).url() + '/config.xml'


class JenkinsAPI(slumber.API):
    resource_class = JenkinsResource

    def __init__(self, *args, **kwargs):
        kwargs['append_slash'] = False
        super(JenkinsAPI, self).__init__(*args, **kwargs)


class JenkinsConfigAPI(slumber.API):
    resource_class = JenkinsConfigResource

    def __init__(self, *args, **kwargs):
        kwargs['append_slash'] = False
        s = slumber.Serializer()
        s.serializers[XMLSerializer.key] = XMLSerializer()
        kwargs['serializer'] = s
        kwargs['format'] = 'xml'
        super(JenkinsConfigAPI, self).__init__(*args, **kwargs)

def jenkins_auth():
    auth = os.getenv('JENKINS_USER'), os.getenv('JENKINS_TOKEN')
    if not any(auth):
        auth = None
    return auth


def filter_directories(jobs):
    filtered = set()
    for job in list(jobs):
        prefix = append_slash(job)

        if not any(x != job and x.startswith(prefix) for x in jobs):
            filtered.add(job)

    return filtered


def job_url_to_name(base_url, url):
    if url.startswith(base_url):
        url = url[len(base_url):]
    return '/'.join(filter(None, map(urllib.unquote, url.split('/')))[1::2])


def append_slash(url):
    if not url.endswith('/'):
        url += '/'
    return url


def job_name_to_url(base_url, name):
    url = '/job/'.join([base_url] + filter(None, map(urllib.quote, name.split('/'))))
    return append_slash(url)


def dot_string_escape(s):
    return '"' + s.replace('"', '\\"') + '"'


def collect_jobs_from_view(view):
    for job in view.get('jobs', []):
        yield append_slash(job['url'])
        # yield 'view/{view_name}/job/{job_name}'.format(
        #     view_name=view['name'], job_name=job['name']
        # )


def main(root_url, view_name='All'):
    auth = jenkins_auth()
    api = JenkinsAPI(root_url, auth=auth)
    config = JenkinsConfigAPI(root_url, auth=auth)
    root = api.view(id=view_name).get()

    to_visit = set()
    visited = set()
    downstream = collections.defaultdict(set)

    if root.get('jobs'):
        to_visit.update(collect_jobs_from_view(root))

    while to_visit:
        job_url = to_visit.pop()
        if job_url in visited:
            continue

        if sys.stderr.isatty():
            print >>sys.stderr, "Fetching {job_name:>40s}. Jobs remaining: {remaining:<20d}\r".format(
                job_name=job_url_to_name(root_url, job_url), remaining=len(to_visit - visited)
            ),
            sys.stderr.flush()

        job_info = api.job(url_override=job_url).get()
        config_info = config.job(url_override=job_url).get()
        downstream_projects = [job['url'] for job in job_info.get('downstreamProjects', [])]
        downstream_job_names = config_info.xpath('.//builders/hudson.plugins.parameterizedtrigger.TriggerBuilder//projects/text()')
        downstream_projects.extend(job_name_to_url(root_url, job_name) for job_name in downstream_job_names)

        if job_info.get('jobs'):
            to_visit.update(collect_jobs_from_view(job_info))

        if downstream_projects:
            downstream[job_url].update(downstream_projects)

        to_visit.update(downstream_projects)

        visited.add(job_url)

    print >>sys.stderr, "Done fetching {num_jobs} jobs.{spacer}".format(num_jobs=len(visited), spacer=60*' ')

    all_jobs = filter_directories(visited)
    orphans = all_jobs - set(sum(map(list, downstream.values()), downstream.keys()))

    dot = io.BytesIO()
    print >>dot, 'digraph {view} {{'.format(view=dot_string_escape(view_name))
    if orphans:
        print >>dot, "  subgraph orphans {"
        for orphan in sorted(orphans):
            if orphan not in all_jobs:
                continue
            print >>dot, '    {orphan};'.format(orphan=dot_string_escape(job_url_to_name(root_url, orphan)))
        print >>dot, '    label = "orphans";'
        print >>dot, '  }'

    for name, downstreams in sorted(downstream.items()):
        for d in sorted(set(downstreams)):
            if d not in all_jobs:
                continue
            print >>dot, '  {upstream} -> {downstream};'.format(
                upstream=dot_string_escape(job_url_to_name(root_url, name)),
                downstream=dot_string_escape(job_url_to_name(root_url, d))
            )

    print >>dot, '}'

    print dot.getvalue()
    return 0

if __name__ == '__main__':
    sys.exit(main(*sys.argv[1:]))
