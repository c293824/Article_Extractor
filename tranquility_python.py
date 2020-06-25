import os
import sys
from html.parser import HTMLParser


"""BEGIN HTML PARSING UTILITIES"""

# Tags to include in output text file
text_containing_tags = ["p", "h1", "h2", "h3", "h4", "h5", "h6", "li"]

# Tags to definitely remove
unnecessary_tags = [
    "style",
    "link",
    "meta",
    "script",
    "noscript",
    "iframe",
    "select",
    "dd",
    "input",
    "textarea",
    "header",
    "footer",
    "nav",
    "form",
    "button",
    "picture",
    "figure",
    "svg",
]

first_heading_reached = False


class Text:
    def __init__(self, data, parent):
        self.data = data
        self.parent = parent


class Tag:
    def __init__(self, tag, attrs, parent=None):
        self.id = tag
        self.attrs = attrs
        self.children = []
        self.text = ""
        self.parent = parent


# Parses html into nested objects in preparation for tranquilizing
class Parser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.parent_queue = []
        self.root = None
        self.first_heading = None

    def handle_starttag(self, tag, attrs):
        new_tag = Tag(tag, attrs)
        if len(self.parent_queue) > 0:
            self.parent_queue[-1].children.append(new_tag)
            new_tag.parent = self.parent_queue[-1]
        else:
            self.root = new_tag

        self.parent_queue.append(new_tag)

        if (
            self.first_heading is None
            and text_containing_tags.count(tag) > 0
            and tag[0] == "h"
        ):
            self.first_heading = new_tag

    def handle_data(self, data):
        self.parent_queue[-1].children.append(Text(data, self.parent_queue[-1]))

    def handle_endtag(self, tag):
        self.parent_queue.pop()

    def has_parent(self, element, id):
        if element.parent is None:
            return False
        elif element.parent.id == id:
            return True
        else:
            return self.has_parent(element.parent, id)


# Get all text from this element and its children recursively and return in a list
# Calling this on the root of the html will obtain all text data
def extract_text(element, texts=None):
    if texts is None:
        texts = []
    if isinstance(element, Text):
        if not element.data.isspace():
            texts.append(element)
    elif isinstance(element, Tag):
        for child in element.children:
            extract_text(child, texts)

    return texts


# For each element whose tag is one of the text-containing tags (<p>, <h1>, ...) group all text under this element
# This is necessary to avoid a <span> splitting up a paragraph or heading in the resulting text file
def group_text(element):
    for child in element.children:
        if isinstance(child, Tag):
            if text_containing_tags.count(child.id) > 0:
                texts = extract_text(child)
                for text in texts:
                    child.text += text.data
            group_text(child)


# Search an element that has 'author' as a value of its attributes
def find_author(element):
    for _, val in element.attrs:
        if val is not None and val.find("author") != -1:
            return element

    for child in element.children:
        if not isinstance(child, Text):
            result = find_author(child)
            if result is not None:
                return result

    return None


def find_title(element):
    if element.id == "title":
        return element

    for child in element.children:
        if not isinstance(child, Text):
            result = find_title(child)
            if result is not None:
                return result

    return None


# Write the body from parsed html and grouped text
def write_body(element, first_heading, texts=None):
    global first_heading_reached
    if texts is None:
        texts = []

    if not first_heading_reached and element == first_heading:
        first_heading_reached = True

    if isinstance(element, Text):
        if first_heading_reached:
            if (
                not element.data.isspace()
                and unnecessary_tags.count(element.parent.id) == 0
            ):
                texts.append("<other>\n" + element.data + "\n</other>")
    else:
        if element.text != "":
            if first_heading_reached:
                texts.append(
                    "<" + element.id + ">\n" + element.text + "\n</" + element.id + ">"
                )
        else:
            for child in element.children:
                write_body(child, first_heading, texts)

    return texts


# Exclude any text that is not under a text-containing tag
def write_body_ph_only(element, first_heading, texts=None):
    global first_heading_reached
    if texts is None:
        texts = []

    if not first_heading_reached and element == first_heading:
        first_heading_reached = True

    if isinstance(element, Tag):
        if element.text != "":
            if first_heading_reached:
                texts.append(
                    "<" + element.id + ">\n" + element.text + "\n</" + element.id + ">"
                )
        else:
            for child in element.children:
                write_body_ph_only(child, first_heading, texts)

    return texts


# Use the above functions to generate the text file
def build_txt(source, url, exclude_non_text_containing_tags):
    parser = Parser()
    parser.feed("<main>" + source + "</main>")

    # Add hyperlink section
    txt = "Hyperlink:\n" + url + "\n\n"

    # Find author
    author_element = find_author(parser.root)
    if author_element is None:
        author = "Not found"
    elif author_element.text != "":
        author = author_element.text
    else:
        author_texts = extract_text(author_element)
        author = ""
        for text in author_texts:
            author += text.data

    # Add author section
    txt += "Author:\n" + author + "\n\n"

    # Group all text containing tags
    group_text(parser.root)

    # Find title
    title_element = find_title(parser.root)
    if title_element is None:
        if parser.first_heading is not None:
            title = parser.first_heading.text
        else:
            title = "Not found"
    else:
        title_texts = extract_text(title_element)
        title = ""
        for text in title_texts:
            title += text.data

    # Add title section
    txt += "Title:\n" + title + "\n\n"

    # Begin body section
    txt += "Body:\n"

    # Gather body texts
    global first_heading_reached
    first_heading_reached = False
    if exclude_non_text_containing_tags:
        body_texts = write_body_ph_only(parser.root, parser.first_heading)
        first_heading_reached = False
    else:
        body_texts = write_body(parser.root, parser.first_heading)
        first_heading_reached = False

    for text in body_texts:
        txt += text + "\n\n"

    return {"title": title, "text": txt[0:-2]}


"""END HTML PARSING UTILITIES"""


# Default file paths
webpage_html_files_path = "webpage_html_files/"
output_text_files_path = "output_text_files/"


def set_default_path(
    webpage_html_files=webpage_html_files_path, output_text_files=output_text_files_path
):
    global webpage_html_files_path
    global output_text_files_path
    webpage_html_files_path = webpage_html_files
    output_text_files_path = output_text_files


# Read html files, return in list
def import_html_files(dir_path=webpage_html_files_path):
    sources = []
    file_names = [
        f for f in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, f))
    ]
    for file_name in file_names:
        sources.append(
            [
                file_name,
                file_name[0 : file_name.find(".")],
                open(dir_path + file_name, "rb")
                .read()
                .decode(sys.stdin.encoding, errors="replace"),
            ]
        )
    return sources


# Tranquilize html files with parser
def tranquilize_files(
    exclude_non_text_containing_tags=True,
    dir_path=webpage_html_files_path,
    output_path=output_text_files_path,
):
    sources = import_html_files(dir_path)

    for url, file_name, source in sources:
        # Tranquilize html and build text file
        txt = build_txt(source, url, exclude_non_text_containing_tags)

        out_file = open(output_path + file_name + ".txt", "w")
        out_file.write(txt["text"].encode(sys.stdout.encoding, errors="replace"))
        out_file.close()
