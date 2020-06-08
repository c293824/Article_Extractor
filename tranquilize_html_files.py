import os
import re
import sys

import assets.parse_html as parse_html

webpage_html_files_path = re.sub(r'\\ ', ' ',
                                 '/Volumes/GoogleDrive/My\ Drive/Website\ Copies\ for\ testing\ nltk\ htmlcorpusmaker\ as\ per\ Text\ Analysis\ With\ Python/www.verywellmind.com/New\ Folder\ With\ 4\ Items/')
output_text_files_path = "output_text_files/"

exclude_nonparagraph_nonheading_text = True


# Read html files, return in list
def import_html_files():
    sources = []
    file_names = [f for f in os.listdir(webpage_html_files_path) if
                  os.path.isfile(os.path.join(webpage_html_files_path, f))]
    for file_name in file_names:
        print(file_name)
        sources.append([file_name, file_name[0:file_name.find('.')],
                        open(webpage_html_files_path + file_name, "rb").read().decode(sys.stdin.encoding,
                                                                                      errors='replace')])
    return sources


def main():
    sources = import_html_files()
    count = 0
    for url, file_name, source in sources:
        # Tranquilize html and build text file
        txt = parse_html.build_txt(source, url, exclude_nonparagraph_nonheading_text)
        print(txt)

        out_file = open(output_text_files_path + file_name + ".txt", "wb")
        out_file.write(txt['text'].encode(sys.stdout.encoding, errors='replace'))
        out_file.close()
        print(count)
        count += 1


if __name__ == '__main__':
    main()
