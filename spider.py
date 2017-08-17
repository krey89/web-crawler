from urllib.request import urlopen
from html.parser import HTMLParser
from urllib import parse
from domain import *
#from link_finder import LinkFinder
from general import *
import ssl


ssl._create_default_https_context = ssl._create_unverified_context




class LinkFinder(HTMLParser):

    def __init__(self, base_url, page_url):
        super().__init__()
        self.base_url = base_url
        self.page_url = page_url
        self.links = set()
        # self.emails = set()

    # When we call HTMLParser feed() this function is called when it encounters an opening tag <a>
    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            for (attribute, value) in attrs:
                if attribute == 'href':
                    url = parse.urljoin(self.base_url, value)

                    if value.startswith('mailto:'):
                        # print("before print")
                        #Spider.emails.add(value)
                        Spider.emails.add(value[7:]+"\tdomain: "+get_domain_name(self.page_url)+"\tsubdomain: "+get_sub_domain_name(self.page_url))
                        #self.emails.add(value)

                        # print("found email" + value)

                    #url = parse.urljoin(self.base_url, value)
                    self.links.add(url)



    def page_links(self):
        return self.links

    def error(self, message):
        pass










class Spider:

    #class variables shared among all spiders
    project_name = ''
    base_url = ''
    domain_name = ''
    queue_file = ''
    crawled_file = ''
    emails_file = ''
    errors_file = ''
    queue = set()
    crawled = set()
    emails = set()
    errors = set()



    def __init__(self,project_name, base_url, domain_name):
        Spider.project_name = project_name
        Spider.base_url = base_url
        Spider.domain_name = domain_name
        Spider.queue_file = Spider.project_name + '/queue.txt'
        Spider.crawled_file = Spider.project_name + '/crawled.txt'

        Spider.emails_file = Spider.project_name + '/emails.txt'
        Spider.errors_file = Spider.project_name + '/errors.txt'

        self.boot()
        self.crawl_page('First Spider', Spider.base_url)

    @staticmethod
    def boot():
        create_project_dir(Spider.project_name)
        create_data_files(Spider.project_name, Spider.base_url)
        Spider.queue = file_to_set(Spider.queue_file)
        Spider.crawled = file_to_set(Spider.crawled_file)
        Spider.emails = file_to_set(Spider.emails_file)
        Spider.errors = file_to_set(Spider.errors_file)

    @staticmethod
    def crawl_page(thread_name, page_url):
        if page_url not in Spider.crawled:
            print(thread_name + ' crawling ' +page_url)
            print('Queue '+ str(len(Spider.queue)) + '| Crawled ' + str(len(Spider.crawled))+'| Errors ' +str(len(Spider.errors)) + '| Emails ' + str(len(Spider.emails)))
            Spider.add_links_to_queue(gather_links(page_url))
            Spider.queue.remove(page_url)
            Spider.crawled.add(page_url)
            Spider.update_files()

    @staticmethod
    def add_links_to_queue(links):
        for url in links:
            if (url in Spider.queue) or (url in Spider.crawled):
                continue
            if Spider.domain_name not in url:
                continue
            Spider.queue.add(url)

    @staticmethod
    def update_files():
        set_to_file(Spider.queue, Spider.queue_file)
        set_to_file(Spider.crawled, Spider.crawled_file)
        set_to_file(Spider.errors, Spider.errors_file)
        set_to_file(Spider.emails, Spider.emails_file)


def gather_links(page_url):
    html_string = ''
    try:
        response = urlopen(page_url)
        # if page_url.startswith('mailto:'):
        #     Spider.emails.add(page_url)
        if 'text/html' in response.getheader('Content-Type'):
            html_bytes = response.read()
            #html_string = html_bytes.decode("ISO-8859-4")
            html_string = html_bytes.decode("utf-8")

        finder = LinkFinder(Spider.base_url, page_url)
        finder.feed(html_string)



    except Exception as e:
        #append_to_file(Spider.errors_file,page_url+'\t'+str(e))
        Spider.errors.add(page_url + "\t" + str(e))
        print(str(e))

        return set()
    # if page_url.startswith("mailto",0,6):
    #     Spider.emails.add(page_url)

    return finder.page_links()



