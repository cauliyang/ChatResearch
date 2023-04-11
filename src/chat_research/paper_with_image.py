import io
import os
import typing as t

import fitz
from loguru import logger
from PIL import Image


class Section:
    section_list = [
        "Abstract",
        "Introduction",
        "Related Work",
        "Background",
        "Introduction and Motivation",
        "Computation Function",
        "Routing Function",
        "Preliminary",
        "Problem Formulation",
        "Methods",
        "Methodology",
        "Method",
        "Approach",
        "Approaches",
        "Materials and Methods",
        "Experiment Settings",
        "Experiment",
        "Experimental Results",
        "Evaluation",
        "Experiments",
        "Results",
        "Findings",
        "Data Analysis",
        "Discussion",
        "Results and Discussion",
        "Conclusion",
        "References",
    ]

    def __init__(self, name: str, text: str, page: t.Optional[int] = None):
        """
        Initializes a Section object with a given name, text, and page number.

        Args:
            name (str): The name of the section.
            text (str): The text content of the section.
            page (int, optional): The page number where the section starts. Defaults to None.
        """

        self.name = name
        self.text = text
        self.page = page

    def __repr__(self):
        return f"Section(name={self.name}, page={self.page})"

    def is_method(self):
        """
        Checks if the section is a method section.

        Returns:
            bool: True if the section is a method section, False otherwise.
        """
        # TODO: add more avalible name for method <Yangyang Li>
        return self.name.lower() in [
            "method",
            "methods",
            "approach",
            "approaches",
            "materials and methods",
        ]

    def is_conclusion(self):
        return "conclu" in self.name.lower()

    def is_introduction(self):
        return "intro" in self.name.lower()

    def has_text(self):
        return self.text != ""

    @staticmethod
    def valid_section_id(section: str):
        if section in Section.section_list:
            return True


class Sections:
    def __init__(self, sections: t.Dict[str, Section]):
        self._sections = sections

    def __getitem__(self, item: str):
        return self._sections[item]

    def __setitem__(self, key: str, value: Section):
        self._sections[key] = value

    def clear(self):
        self._sections.clear()

    def __repr__(self):
        return f"Sections({self._sections})"

    def has_section(self, section_name: str):
        return section_name in self._sections.keys()

    def update(self, section_dict: t.Dict[str, Section]):
        self._sections.update(section_dict)

    def section_names(self):
        return self._sections.keys()

    def sections(self):
        return self._sections.values()

    @classmethod
    def from_dict(cls, data: t.Dict[str, str]):
        sections = {}
        for name, text in data.items():
            sections[name] = Section(name, text)
        return cls(sections)

    def get_method(self) -> t.List[Section]:
        methods = []
        for _, section in self._sections.items():
            if section.is_method():
                methods.append(section)
        return methods

    def get_conclusion(self) -> t.List[Section]:
        conclusions = []
        for _, section in self._sections.items():
            if section.is_conclusion():
                conclusions.append(section)
        return conclusions

    def get_intro(self) -> Section:
        return self._sections.get("Introduction")


class Paper:
    def __init__(self, path, title="", url="", abs="", authers=[]):
        self.url = url
        self.path = path
        self.section_names = []
        self.section_texts = {}
        self.abs = abs
        self.title_page = 0
        self.pdf = fitz.open(self.path)
        self.title = self.get_title() if title == "" else title

        self.parse_pdf()
        self.authers = authers
        self.first_image = ""

    def __repr__(self):
        return f"""Papers(title={self.title}, url={self.url}, authers={self.authers} abs={self.abs})"""

    __str__ = __repr__

    def parse_pdf(self):
        self.text_list = [page.get_text() for page in self.pdf]
        self.all_text = " ".join(self.text_list)
        self.section_page_dict = self._get_all_page_index()  # 段落与页码的对应字典
        logger.trace(f"section_page_dict {self.section_page_dict}")

        section_text_dict = self._get_all_page()  # 段落与内容的对应字典
        self.sections = Sections.from_dict(section_text_dict)
        self.sections["titile"] = Section("title", self.title)
        self.sections["paper_info"] = Section("paper_info", self.get_paper_info())

    def get_paper_info(self):
        first_page_text = self.pdf[self.title_page].get_text()
        if self.sections.has_section("Abstract"):
            abstract_text = self.sections["Abstract"].text
        else:
            abstract_text = self.abs

        first_page_text = first_page_text.replace(abstract_text, "")

        return first_page_text

    def get_image_path(self, image_path=""):
        max_size = 0
        image_list = []
        ext = None
        with fitz.Document(self.path) as my_pdf_file:
            for page_number in range(1, len(my_pdf_file) + 1):
                page = my_pdf_file[page_number - 1]
                page.get_images()
                for _, image in enumerate(page.get_images(), start=1):
                    xref_value = image[0]
                    base_image = my_pdf_file.extract_image(xref_value)
                    image_bytes = base_image["image"]
                    ext = base_image["ext"]
                    image = Image.open(io.BytesIO(image_bytes))
                    image_size = image.size[0] * image.size[1]
                    if image_size > max_size:
                        max_size = image_size
                    image_list.append(image)

        if ext is None:
            raise Exception("No image found in pdf")

        for image in image_list:
            image_size = image.size[0] * image.size[1]
            if image_size == max_size:
                image_name = f"image.{ext}"
                im_path = os.path.join(image_path, image_name)
                logger.trace(f"image_path: {im_path}")

                max_pix = 480
                min(image.size[0], image.size[1])

                if image.size[0] > image.size[1]:
                    min_pix = int(image.size[1] * (max_pix / image.size[0]))
                    newsize = (max_pix, min_pix)
                else:
                    min_pix = int(image.size[0] * (max_pix / image.size[1]))
                    newsize = (min_pix, max_pix)
                image = image.resize(newsize)

                image.save(open(im_path, "wb"))
                return im_path, ext
        return None, None

    def fetch_title(self):
        logger.trace(self.pdf.metadata)
        return self.pdf.metadata["title"]

    def get_max_font_size(self, max_page_index=4):
        max_font_size = 0  # 初始化最大字体大小为0
        all_font_sizes = [0]

        for page_index, page in enumerate(self.pdf):  # 遍历每一页
            if page_index < max_page_index:
                text = page.get_text("dict")  # 获取页面上的文本信息
                blocks = text["blocks"]  # 获取文本块列表
                for block in blocks:  # 遍历每个文本块
                    if block["type"] == 0 and len(block["lines"]):  # 如果是文字类型
                        if len(block["lines"][0]["spans"]):
                            font_size = block["lines"][0]["spans"][0][
                                "size"
                            ]  # 获取第一行第一段文字的字体大小
                            all_font_sizes.append(font_size)
                            if font_size > max_font_size:  # 如果字体大小大于当前最大值
                                max_font_size = font_size  # 更新最大值

        all_font_sizes.sort()
        return all_font_sizes, max_font_size

    def get_title(self, max_page_index=4):
        max_font_sizes, max_font_size = self.get_max_font_size(max_page_index)

        logger.trace(f"max_font_sizes {max_font_sizes[-10:]}")
        cur_title = ""
        previous_page_index = 0
        for page_index, page in enumerate(self.pdf):  # 遍历每一页
            if page_index < max_page_index:
                text = page.get_text("dict")  # 获取页面上的文本信息
                blocks = text["blocks"]  # 获取文本块列表
                for block in blocks:  # 遍历每个文本块
                    if block["type"] == 0 and len(block["lines"]):  # 如果是文字类型
                        if len(block["lines"][0]["spans"]):
                            cur_string = block["lines"][0]["spans"][0][
                                "text"
                            ]  # 更新最大值对应的字符串
                            font_size = block["lines"][0]["spans"][0][
                                "size"
                            ]  # 获取第一行第一段文字的字体大小

                            if (
                                abs(font_size - max_font_sizes[-1]) < 0.3
                                or abs(font_size - max_font_sizes[-2]) < 0.3
                            ):
                                if len(cur_string) > 4 and "arXiv" not in cur_string:
                                    if cur_string != "":
                                        if previous_page_index == page_index:
                                            cur_title += " " + cur_string
                                    else:
                                        cur_title += cur_string
                                        self.title = page_index
                                    previous_page_index = page_index

        title = cur_title.replace("\n", " ").strip()
        return title

    def _get_all_page_index(self):
        # define the chapter name list
        section_page_dict = {}
        for page_index, page in enumerate(self.pdf):
            cur_text = page.get_text()
            for section_name in Section.section_list:
                if (
                    section_name in cur_text
                    or section_name.upper() + "\n" in cur_text
                    or section_name + "\n" in cur_text
                ):
                    section_page_dict[section_name] = page_index

        return section_page_dict

    def _get_all_page(self):
        """

        Get the text information of each page in the PDF file and return the text information as a dictionary according to the chapter.

        Returns:
            section_dict (dict): Text information dictionary for each chapter, key for chapter name, value for chapter text.

        """
        text_list = []
        section_dict = {}

        text_list = [page.get_text() for page in self.pdf]

        for sec_index, sec_name in enumerate(self.section_page_dict):
            logger.trace(
                f"{sec_index=}, {sec_name=}, {self.section_page_dict[sec_name]}"
            )

            if sec_index <= 0 and self.abs:
                continue
            else:
                start_page = self.section_page_dict[sec_name]

                if sec_index < len(list(self.section_page_dict.keys())) - 1:
                    end_page = self.section_page_dict[
                        list(self.section_page_dict.keys())[sec_index + 1]
                    ]
                else:
                    end_page = len(text_list)

                logger.trace(f"{start_page=}, {end_page=}")

                cur_sec_text = ""
                if end_page - start_page == 0:
                    if sec_index < len(list(self.section_page_dict.keys())) - 1:
                        next_sec = list(self.section_page_dict.keys())[sec_index + 1]
                        if text_list[start_page].find(sec_name) == -1:
                            start_i = text_list[start_page].find(sec_name.upper())
                        else:
                            start_i = text_list[start_page].find(sec_name)
                        if text_list[start_page].find(next_sec) == -1:
                            end_i = text_list[start_page].find(next_sec.upper())
                        else:
                            end_i = text_list[start_page].find(next_sec)
                        cur_sec_text += text_list[start_page][start_i:end_i]
                else:
                    for page_i in range(start_page, end_page):
                        if page_i == start_page:
                            if text_list[start_page].find(sec_name) == -1:
                                start_i = text_list[start_page].find(sec_name.upper())
                            else:
                                start_i = text_list[start_page].find(sec_name)
                            cur_sec_text += text_list[page_i][start_i:]
                        elif page_i < end_page:
                            cur_sec_text += text_list[page_i]
                        elif page_i == end_page:
                            if sec_index < len(list(self.section_page_dict.keys())) - 1:
                                next_sec = list(self.section_page_dict.keys())[
                                    sec_index + 1
                                ]
                                if text_list[start_page].find(next_sec) == -1:
                                    end_i = text_list[start_page].find(next_sec.upper())
                                else:
                                    end_i = text_list[start_page].find(next_sec)
                                cur_sec_text += text_list[page_i][:end_i]
                section_dict[sec_name] = cur_sec_text.replace("-\n", "").replace(
                    "\n", " "
                )
        return section_dict
