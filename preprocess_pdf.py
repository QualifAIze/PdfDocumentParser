import re
import fitz


class PreprocessPDF:
    BOOK_END_NAMING = "THE END"
    TOC_WITHOUT_CONTENT_NAME = "toc_without_content"
    TOC_WITH_CONTENT_NAME = "toc_with_content"

    def __init__(self, pdf_file_bytes_stream, file_name):
        self.document_name = file_name
        self.doc = fitz.open(self.document_name, pdf_file_bytes_stream)  # Open the PDF file
        self.toc = self.doc.get_toc()  # Get the table of contents

    class TreeNode:
        def __init__(self, *args):
            self.title = args[0]
            self.subsections = []
            self.level = - 1
            self.position = 0
            if len(args) == 3:
                self.content = args[1]
                self.page = args[2]

        def add_child(self, node):
            node.level = self.level + 1
            node.position = len(self.subsections)
            self.subsections.append(node)

        def to_dict(self):
            attributes_to_exist_in_json = {
                'title': self.title,
                'level': self.level,
                'position': self.position
            }
            if hasattr(self, 'page') and hasattr(self, 'content'):
                attributes_to_exist_in_json['page'] = self.page
                attributes_to_exist_in_json['content'] = self.content

            children_count = len(self.subsections)
            attributes_to_exist_in_json['subsections_count'] = children_count
            if children_count > 0:
                attributes_to_exist_in_json['subsections'] = [child.to_dict() for child in self.subsections]

            return attributes_to_exist_in_json

    def remove_useless_characters(self, string):
        return (string.encode('ascii', 'ignore')).decode("utf-8")

    def modify_title(self, title, is_start_of_sentence=True):
        if "?" in title:
            title = self.split_title_by_unexpected_char(title, is_start_of_sentence)
        title = self.remove_titles_starting_with_numbers(title)
        title = self.remove_one_char_strings(title)
        title = title.encode('utf-8').decode('ascii', 'ignore')
        return title

    def find_in_text_provided(self, text, title, search_func=str.find):
        title = self.modify_title(title, True if search_func == str.find else False)
        idx = search_func(text, title)
        return idx

    def find_title(self, text, title):
        idx = self.find_in_text_provided(text, title, str.find)
        return idx if idx >= 0 else 0

    def rfind_title(self, text, title):
        idx = self.find_in_text_provided(text, title, str.rfind)
        return idx if idx >= 0 else len(text)

    def split_title_by_unexpected_char(self, sentence, is_start_of_sentence=True):
        # Takes first half of the word when it is end_title
        # Takes second half of the word when it is starting title of the section
        return sentence.split("?")[1 if is_start_of_sentence else 0].strip()

    def remove_titles_starting_with_numbers(self, title):
        if len(title) > 0 and title[0].isdigit() and any(chr.isdigit() for chr in title):
            pattern = r"^(\d+(\.\d+)*\s+)*([A-Za-z\s]+)(\s+\d*$)*"
            match = re.search(pattern, title)
            if match:
                title = match.group(3).strip()
        return title

    def remove_one_char_strings(self, string):
        # If there is a section like 'C HAPTER ONE and so on' this method removes 'C' and the title becomes 'HAPTER ONE and so on'
        string = string.split()
        is_there_single_char_word = [item for item in string[:2] if len(item) == 1]
        string_to_return = []

        if len(string) > 1 and is_there_single_char_word:
            for i in range(len(string)):
                if i == 0:
                    continue
                string_to_return.append(string[i])
            string = " ".join(string_to_return)
        else:
            string = " ".join(string)

        return string

    def find_in_text(self, start_title, end_title, text):
        if end_title == self.BOOK_END_NAMING:
            return text
        text = re.sub(r"\n|\s{2,}", " ", text)

        section_start = self.find_title(text, start_title) + len(start_title)
        section_end = self.rfind_title(text, end_title)

        extracted_text = text[section_start: section_end]

        return extracted_text.strip()

    def separate_content_by_topics(self):
        for idx, (level, topic_title, start_page) in enumerate(self.toc):
            title = ' '.join(self.remove_titles_starting_with_numbers(topic_title).split())

            end_page = self.doc.page_count
            next_title = self.BOOK_END_NAMING
            if idx + 1 < len(self.toc):
                next_title = ' '.join(self.remove_useless_characters(self.toc[idx + 1][1]).split())
                end_page = self.toc[idx + 1][2]

            text = ""

            for page in range(start_page, end_page + 1):
                text += self.doc.load_page(page - 1).get_text()

            text = self.find_in_text(title, next_title, self.remove_useless_characters(text))

            self.toc[idx].append(text)

    def build_tree(self, toc, tree_name):
        tree = self.TreeNode(tree_name)
        stack = [tree]

        for entry in toc:
            level, title, page, content = entry

            node = self.TreeNode(title, content, page)

            while len(stack) > level:
                stack.pop()

            stack[-1].add_child(node)

            stack.append(node)

        return tree

    def process(self):
        self.separate_content_by_topics()
        toc_with_content = self.build_tree(self.toc, self.TOC_WITH_CONTENT_NAME).subsections

        # Convert TreeNode objects to dictionaries
        subsections_dict = [node.to_dict() for node in toc_with_content]

        return {
            'document_name': self.document_name,
            'subsections': subsections_dict
        }