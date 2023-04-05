# ChatResearch

[![pypi](https://img.shields.io/pypi/v/chat-research.svg)][pypi status]
[![python version](https://img.shields.io/pypi/pyversions/chat-research)][pypi status]
[![license](https://img.shields.io/pypi/l/chat-research)][license]
[![precommit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)][precommit]
[![black](https://img.shields.io/badge/code%20style-black-000000.svg)][black]
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/charliermarsh/ruff/main/assets/badge/v1.json)](https://github.com/charliermarsh/ruff)

[pypi status]: https://pypi.org/project/chat-research
[license]: https://opensource.org/licenses/mit
[precommit]: https://github.com/pre-commit/pre-commit
[black]: https://github.com/psf/black

ChatResearch is a tool that uses OpenAI's GPT-3 to accelerate your research.
It provides several features such as generating summary papers, fetching and summarizing papers from arxiv and bioarxiv, generating responses for review comments, and more.

## Why ChatResearch?

Numerous projects and research endeavors have been undertaken in the realm of ChatGPT, yet none have met my specific requirements.
As a result, I have resolved to
create my own project, tailored to my personal preferences.
I shall persist in refining and enhancing this project.
Please do not hesitate to leave a star, and I am grateful for your support and ratings.
I welcome any suggestions, proposals, and pull requests.

## TODO

- [x] Multi thread and Asynchronous support
- [x] Add GIF for document
- [x] Use config to set key
- [ ] Format PDF output
- [ ] Tune prompt to support latex
- [ ] Support output latex
- [ ] Fine-tune prompt
- [ ] Generate Image
- [ ] Add RSS support for multiple journal
- [ ] Revise help message
- [ ] add classic paper as examples

## Features

- [Chat Config](#chat-config): Generate `chatre.toml` in current working directory or set environment variable `OPENAI_API_KEY`.
- [Chat Paper](#chat-paper): Fetch or summary paper from local or arxiv with specified query, research fields, and language.
- [Chat Biorxiv](#chat-biorxiv): Fetch and summary paper from bioarxiv with specified category, filter keys, and language.
- [Chat Reviewer](#chat-reviewer): Generate summary paper with specified research fields and language.
- [Chat Response](#chat-response): Generate response for review comment with specified language.
- [Markdown](https://github.com/cauliyang/ChatResearch/blob/main/images/example2.md) and [PDF report](https://github.com/cauliyang/ChatResearch/blob/main/images/example1.pdf)

<img src="https://github.com/cauliyang/ChatResearch/blob/main//tutorial/project.gif" width="800" height="400">

## Installation

```console
$pip install chat-research
```

## Usage

<img src="https://github.com/cauliyang/ChatResearch/blob/main//tutorial/help.gif" width="800" height="400">

### Chat Config

<img src="https://github.com/cauliyang/ChatResearch/blob/main//tutorial/config.gif" width="800" height="400">

```console
❯ chatre config
```

It will generate `chatre.toml` in current working directory. Otherwise,
setting environment variable `OPENAI_API_KEY` is another way to config API KEY.
Also, `chatre config set OPENAI_API_KEY=sk-key` will create configuration file
in current file directory and set your key as `sk-key`.

```toml
[OpenAI]
OPENAI_API_KEYS = [ "sk-key1", "sk-key2",]

[Gitee]
api = "your_gitee_api"
owner = "your_gitee_name"
repo = "your_repo_name"
path = "files_name_in_your_repo"
```

### Chat Paper

<img src="https://github.com/cauliyang/ChatResearch/blob/main//tutorial/paper.gif" width="800" height="400">

### Chat Biorxiv

<img src="https://github.com/cauliyang/ChatResearch/blob/main//tutorial/biorxiv.gif" width="800" height="400">

### Chat Response

<img src="https://github.com/cauliyang/ChatResearch/blob/main//tutorial/response.gif" width="800" height="400">

### Chat Reviewer

```console
> chatre reviewer -h
usage: chatre reviewer [-h] --paper-path  [--file-format] [--review-format] [--research-fields] [--language]

optional arguments:
  -h, --help          show this help message and exit
  --paper-path        path of papers
  --file-format       output file format (default: txt)
  --review-format     review format
  --research-fields   the research fields of paper (default: computer science, artificial intelligence and reinforcement learning)
  --language          output language, en or zh (default: en)
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributors

- Yangyang Li

![Alt](https://repobeats.axiom.co/api/embed/05714e0999ba02041b2be2307b7923d497c0b5c3.svg "Repobeats analytics image")

## Acknowledgement

- [ChatPaper](https://github.com/kaixindelele/ChatPaper/blob/main/README.md)
- [Arxiv](https://github.com/lukasschwab/arxiv.py)
