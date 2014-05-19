import os
import xmlrpclib
import requests
import tarfile
import re
import zipfile


REQ_LINE = re.compile(r"([^<>=!]*)\s*(<=?|>=?|==|!=)?\s*(.*)")

cache_dir = os.path.join(os.path.dirname(__file__), '..', 'download-cache')
if not os.path.exists(cache_dir):
    os.mkdir(cache_dir)


def real_name(pkg_name):
    resp = requests.get(
        'http://pypi.python.org/simple/{0}'.format(pkg_name),
        timeout=10,
        allow_redirects=True,
    )
    return resp.url.split('/')[-2]


def get_reqs(pkg_name):
    client = xmlrpclib.ServerProxy('http://pypi.python.org/pypi')
    pkg_releases = client.package_releases(pkg_name)
    if not pkg_releases:
        pkg_name = real_name(pkg_name)
        pkg_releases = client.package_releases(pkg_name)

    if pkg_releases:
        pkg_urls = client.release_urls(pkg_name, pkg_releases[0])
        for pkg_url in pkg_urls:
            if pkg_url.get('packagetype') == 'sdist':
                url = pkg_url['url']
                filepath = download(url)
                if filepath:
                    return pkg_name, extract_reqs(pkg_name, filepath)


def download(url):
    filename = os.path.basename(url)
    filepath = os.path.join(cache_dir, filename)
    if os.path.exists(filepath):
        return filepath

    resp = requests.get(url, timeout=10)
    if resp.status_code == 200:
        with open(filepath, 'w') as f:
            f.write(resp.content)
        return filepath


def extract_reqs(pkg_name, filepath):
    if tarfile.is_tarfile(filepath):
        with tarfile.open(name=filepath, mode='r:*') as tar:
            req_files = []
            req_fn = '{0}.egg-info/requires.txt'.format(pkg_name)
            for tarinfo in tar:
                if tarinfo.name.endswith(req_fn):
                   req_files.append(tarinfo)

            if req_files:
                req_file = tar.extractfile(req_files[0])
                return parse_reqs(req_file.read())
            return {}

    elif zipfile.is_zipfile(filepath):
        with zipfile.ZipFile(filepath, 'r') as zipdata:
            req_files = []
            req_fn = '{0}.egg-info/requires.txt'.format(pkg_name)
            for fn in zipdata.namelist():
                if fn.endswith(req_fn):
                   req_files.append(fn)

            if req_files:
                return parse_reqs(zipdata.read(req_files[0]))
            return {}


def is_section(s):
    s = s.strip()
    return (s[0], s[-1]) == ('[', ']') and s[1:-1].strip()


def parse_line(line):
    m = REQ_LINE.search(line)
    if m:
        return m.groups()


def parse_reqs(data):
    result = {'install': {}}

    section = 'install'
    for line in data.splitlines():
        if not line.strip():
            continue

        if is_section(line):
            section = line[1:-1].strip()
            result[section] = {}
        else:
            parsed = parse_line(line)
            if parsed:
                name, cond, version = parsed
                if cond is not None:
                    version = cond + version
                result[section][name] = version

    return result
