from flask import Flask, render_template, request
import requests
from lxml import etree
import re
from bs4 import BeautifulSoup

sideLinks = {}

# add some infos that are not on the page

camera_series = '["PLACEHOLDER"]'
article_type = 'PLACEHOLDER'
chapter = 'PLACEHOLDER'
tags = '["PLACEHOLDER"]'
image = 'PLACEHOLDER'
imagesquare = 'PLACEHOLDER'


### Create Flask App ###

app = Flask(__name__)


### Create Elastic Docs ###

@app.route('/', methods=['GET'])
def create_doc_get():
    return render_template('gen_elastic_doc.html')

@app.route('/', methods=['POST'])
def create_doc_post():
    # read in list of page urls
    url = request.form['url']
    
    # use page url to fetch/parse content
    response = requests.get(url)
    html = response.text
    soup = BeautifulSoup(html, 'html.parser')

    # find in content

    ## get article title from meta tag
    article_title = (soup.find("meta", property="og:title"))["content"]
    ## get article description from meta tag
    article_description = (soup.find("meta", property="og:description"))["content"]
    ## get article description from meta tag
    article_content = soup.find('main', attrs={'class': 'docMainContainer_gTbr'}).text
    ## replace quotation marks
    jsonfied_content = article_content.replace('"', ' ')
    ## strip multiple-space character
    single_space = re.sub('\s+',' ',jsonfied_content)

    # create json object from results

    json_template = """{
        "title": "ARTICLE_TITLE",
        "series": ARTICLE_SERIES,
        "type": "ARTICLE_TYPE",
        "description": "ARTICLE_BODY",
        "sublink1": "ARTICLE_URL",
        "chapter": "ARTICLE_CHAPTER",
        "tags": ARTICLE_TAGS,
        "image": "ARTICLE_THUMB",
        "imagesquare": "ARTICLE_SQUAREIMAGE",
        "short": "ARTICLE_SHORT",
        "abstract": "ARTICLE_ABSTRACT"
    }"""


    add_body = json_template.replace('ARTICLE_BODY', single_space)
    add_title = add_body.replace('ARTICLE_TITLE', article_title)
    add_series = add_title.replace('ARTICLE_SERIES', camera_series)
    add_type = add_series.replace('ARTICLE_TYPE', article_type)
    add_url = add_type.replace('ARTICLE_URL', url[29:])
    add_chapter = add_url.replace('ARTICLE_CHAPTER', chapter)
    add_tags = add_chapter.replace('ARTICLE_TAGS', tags)
    add_image = add_tags.replace('ARTICLE_THUMB', image)
    add_imagesquare = add_image.replace('ARTICLE_SQUAREIMAGE', imagesquare)
    add_short = add_imagesquare.replace('ARTICLE_SHORT', article_description)
    add_abstract = add_short.replace('ARTICLE_ABSTRACT', article_description)

    print(add_abstract)

    # url_file = "INFO :: URL list was processed from: {0}".format(location)

    # es_docs = "INFO :: The Elastic Docs were stored in: data/articles.json"
    
    return render_template('gen_elastic_doc.html', doc = add_abstract)


### Process Sitemaps ###

@app.route('/sitemap', methods=['GET'])
def sitemap_get():
    return render_template('sitemap.html')

@app.route('/sitemap', methods=['POST'])
def sitemap_post():
    url = request.form['url']
    r = requests.get(url)
    root = etree.fromstring(r.content)

    sitemap_url = "INFO :: Sitemap processed from:  {0}".format(url)
    urls_processed = "INFO :: {0} pages imported from sitemap and file saved to data/sideLinks.txt.".format(len(root))

    for sitemap in root:
        children = sitemap.getchildren()
        sideLinks[children[0].text] = children[1].text

    with open('data/sideLinks.txt', 'w') as file:
        file.writelines('\n'.join(sideLinks))
    
    return render_template('sitemap.html', url=sitemap_url, info=urls_processed)

### Process URLs from Sitemap ###

@app.route('/process', methods=['GET'])
def process_sitemap_get():
    return render_template('process_urls.html')

@app.route('/process', methods=['POST'])
def process_sitemap_post():
    # read in list of page urls
    location = request.form['location']
    pages = open(location, 'r')

    for line in pages:
        page = line.split()[0]
        
        # use page url to fetch/parse content
        response = requests.get(page)
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')

        # find in content

        ## get article title from meta tag
        article_title = (soup.find("meta", property="og:title"))["content"]
        ## get article description from meta tag
        article_description = (soup.find("meta", property="og:description"))["content"]
        ## get article description from meta tag
        article_content = soup.find('main', attrs={'class': 'docMainContainer_gTbr'}).text
        ## replace quotation marks
        jsonfied_content = article_content.replace('"', ' ')
        ## strip multiple-space character
        single_space = re.sub('\s+',' ',jsonfied_content)

        # create json object from results

        json_template = """{
            "title": "ARTICLE_TITLE",
            "series": ARTICLE_SERIES,
            "type": "ARTICLE_TYPE",
            "description": "ARTICLE_BODY",
            "sublink1": "ARTICLE_URL",
            "chapter": "ARTICLE_CHAPTER",
            "tags": ARTICLE_TAGS,
            "image": "ARTICLE_THUMB",
            "imagesquare": "ARTICLE_SQUAREIMAGE",
            "short": "ARTICLE_SHORT",
            "abstract": "ARTICLE_ABSTRACT"
        }"""


        add_body = json_template.replace('ARTICLE_BODY', single_space)
        add_title = add_body.replace('ARTICLE_TITLE', article_title)
        add_series = add_title.replace('ARTICLE_SERIES', camera_series)
        add_type = add_series.replace('ARTICLE_TYPE', article_type)
        add_url = add_type.replace('ARTICLE_URL', page[29:])
        add_chapter = add_url.replace('ARTICLE_CHAPTER', chapter)
        add_tags = add_chapter.replace('ARTICLE_TAGS', tags)
        add_image = add_tags.replace('ARTICLE_THUMB', image)
        add_imagesquare = add_image.replace('ARTICLE_SQUAREIMAGE', imagesquare)
        add_short = add_imagesquare.replace('ARTICLE_SHORT', article_description)
        add_abstract = add_short.replace('ARTICLE_ABSTRACT', article_description)

        with open('data/articles.json', 'a') as file:
            file.write(add_abstract)

    pages.close()

    url_file = "INFO :: URL list was processed from: {0}".format(location)

    es_docs = "INFO :: The Elastic Docs were stored in: data/articles.json"
    
    return render_template('process_urls.html', location=url_file, info=es_docs)

### Run the App on all Interfaces ###

app.run(host='0.0.0.0')