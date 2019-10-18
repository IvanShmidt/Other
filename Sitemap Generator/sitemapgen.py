from bs4 import BeautifulSoup, SoupStrainer
from threading import Thread, Lock
import xml.etree.ElementTree as ET
import requests
import sys
import argparse


def createParser ():

    parser = argparse.ArgumentParser()
    parser.add_argument ('-u', '--url', required=True)                    #url to parse
    parser.add_argument ('-d', '--depth', type=int, default=1)            #recursion depth
    parser.add_argument ('-v', '--verbose', type=int, default=0)            #recursion depth
 
    return parser
 
    
class Sitemap_Generator(object):

    """The generator finds all the links on the page and starts recursively crawl on them.
    In case there are a lot of references, the depth of recursion is limited. There are also verbose parameter provided for viewing
    information in detail about crawling process."""
    
    def __init__(self, verbose=0, depth=1):
        
        self.list_links = []
        self.links      = set()
        self.bad_links  = set()
        self.verbose    = verbose
        self.depth      = depth
        self.prtc       = ''
        self.domain     = ''
    
    
    def get_domain(self, web_url):
        try:
            url_arr = web_url.split('://')
            return url_arr[0], url_arr[1].split('/')[0]
        except BaseException:
            return '', ''
    
    
    def check_link2(self, link):
        try:
            if self.domain not in link:
                link = self.prtc + '://' + self.domain + link
        except BaseException:
            link = ''
        return link


    def validate_link(self, link):
        try:
            r = requests.get(link)
            return link, True if r.status_code == 200 else False
        except BaseException:
            return link, False

        
    def recursive_crawl4(self, website_url, depth):

        if depth >= self.depth:
            return self.links, depth

        content      = requests.get(website_url)
        website_text = content.text
        bs           = BeautifulSoup(website_text, features="html.parser")

        for k, link in enumerate(bs.find_all('a')):
            checked_link = self.check_link2(link.get('href'))
            if (checked_link not in self.links) and (checked_link not in self.bad_links):
                valid_link = self.validate_link(checked_link)
                if valid_link[1]:
                    if self.verbose == 1:
                        print(valid_link[0])
                    self.links.add(valid_link[0])
                    self.links.update(self.recursive_crawl4(valid_link[0], depth+1)[0])
                else:
                    self.bad_links.add(valid_link[0])

        return self.links, depth
    
    
    def start_crowl(self, website_url):

        self.prtc, self.domain = self.get_domain(website_url)
        content                = requests.get(self.prtc + '://' + self.domain)
        website_text           = content.text
        bs                     = BeautifulSoup(website_text, features="html.parser")

        for link in bs.find_all('a'):
            valid_link = self.validate_link(link.get('href'))
            if valid_link[1]:
                self.list_links.append([valid_link[0], 0])
                if self.verbose == 1:
                    print(valid_link[0])

        if self.verbose == 1:
            print('links on rhe main page:', self.list_links)

        th_arr = []
        
        for _ in self.list_links:
            thread = Thread(target=self.recursive_crawl4, args=(_))
            th_arr.append(thread)
            thread.start()

        for thread in th_arr:
            thread.join()
            
        if self.verbose == 1:
            print('Ended crowling')
        
        
    def show_map(self):

        print("links I'v found")
        for i, link in enumerate(self.links):
            print(i, link)
        print('Total: {}'.format(len(self.links)))
        
        
    def save_sitemap_xml(self):

        links = list(self.links)

        for l in links:
            if 'stepik.org' not in l:
                links.remove(l)
        links.sort(key=lambda x: x.count('/'))

        urlset      = ET.Element("urlset")
        urlset      = ET.SubElement(urlset,"urlset")
        urlset.text = "xmlns= ---------- the location path of the sitemap ----------"

        for l in range(len(links)):
            usr      = ET.SubElement(urlset,"usr")
            loc      = ET.SubElement(usr,"loc")
            loc.text = links[l]

        tree = ET.ElementTree(urlset)
        tree.write("sitemap.xml",encoding='utf-8', xml_declaration=True)


if __name__ == "__main__":
  
    parser = createParser()
    namespace = parser.parse_args()


    sitemap = Sitemap_Generator(namespace.verbose, namespace.depth)
    sitemap.start_crowl(namespace.url)
    if namespace.verbose == 1:
        sitemap.show_map()

    print('saving sitemap')
    sitemap.save_sitemap_xml()
    
    
