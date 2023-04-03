# ChatResearch

[![pypi](https://img.shields.io/pypi/v/chat-research.svg)][pypi status]
[![status](https://img.shields.io/pypi/status/chat-research.svg)][pypi status]
[![python version](https://img.shields.io/pypi/pyversions/chat-research)][pypi status]
[![license](https://img.shields.io/pypi/l/chat-research)][license]
[![precommit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)][precommit]
[![black](https://img.shields.io/badge/code%20style-black-000000.svg)][black]
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/charliermarsh/ruff/main/assets/badge/v1.json)](https://github.com/charliermarsh/ruff)

[pypi status]: https://pypi.org/project/chat-research/
[license]: https://opensource.org/licenses/GPLv3
[precommit]: https://github.com/pre-commit/pre-commit
[black]: https://github.com/psf/black

This is a research project on chatbot development and evaluation.
The project includes several chatbot models and evaluation metrics.

## TODO

- [ ] Multi thread support
- [ ] Format PDF output
- [ ] Support output latex
- [ ] Tune prompt to support latex

## Features

- Chat Config: Generate `apikey.toml` in current working directory or set environment variable `OPENAI_API_KEY`.
- Chat Reviewer: Generate summary paper with specified research fields and language.
- Chat Arxiv: Fetch and summary paper from arxiv with specified query and language.
- Chat Response: Generate response for review comment with specified language.
- Chat Paper: Fetch or summary paper from local or arxiv with specified query, research fields, and language.
- Chat Biorxiv: Fetch and summary paper from bioarxiv with specified category, filter keys, and language.
- [Markdown](https://raw.githubusercontent.com/cauliyang/ChatResearch/main/images/example2.md) and [PDF report](https://raw.githubusercontent.com/cauliyang/ChatResearch/main/images/example1.pdf)

## Installation

```console
$pip install chat-research
```

## Usage

```console
> chatre -h
usage: chatre [-h] [--log-level ]
              {reviewer,arxiv,response,paper,config,biorxiv} ...

chatre Use ChatGPT to accelerate research

optional arguments:
  -h, --help                              show this help message and exit
  --log-level         The log level (default: info)

subcommand:
  valid subcommand

  {reviewer,arxiv,response,paper,config,biorxiv}
    reviewer                              Summary paper
    arxiv                                 Fetch and summary paper from arxiv
    response                              Generate reponse for review comment
    paper                                 Fetch or Summary paper from local or arxiv
    config                                config your apikey
    biorxiv                               Fetch and Summary paper from bioarxiv

```

### Chat Config

```console
❯ chatre config
```

It will generate `apikey.toml` in current working directory. Otherwise,
setting environment variable `OPENAI_API_KEY` is another way to config API KEY.

```toml
[OpenAI]
OPENAI_API_KEYS = [ "sk-key1", "sk-key2",]

[Gitee]
api = "your_gitee_api"
owner = "your_gitee_name"
repo = "your_repo_name"
path = "files_name_in_your_repo"
```

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

### Chat Arxiv

```console
❯ chatre arxiv -h
usage: chatre arxiv [-h] [--query] [--key-word] [--page-num] [--max-results] [--days] [--sort] [--save-image] [--file-format] [--language]

optional arguments:
  -h, --help      show this help message and exit
  --query         the query string, ti: xx, au: xx, all: xx,
  --key-word      the key word of user research fields
  --page-num      the maximum number of page
  --max-results   the maximum number of results
  --days          the last days of arxiv papers of this query
  --sort          another is LastUpdatedDate
  --save-image    save image? It takes a minute or two to save a picture! But pretty
  --file-format   export file format, if you want to save pictures, md is the best, if not, txt will not be messy
  --language      The other output lauguage is English, is en
```

### Chat Response

```console
❯ chatre response -h
usage: chatre response [-h] --comment-path  [--file-format] [--language]

optional arguments:
  -h, --help       show this help message and exit
  --comment-path   path of comment
  --file-format    output file format (default: txt)
  --language       output language, en or zh (default: en)

```

### Chat Paper

```console
❯ chatre paper -h
usage: chatre paper [-h] [--pdf-path] [--query] [--key-word] [--filter-keys] [--max-results] [--sort] [--save-image] [--file-format] [--language]

optional arguments:
  -h, --help      show this help message and exit
  --pdf-path      if none, the bot will download from arxiv with query
  --query         the query string, ti: xx, au: xx, all: xx (default: all: ChatGPT robot)
  --key-word      the key word of user research fields (default: reinforcement learning)
  --filter-keys   the filter key words, every word in the abstract must have, otherwise it will not be selected as the target paper (default: ChatGPT
                  robot)
  --max-results   the maximum number of results (default: 1)
  --sort          another is LastUpdatedDate (default: Relevance)
  --save-image    save image? It takes a minute or two to save a picture! But pretty (default: False)
  --file-format   the format of the exported file, if you save the picture, it is best to be md, if not, the txt will not be messy (default: md)
  --language      The other output lauguage is English, is en (default: en)

```

### Chat Biorxiv

```console
❯ chatre biorxiv -h
usage: chatre biorxiv [-h] [--category  [...]] [--date  | --days ] [--server] [--filter-keys  [...]] [--max-results] [--sort] [--save-image]
                      [--file-format] [--language]

optional arguments:
  -h, --help            show this help message and exit
  --category  [ ...]    the category of user research fields (default: bioinformatics)
  --date                the date of user research fields (example 2018-08-21:2018-08-28)
  --days                the last days of arxiv papers of this query (default: 2)
  --server              the category of user research fields (default: biorxiv)
  --filter-keys  [ ...]
                        the filter key words, every word in the abstract must have, otherwise it will not be selected as the target paper
  --max-results         the maximum number of results (default: 20)
  --sort                another is LastUpdatedDate (default: Relevance)
  --save-image          save image? It takes a minute or two to save a picture! But pretty (default: False)
  --file-format         the format of the exported file, if you save the picture, it is best to be md, if not, the txt will not be messy (default: md)
  --language            The other output lauguage is English, is en (default: en)
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributors

- Yangyang Li
