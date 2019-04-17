import requests
from BeautifulSoup import BeautifulSoup

url_stub = "http://www.pgatour.com/stats/stat.%s.%s.html" #stat id, year
category_url_stub = 'http://www.pgatour.com/stats/categories.%s.html'
category_labels = ['RPTS_INQ', 'ROTT_INQ', 'RAPP_INQ', 'RARG_INQ', 'RPUT_INQ', 'RSCR_INQ', 'RSTR_INQ', 'RMNY_INQ']
pga_tour_base_url = "http://www.pgatour.com"
def gather_pages(url, filename):
    print filename
    urllib.urlretrieve(url, filename)

def gather_html():
    stat_ids = []
    for category in category_labels:
        category_url = category_url_stub % (category)
        page = requests.get(category_url)
        html = BeautifulSoup(page.replace('\n',''), 'html.parser')
        for table in html.find_all("div", class_="table-content"):
            for link in table.find_all("a"):
                stat_ids.append(link['href'].split('.')[1])
    starting_year = 2015 #page in order to see which years we have info for
    for stat_id in stat_ids:
        url = url_stub % (stat_id, starting_year)
        page = requests.get(url)
        html = BeautifulSoup(page.replace('\n',''), 'html.parser')
        stat = html.find("div", class_="parsys mainParsys").find('h3').text
        print stat
        directory = "stats_html/%s" % stat.replace('/', ' ') #need to replace to avoid
        if not os.path.exists(directory):
            os.makedirs(directory)
        years = []
        for option in html.find("select", class_="statistics-details-select").find_all("option"):
            year = option['value']
            if year not in years:
                years.append(year)
        url_filenames = []
        for year in years:
            url = url_stub % (stat_id, year)
            filename = "%s/%s.html" % (directory, year)
            if not os.path.isfile(filename): #this check saves time if you've already downloaded the page
                url_filenames.append((url, filename))
            jobs = [gevent.spawn(gather_pages, pair[0], pair[1]) for pair in url_filenames]
            gevent.joinall(jobs)
