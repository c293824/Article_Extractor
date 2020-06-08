import os
import re
import sys

import assets.parse_html as parse_html
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

chromedriver_path = "assets/chromedrivers/"
saved_sources_path = "saved_tranquilized_webpages/"
tranquilize_js_path = "assets/tranquilize.js"
webpage_html_files_path = re.sub(r'\\ ', ' ',
                                 '/Volumes/GoogleDrive/My\ Drive/Website\ Copies\ for\ testing\ nltk\ htmlcorpusmaker\ as\ per\ Text\ Analysis\ With\ Python/www.psychologytoday.com/us/conditions/')
output_text_files_path = "output_text_files/"

exclude_nonparagraph_nonheading_text = False


# Get current platform to decide chromedriver file
def current_platform():
    if sys.platform.startswith('linux'):
        return 'linux'
    elif sys.platform.startswith('darwin'):
        return 'mac'
    elif (sys.platform.startswith('win') or
          sys.platform.startswith('msys') or
          sys.platform.startswith('cyg')):
        if sys.maxsize > 2 ** 31 - 1:
            return 'win64'
        return 'win32'
    raise OSError('Unsupported platform: ' + sys.platform)


# Read links from webpage_links.txt, return as [ [url, title], ...]
def import_links():
    links_file = open("webpage_links.txt", "r")
    lines = links_file.readlines()
    links = []
    for i in range(len(lines)):
        if lines[i].find(' ') != -1:
            if lines[i].find('\n') != -1:
                links.append([lines[i][0:lines[i].find(' ')], lines[i][lines[i].find(' ') + 1:lines[i].find('\n')]])
            else:
                links.append([lines[i][0:lines[i].find(' ')], lines[i][lines[i].find(' ') + 1:]])
        else:
            if lines[i].find('\n') != -1:
                links.append([lines[i][0:lines[i].find('\n')], None])
            else:
                links.append([lines[i], None])
    links_file.close()
    return links


# Import javascript tranquilizing code
def import_tranquilize_functions():
    file = open(tranquilize_js_path, "r")
    tranquilize_definitions = file.read()
    file.close()
    return tranquilize_definitions


# Tranquilize pages and return the new html
def get_tranquilized_page_sources():
    chrome_options = Options()
    chrome_options.add_argument('headless')

    # Decide chromedriver file
    platform = current_platform()
    if platform == 'win32' or platform == 'win64':
        driver_file = 'chromedriver_windows.exe'
    elif platform == 'mac':
        driver_file = 'chromedriver'
    elif platform == 'linux':
        driver_file = 'chromedriver_linux'

    # Import javascript and links
    tranquilize_definitions = import_tranquilize_functions()
    links = import_links()

    # Init headless browser driver
    print("Initializing headless driver")
    driver = webdriver.Chrome(executable_path=os.getcwd() + '/' + chromedriver_path + driver_file,
                              options=chrome_options)
    print("Done")

    sources = []
    for url, file_name in links:
        # Open page in headless browser
        print("Getting " + url)
        driver.get(url)

        # Run javascript tranquilize on page
        print("Tranquilizing...")
        driver.execute_script(tranquilize_definitions + """
                let contentDoc = document.cloneNode(true);
                processContentDoc(contentDoc, \"""" + url + """\");
            """)

        # Add tranquilized page to return list
        sources.append([url, file_name, driver.page_source])

        print("Done")

    driver.close()
    return sources


def main():
    sources = get_tranquilized_page_sources()

    # Decide file name
    i = 1
    while True:
        try:
            open(saved_sources_path + "source_" + str(i) + ".html", 'r').close()
            i += 1
        except FileNotFoundError:
            break

    for url, file_name, source in sources:

        # Save source
        if file_name is None:
            file_name = "source_" + str(i)
            i += 1

        f = open(saved_sources_path + file_name + ".html", "wb")
        f.write(source.encode(sys.stdout.encoding, errors='replace'))
        f.close()

        # Build text file
        txt = parse_html.build_txt(source, url, exclude_nonparagraph_nonheading_text)

        out_file = open(output_text_files_path + file_name + ".txt", "wb")
        out_file.write(txt['text'].encode(sys.stdout.encoding, errors='replace'))
        out_file.close()


if __name__ == '__main__':
    main()
