import getopt
import os
import sys
import requests
import urllib.request
from html.parser import HTMLParser

class ImageParser(HTMLParser):
    def __init__(self):
        super(ImageParser, self).__init__()
        self.__img_srcs = []


    def handle_starttag(self, tag, attrs):
        if tag == 'img':
            src_attributes = list(filter(lambda attr: len(attr)>1 and attr[0]=='src', attrs))
            src_values = [value[1].split('?')[0] for value in src_attributes]
            self.__img_srcs += src_values


    def get_img_srcs(self):
        return self.__img_srcs


def main(argv):
    url, destination_dir = parse_arguments(argv[1:])
    image_srcs = get_image_srcs(url)
    if len(image_srcs) > 0:
        image_urls = srcs_to_urls(image_srcs, url)
        download_images(image_urls, destination_dir)
    else:
        print('No images found')


def download_images(urls,destination_dir):
    if not os.path.isdir(destination_dir):
        os.mkdir(destination_dir)
    for url in urls:
        filename = url[:-1].split('/')[-1] if url.endswith('/') else url.split('/')[-1]
        req = requests.get(url, allow_redirects=True)
        open(destination_dir + '/'+ filename, 'wb').write(req.content)


def srcs_to_urls(srcs, basic_url):
    urls = []
    for src in srcs:
        if src.startswith('http'):
            urls.append(src)
        elif src.startswith('/'):
            urls.append(basic_url + src[1:])
        else:
            urls.append(basic_url + src)
    return urls


def get_image_srcs(url):
    request = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    html_data = urllib.request.urlopen(request)
    html_bytes = html_data.read()
    html_str = html_bytes.decode('utf8')
    parser = ImageParser()
    parser.feed(html_str)
    return parser.get_img_srcs()


def parse_arguments(argv):
    destination = None
    url = None
    try:
        opts, args = getopt.getopt(argv, 'u:d:h', ['url=', 'destination=', 'help='])
    except:
        print_help()
        sys.exit(0)
    if len(opts) == 0:
        print_help()
        sys.exit(0)
    for opt, a in opts:
        if opt in ('-u', '--url'):
            url = a if a.endswith('/') else a + '/'
        elif opt in ('-d', '--destination'):
            destination = a
        elif opt in ('-h', '--help'):
            print_help()
            sys.exit(0)
        else:
            print_help()
            sys.exit(0)
    if url is None:
        print_help()
        sys.exit(0)
    if destination is None:
        destination = os.getcwd() + '/images'
    return url, destination


def print_help():
    print('Help:')
    print(sys.argv[0] + ' -u [URL] -d [DESTINATION DIRECTORY]')


if __name__ == '__main__':
    main(sys.argv)