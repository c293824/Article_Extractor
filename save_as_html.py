import requests

webpage_html_files_path = "webpage_html_files/"


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


def main():
    links = import_links()

    i = 1
    while True:
        try:
            open(webpage_html_files_path + "source_" + str(i) + ".html", 'r').close()
            i += 1
        except FileNotFoundError:
            break

    for url, file_name in links:

        # Use requests to get this page
        r = requests.get(url)

        if file_name is None:
            file_name = "source_" + str(i)
            i += 1

        # Save page source
        w_file = open(webpage_html_files_path + file_name + ".html", "wb")
        w_file.write(r.content)
        w_file.close()


if __name__ == '__main__':
    main()
