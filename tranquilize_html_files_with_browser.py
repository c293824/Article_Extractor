import os
import re
import sys

import assets.parse_html as parse_html
from selenium import *
from selenium import webdriver
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options

chromedriver_path = "assets/chromedrivers/"
tranquilize_js_path = "assets/tranquilize.js"
webpage_html_files_path = re.sub(r'\\ ', ' ',
                                 'PATH_TO_FOLDER_OF_HTML_FILES/')
output_text_files_path = "PATH_TO_OUTPUT_FOLDER/"

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


# Read html files, return in list
def import_html_files():
    file_names = [f for f in os.listdir(webpage_html_files_path) if
                  os.path.isfile(os.path.join(webpage_html_files_path, f))]
    return file_names


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
    files = import_html_files()

    # Init headless browser driver
    print("Initializing headless browser...")
    print(type(Options))
    print(dir(Options))
    driver = webdriver.Chrome(executable_path='~/Documents/chromedriver_mac')
    print("Done")

    sources = []
    for file_name in files:
        # Open page in headless browser
        print("Loading " + file_name + "...")
        driver.get("file://" + os.getcwd() + "/" + webpage_html_files_path + file_name)
        print("Done")

        # Run javascript tranquilize on page
        print("Tranquilizing...")
        driver.execute_script(tranquilize_definitions + """
                let contentDoc = document.cloneNode(true);
                processContentDoc(contentDoc, \"""" + "" + """\");
            """)

        # Add tranquilized page to return list
        sources.append([file_name, file_name[0:file_name.find('.')], driver.page_source])

        print("Done")

    driver.close()
    return sources


def main():
    sources = get_tranquilized_page_sources()

    for url, file_name, source in sources:
        # Tranquilize html and build text file
        txt = parse_html.build_txt(source, url, exclude_nonparagraph_nonheading_text)

        out_file = open(output_text_files_path + file_name + ".txt", "wb")
        out_file.write(txt['text'].encode(sys.stdout.encoding, errors='replace'))
        out_file.close()


if __name__ == '__main__':
    main()
