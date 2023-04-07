import io
import os

import fitz
from loguru import logger
from PIL import Image


class Paper:
    def __init__(self, path, title="", url="", abs="", authers=[]):
        self.url = url  # 文章链接
        self.path = path  # pdf路径
        self.section_names = []  # 段落标题
        self.section_texts = {}  # 段落内容
        self.abs = abs
        self.title_page = 0
        self.pdf = fitz.open(self.path)  # pdf文档

        self.title = self.get_title() if title == "" else title

        self.parse_pdf()
        self.authers = authers
        self.roman_num = [
            "I",
            "II",
            "III",
            "IV",
            "V",
            "VI",
            "VII",
            "VIII",
            "IIX",
            "IX",
            "X",
        ]

        self.digit_num = [str(d + 1) for d in range(10)]
        self.first_image = ""

    def __repr__(self):
        return f"""Papers(title={self.title}, url={self.url}, authers={self.authers} abs={self.abs})"""

    __str__ = __repr__

    def parse_pdf(self):
        self.pdf = fitz.open(self.path)  # pdf文档
        self.text_list = [page.get_text() for page in self.pdf]
        self.all_text = " ".join(self.text_list)
        self.section_page_dict = self._get_all_page_index()  # 段落与页码的对应字典
        logger.trace(f"section_page_dict {self.section_page_dict}")
        self.section_text_dict = self._get_all_page()  # 段落与内容的对应字典
        self.section_text_dict.update({"title": self.title})
        self.section_text_dict.update({"paper_info": self.get_paper_info()})
        self.pdf.close()

    def get_paper_info(self):
        first_page_text = self.pdf[self.title_page].get_text()
        if "Abstract" in self.section_text_dict.keys():
            abstract_text = self.section_text_dict["Abstract"]
        else:
            abstract_text = self.abs
        first_page_text = first_page_text.replace(abstract_text, "")
        return first_page_text

    def get_image_path(self, image_path=""):
        """
        将PDF中的第一张图保存到image.png里面，存到本地目录，返回文件名称，供gitee读取
        :param filename: 图片所在路径，"C:\\Users\\Administrator\\Desktop\\nwd.pdf"
        :param image_path: 图片提取后的保存路径
        :return:
        """
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

    def get_chapter_names(
        self,
    ):
        doc = fitz.open(self.path)  # pdf文档
        text_list = [page.get_text() for page in doc]
        all_text = ""
        for text in text_list:
            all_text += text
        # # 创建一个空列表，用于存储章节名称
        chapter_names = []
        for line in all_text.split("\n"):
            line.split(" ")
            if "." in line:
                point_split_list = line.split(".")
                space_split_list = line.split(" ")
                if 1 < len(space_split_list) < 5:
                    if 1 < len(point_split_list) < 5 and (
                        point_split_list[0] in self.roman_num
                        or point_split_list[0] in self.digit_num
                    ):
                        logger.info(f"{line=}")
                        chapter_names.append(line)
                    # 这段代码可能会有新的bug，本意是为了消除"Introduction"的问题的！
                    elif 1 < len(point_split_list) < 5:
                        logger.info(f"{line=}")
                        chapter_names.append(line)

        return chapter_names

    def fetch_title(self):
        logger.trace(self.pdf.metadata)
        return self.pdf.metadata["title"]

    def get_title(self):
        max_font_size = 0  # 初始化最大字体大小为0
        max_font_sizes = [0]
        for page_index, page in enumerate(self.pdf):  # 遍历每一页
            text = page.get_text("dict")  # 获取页面上的文本信息
            blocks = text["blocks"]  # 获取文本块列表
            for block in blocks:  # 遍历每个文本块
                if block["type"] == 0 and len(block["lines"]):  # 如果是文字类型
                    if len(block["lines"][0]["spans"]):
                        font_size = block["lines"][0]["spans"][0][
                            "size"
                        ]  # 获取第一行第一段文字的字体大小
                        max_font_sizes.append(font_size)
                        if font_size > max_font_size:  # 如果字体大小大于当前最大值
                            max_font_size = font_size  # 更新最大值
                            block["lines"][0]["spans"][0]["text"]  # 更新最大值对应的字符串
        max_font_sizes.sort()
        logger.trace(f"max_font_sizes {max_font_sizes[-10:]}")
        cur_title = ""

        for page_index, page in enumerate(self.pdf):  # 遍历每一页
            text = page.get_text("dict")  # 获取页面上的文本信息
            blocks = text["blocks"]  # 获取文本块列表
            for block in blocks:  # 遍历每个文本块
                if block["type"] == 0 and len(block["lines"]):  # 如果是文字类型
                    if len(block["lines"][0]["spans"]):
                        cur_string = block["lines"][0]["spans"][0][
                            "text"
                        ]  # 更新最大值对应的字符串
                        block["lines"][0]["spans"][0]["flags"]  # 获取第一行第一段文字的字体特征
                        font_size = block["lines"][0]["spans"][0][
                            "size"
                        ]  # 获取第一行第一段文字的字体大小
                        # print(font_size)
                        if (
                            abs(font_size - max_font_sizes[-1]) < 0.3
                            or abs(font_size - max_font_sizes[-2]) < 0.3
                        ):
                            # print("The string is bold.", max_string, "font_size:", font_size, "font_flags:", font_flags)
                            if len(cur_string) > 4 and "arXiv" not in cur_string:
                                # print("The string is bold.", max_string, "font_size:", font_size, "font_flags:", font_flags)
                                if cur_title == "":
                                    cur_title += cur_string
                                else:
                                    cur_title += " " + cur_string
                            self.title_page = page_index

        title = cur_title.replace("\n", " ")
        return title

    def _get_all_page_index(self):
        # define the chapter name list
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
        section_page_dict = {}
        for page_index, page in enumerate(self.pdf):
            cur_text = page.get_text()
            for section_name in section_list:
                section_name_upper = section_name.upper()
                if "Abstract" == section_name and section_name in cur_text:
                    section_page_dict[section_name] = page_index
                else:
                    if section_name + "\n" in cur_text:
                        section_page_dict[section_name] = page_index
                    elif section_name_upper + "\n" in cur_text:
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
                        #                         print("page_i:", page_i)
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
