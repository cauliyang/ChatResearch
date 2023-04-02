import argparse
import logging
from contextlib import redirect_stdout
from io import StringIO
from pprint import pformat

from chat_arxiv import ArxivParams, chat_arxiv_main
from chat_paper import PaperParams, chat_paper_main
from chat_response import ResponseParams, chat_response_main
from chat_reviewer import ReviewerParams, chat_reviewer_main
from flask import Flask, request, url_for
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


@app.route("/", methods=["GET"])
@app.route("/index", methods=["GET"])
def home():
    arxiv_url = url_for(
        "arxiv",
        _external=True,
        query="GPT-4",
        key_word="GPT robot",
        page_num=1,
        max_results=1,
        days=1,
        sort="web",
        save_image=False,
        file_format="md",
        language="zh",
    )
    paper_url = url_for(
        "paper",
        _external=True,
        pdf_path="",
        query="all: ChatGPT robot",
        key_word="reinforcement learning",
        filter_keys="ChatGPT robot",
        max_results=1,
        sort="Relevance",
        save_image=False,
        file_format="md",
        language="zh",
    )
    response_url = url_for(
        "response",
        _external=True,
        comment_path="review_comments.txt",
        file_format="txt",
        language="en",
    )
    reviewer_url = url_for(
        "reviewer",
        _external=True,
        paper_path="",
        file_format="txt",
        research_fields="computer science, artificial intelligence and reinforcement learning",
        language="en",
    )
    return f"""
    <h1>ChatPaper，Flask版本的优势</h1>
    <p>GitHub 项目地址：<a href="https://github.com/kaixindelele/ChatPaper" target="_blank">https://github.com/kaixindelele/ChatPaper</a></p>
    <p>将原始的 Python 脚本改为使用 Flask 构建的 Web 服务具有以下优点：</p>
    <ul>
        <li><strong>易用性</strong>：通过简单的 HTTP 请求，用户可以轻松访问和使用各个功能，无需在本地安装 Python 或其他依赖。</li>
        <li><strong>跨平台兼容性</strong>：作为 Web 服务，Flask 应用程序可以在任何支持 HTTP 请求的设备和平台上运行，从而提高了应用程序的可访问性。</li>
        <li><strong>可扩展性</strong>：使用 Flask 可以更轻松地扩展应用程序，以包含其他功能、中间件和 API 端点。</li>
        <li><strong>易于集成</strong>：Flask 应用程序可以与其他 Web 服务和前端框架（如 React、Vue.js 等）轻松集成，从而提供更丰富的用户体验。</li>
    </ul>
    <h1>功能描述和调用方法</h1>
    <h2>arxiv</h2>
    <p>搜索 Arxiv 上的论文。参数：query, key_word, page_num, max_results, days, sort, save_image, file_format, language</p>
    <p>示例：<a href="{arxiv_url}" target="_blank">{arxiv_url}</a></p>

    <h2>paper</h2>
    <p>搜索并分析论文。参数：pdf_path, query, key_word, filter_keys, max_results, sort, save_image, file_format, language</p>
    <p>示例：<a href="{paper_url}" target="_blank">{paper_url}</a></p>

    <h2>response</h2>
    <p>处理论文审稿评论。参数：comment_path, file_format, language</p>
    <p>示例：<a href="{response_url}" target="_blank">{response_url}</a></p>

    <h2>reviewer</h2>
    <p>查找论文审稿人。参数：paper_path, file_format, research_fields, language</p>
    <p>示例：<a href="{reviewer_url}" target="_blank">{reviewer_url}</a></p>
    """


def process_request(main_function, params_class, default_values):
    args = request.args.to_dict()
    for key, value in args.items():
        if key in default_values:
            args[key] = type(default_values[key])(value)

    params = params_class(**{**default_values, **args})
    output = StringIO()
    with redirect_stdout(output):
        main_function(args=params)

    output_str = output.getvalue()
    output_lines = [line.strip() for line in output_str.split("\n") if line.strip()]
    formatted_output_str = "\n".join(output_lines)
    return pformat(formatted_output_str)


@app.route("/arxiv", methods=["GET"])
def arxiv():
    default_values = {
        "query": "GPT-4",
        "key_word": "GPT robot",
        "page_num": 1,
        "max_results": 1,
        "days": 1,
        "sort": "web",
        "save_image": False,
        "file_format": "md",
        "language": "zh",
    }
    return process_request(chat_arxiv_main, ArxivParams, default_values)


@app.route("/paper", methods=["GET"])
def paper():
    default_values = {
        "pdf_path": "",
        "query": "all: ChatGPT robot",
        "key_word": "reinforcement learning",
        "filter_keys": "ChatGPT robot",
        "max_results": 1,
        "sort": "Relevance",
        "save_image": False,
        "file_format": "md",
        "language": "zh",
    }
    return process_request(chat_paper_main, PaperParams, default_values)


@app.route("/response", methods=["GET"])
def response():
    default_values = {
        "comment_path": "review_comments.txt",
        "file_format": "txt",
        "language": "en",
    }
    return process_request(chat_response_main, ResponseParams, default_values)


@app.route("/reviewer", methods=["GET"])
def reviewer():
    default_values = {
        "paper_path": "",
        "file_format": "txt",
        "research_fields": "computer science, artificial intelligence and reinforcement learning",
        "language": "en",
    }
    return process_request(chat_reviewer_main, ReviewerParams, default_values)


def get_log_level(args):
    if args.verbose == 2:
        return logging.INFO
    elif args.verbose > 2:
        return logging.DEBUG
    else:
        return logging.WARN


if __name__ == "__main__":
    # Initialize the main argument parser
    parser = argparse.ArgumentParser(description="Description of main script")
    parser.add_argument(
        "--debug", "-d", help="deploy debug mode", action="store_true", default=False
    )
    parser.add_argument("--verbose", "-v", action="count", default=1)

    args = parser.parse_args()

    logging.basicConfig(
        level=get_log_level(args),
        format="%(asctime)s %(message)s",
        datefmt="%m/%d/%Y %I:%M:%S %p",
    )

    if args.debug:
        app.run(debug=True, threaded=True, host="0.0.0.0", port=5000)
    else:
        app.run(debug=False, threaded=True, host="0.0.0.0", port=5000)
