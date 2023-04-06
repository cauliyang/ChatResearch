# Changelog

All notable changes to this project will be documented in this file.

## [unreleased]

### Co-authored-by

- Dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>
- Dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>
- Dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>
- Yangliz5 <yangyang.li@northwestern.edu>
- Dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>
- Dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>
- Dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>
- Dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>
- Dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>
- Dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>
- Dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>
- Dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>

### Features

- 🔧 chore(cliff.toml): update commit_parsers regex to match any commit message starting with feat, fix, doc, perf, refactor, style, test, chore, and ending with any character. Update filter_unconventional to false and split_commits to true.
- 🚀 feat(.opencommitignore): add file to ignore certain file types in commits

### Miscellaneous Tasks

- 🔧 chore(Makefile): replace aic with oc in commit script

### Signed-off-by

- Dependabot[bot] <support@github.com>

### Build

- Bump poetry from 1.4.1 to 1.4.2 in /.github/workflows
- Bump openai from 0.27.2 to 0.27.4 (#14)
- Bump ruff from 0.0.260 to 0.0.261 (#13)
- Bump pypa/gh-action-pypi-publish from 1.5.1 to 1.8.5 (#11)

## [0.1.10] - 2023-04-05

### Features

- Add fetch_title method to fetch title from pdf metadata

### Miscellaneous Tasks

- 🔖 chore(pyproject.toml): bump up version to 0.1.10

### Refactor

- Comment out unused code

## [0.1.9] - 2023-04-05

### Documentation

- Add docs
- Add Makefile with clean, format, sync, test, and commit commands, and update README with classic paper examples in TODO list; remove unused Docker-related files and images; move tutorial images to docs folder
- Add docs

## [0.1.8] - 2023-04-05

### Bug Fixes

- 🐛 fix(AsyncBaseReader): change logger level from info to trace in report_token_usage method
- 🐛 fix(async_arxiv.py): change logger level from trace to info in Result class's download_pdf method

### Features

- 📝 docs(README.md): update README.md with new features and GIF tutorials

### Refactor

- Refactor

## [0.1.7] - 2023-04-05

### Bug Fixes

- 🔨 chore(**main**.py): fix typo in chat_arxiv_command variable name
- 🐛 fix(chat_research): rename cli function to \_cli to avoid name collision
- 🐛 fix(chat_async_paper.py): rename subcommand name from asyncpaper to paper

### Features

- Add async support
- ✨ feat(chat_research): add try-except block to handle KeyboardInterrupt

### Miscellaneous Tasks

- 🔖 chore(pyproject.toml): bump up version to 0.1.6

### Refactor

- Add aiohttp and fake-useragent to Pyproject.toml, and refactor chat_biorxiv.py and async_biorxiv.py to use async/await and aiohttp for downloading PDFs in an asynchronous way
- 🔥 refactor(**main**.py): remove chat_paper module and its references
- Refactor

## [0.1.6] - 2023-04-04

### Bug Fixes

- 📝 docs(README.md): fix typo in TODO list
- 🐛 fix(README.md): check off "Use config to set key" task

### Documentation

- 📝 docs(README.md): revise TODO list
- 📝 docs(README.md): add help.gif to Usage section
- 📝 docs(README.md): update file to reflect correct configuration file name.
- 📝 docs(config.yml): add configuration for welcome, new-issue-welcome, new-pr-welcome, and first-pr-merge behavior bots

### Features

- 📝 docs(CHANGELOG.md): add new features and changes in version 0.1.4
- ✨ feat(create_gif.sh): add script to create gif from asciinema recording
- ✨ feat(chat_config.py): add ability to set OpenAI API keys in config file using command line arguments

### Miscellaneous Tasks

- 🔍 chore(.gitignore): update .gitignore to exclude chatre.toml instead of apikey.toml
- 🔍 chore(.gitignore): add \*.cast to ignore list
- 🔧 chore(cliff.toml): add configuration file for git-cliff
- 🚀 chore(README.md): add 'Use config to set key' to the to-do list
- 🔖 chore(pyproject.toml): bump up version to 0.1.6

### Styling

- 🎨 style(tutorial/help.gif): add help.gif to tutorial directory
- 🎨 style(README.md): replace markdown image with HTML image tag
- 🎨 style(README.md): resize images in README.md
- 🎨 style(README.md): add image to Chat Config section
- 🎨 style(README.md): add image to Chat Arxiv section
- 🎨 style(tutorial): add gif files for Chat Config and Chat Arxiv sections
- 🎨 style(README.md): update images size and remove unnecessary console output

## [0.1.5] - 2023-04-03

### Bug Fixes

- 📝 docs(README.md): update project description and fix broken links
- 📝 docs(README.md): improve readability and fix typos

### Documentation

- 📝 docs: add Repobeats analytics image to README.md
- 📝 docs: add Acknowledgement section to README.md

### Features

- 🚀 feat: add homepage, repository, documentation, and classifiers to pyproject.toml
- 🚀 feat: add classifiers to pyproject.toml
- 🚀 feat(README.md): add 'Add gif' to the feature list

### Miscellaneous Tasks

- 🔧 chore: update license to MIT License
- 🚚 chore(chat_config.py): rename 'config your apikey' to 'Generate configuration file'
- 🚚 chore(utils.py): rename 'apikey.toml' to 'chatre.toml' and add CONFIG_FILE_NAME constant
- 🔖 chore(pyproject.toml): bump up version to 0.1.5

### Testing

- 🔧 chore(pre-commit): update black and ruff hooks to latest versions

## [0.1.4] - 2023-04-03

### Bug Fixes

- 🚀 chore(pyproject.toml): remove packages field and fix chatre script path
- 🐛 fix(**init**.py): fix import statement for Paper class
- 🐛 fix(**main**.py): set width to 80 for RichHelpFormatter
- 🐛 fix(**init**.py): import paper and paper_with_image modules
- 🐛 fix(chat_paper.py): raise ValueError if args is None
- 🐛 fix(chat_paper.py): set language to English if args.language is not "en" or "zh"
- 🐛 fix(chat_paper.py): raise ValueError if pdf_path does not exist
- 🐛 fix(chat_response.py): raise ValueError if comment_path does not exist
- 🐛 fix(chat_arxiv.py): log exception messages correctly
- 🐛 fix(chat_arxiv.py): fix report_token_usage import
- 🐛 fix(chat_arxiv.py): fix report_token_usage function call
- 🐛 fix(chat_arxiv.py): fix logger.info calls to use f-strings
- 🐛 fix(chat_arxiv.py): fix logger.info calls to log token usage correctly
- 🐛 fix(paper_with_image.py): fix logger.info() calls by adding f-string
- 🐛 fix(test_paper.py): fix test_paper and test_paper_with_image tests to use demo.pdf from test/data directory
- 🐛 fix(.gitignore): add 'export' to .gitignore
- 🐛 fix(chat_paper.py): fix root_path type error
- 🐛 fix(paper_with_image.py): add f-string to logger.info to log start_page and end_page variables
- 🐛 fix(**main**.py): add logger configuration to stderr
- 🐛 fix(chat_arxiv.py): get gitee_key from config dictionary
- 🐛 fix(chat_reviewer.py): raise ValueError if args is None
- 🐛 fix(**main**.py): remove single quotes from logger format string to fix formatting issue
- 🐛 fix(chat_paper.py): remove redundant log message and fix log message format in chat_paper.py
- 🐛 fix(export.py): add fallback to markdown if pandoc fails to output pdf
- 🐛 fix(reader.py): remove unnecessary translations and add f-strings

### Documentation

- 📝 docs(README.md): add project description, installation, usage, license, and contributors sections
- 📄 docs: add demo.pdf test file
- 📝 docs(README.md): update README.md with new usage instructions and subcommands
- 📝 docs(README.md): add links to example markdown and pdf report

### Features

- 🚀 feat(chat_arxiv.py): add Paper class to handle papers with images
- ✨ feat(chat_arxiv.py): add metavar to arguments and improve help messages
- ✨ feat(paper_with_image.py): add Paper class to parse pdf and extract paper information and sections. Add get_image_path method to extract the first image from the pdf and save it to a local directory. Add get_chapter_names method to extract chapter names from the pdf. Add get_title method to extract the title of the paper from the pdf.
- ✨ feat(chat_paper.py): add support for pytest
- ✨ feat(chat_paper.py): add support for pytest-sugar
- ✨ feat(chat_paper.py): add support for --max-results argument
- ✨ feat(chat_paper.py): add support for --save-image argument
- ✨ feat(chat_paper.py): add support for --file-format argument
- ✨ feat
- ✨ feat(paper_with_image.py): add support for image resizing and saving
- ✨ feat(chat_research): add rich traceback to **init**.py
- ✨ feat(chat_research): add loguru logger to **main**.py
- ✨ feat(paper.py): add title parameter to Paper class constructor
- ✨ feat(chat_research/chat_config.py): add config subcommand to create apikey.toml
- Add biorxiv provider
- Add biorxiv provider
- ✨ feat(reader.py): add key_words parameter to summary_with_chat, chat_summary, chat_method, and chat_conclusion methods
- Extract base reader
- 🎉 feat(noxfile.py): add nox configuration file
- 🚀 chore(README.md): add features section and update installation guide
- 🚀 chore(README.md): add new features to TODO list

### Miscellaneous Tasks

- 🔧 chore(chat_arxiv.py): remove unnecessary blank lines and add metavar to arguments
- 🔧 chore(chat_paper.py): update import statement for Paper class
- 🔧 chore(chat_paper.py): change sort parameter type from enum to string
- 🔧 chore(chat_reviewer.py): update import statement for Paper class
- 🔧 chore(chat_reviewer.py): add default value for review_format parameter
- 🔧 chore(chat_reviewer.py): add metavar for all arguments in add_subcommand function in chat_reviewer.py
- 🔧 chore(chat_response.py): add metavar for all arguments in add_subcommand function in chat_response.py
- 🔧 chore(pyproject.toml): add types-requests package
- 🔧 chore(pre-commit): add isort hook to pre-commit config
- 🔧 chore(pyproject.toml): add isort profile to tool.isort
- 🔧 chore(chat_research): move report_token_usage function to utils.py
- 🔧 chore(paper.py): rearrange imports in alphabetical order
- 🚀 chore(utils.py): add function to report token usage
- 🗑️ chore(ReviewFormat.txt): delete file
- 🔧 chore(.gitignore): add apikey.toml to ignore list
- 🔧 chore(pyproject.toml): add toml to dependencies
- 🔧 chore(chat_research/**main**.py): add chat_config subcommand
- 🔧 chore(chat_research/chat_arxiv.py): add help message to subcommand
- 🔧 chore(chat_research/chat_paper.py): add help message to subcommand
- 🔧 chore(chat_research/chat_response.py): add help message to subcommand
- 🔧 chore(chat_research/chat_reviewer.py): add help message to subcommand
- 🔧 chore(chat_research/utils.py): change apikey.ini to apikey.toml and add error message
- 🔧 chore(**init**.py): add utils module to **all** list
- 🔧 chore(chat_biorxiv.py): add file-format argument and choices to add_subcommand function
- 🔧 chore(chat_paper.py): add file-format argument and choices to add_subcommand function
- 🔧 chore(export.py): add export function and combine_md function
- 🔧 chore(paper_with_image.py): change logger.info to logger.trace in Paper class
- 🔧 chore(arxiv.py): change \_last_request_dt type to Optional[datetime]
- 🚀 chore(release.yml): remove unused check-parent-commit step
- 🔧 chore(pyproject.toml): add nox and nox-poetry dependencies
- 🔖 chore(pyproject.toml): update version to 0.1.1
- 📝 chore(pyproject.toml): update version to 0.1.2
- 🚀 chore(pyproject.toml): update version to 0.1.3
- 🔖 chore(pyproject.toml): bump up version to 0.1.4

### Refactor

- 🔥 refactor(chat_arxiv.py): remove unused imports and code
- 🔥 refactor(chat_arxiv.py): remove unused Paper class and its methods
- 🔨 refactor(chat_reviewer.py): add pydantic validator to check if paper_path exists
- 🔨 refactor(chat_reviewer.py): add default values to some arguments
- 🔨 refactor(paper.py): remove redundant code
- 🔨 refactor(paper_with_image.py): remove main function
- 🔧 chore(chat_research): refactor code to load API keys from configuration file and environment variable
- 🔧 chore(**main**.py): refactor logger initialization and add log-level argument
- 🔨 refactor(reader.py): remove category parameter from BaseReader constructor
- 🔨 refactor(reader.py): remove export_to_markdown method from BaseReader class

### Styling

- 🎨 style(**init**.py): reformat import statements
- 🎨 style(**main**.py): reformat import statements
- 🎨 style(app.py): reformat import statements
- 🎨 style(README.md): update badges and format file for better readability

### Testing

- 🔧 chore(pyproject.toml): add pytest and pytest-sugar packages
- 🧪 test(test_paper.py): add test for paper_with_image module
- 🚚 chore(test_paper.py): move demo.pdf to test/data directory

<!-- generated by git-cliff -->
