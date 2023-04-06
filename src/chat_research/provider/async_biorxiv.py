import asyncio
import json
import re
import time
import typing as t
from calendar import timegm
from datetime import datetime, timezone
from enum import Enum, auto
from pathlib import Path
from typing import Any, Optional

import aiofiles
import aiohttp
import feedparser
import requests
import tenacity
from loguru import logger
from pydantic import BaseModel

_DEFAULT_TIME = datetime.min


class Category(Enum):
    AnimalBeHaviorAndCognition = auto()
    Biochemistry = auto()
    Bioengineering = auto()
    Bioinformatics = auto()
    Biophysics = auto()
    CancerBiology = auto()
    CellBiology = auto()
    ClinicalTrials = auto()
    DevelopmentalBiology = auto()
    Ecology = auto()
    Epidemiology = auto()
    EvolutionaryBiology = auto()
    Genetics = auto()
    Genomics = auto()
    Immunology = auto()
    Microbiology = auto()
    MolecularBiology = auto()
    Neuroscience = auto()
    Paleontology = auto()
    Pathology = auto()
    PharmacologyAndToxicology = auto()
    Physiology = auto()
    PlantBiology = auto()
    ScientificCommunicationAndEducation = auto()
    SyntheticBiology = auto()
    SystemsBiology = auto()
    Zoology = auto()
    Unknown = auto()

    @classmethod
    def from_str(cls, category) -> "Category":
        if category == "animal behavior and cogtition":
            return cls.AnimalBeHaviorAndCognition
        elif category == "biochemistry":
            return cls.Biochemistry
        elif category == "bioengineering":
            return cls.Bioengineering
        elif category == "bioinformatics":
            return cls.Bioinformatics
        elif category == "biophysics":
            return cls.Biophysics
        elif category == "cancer biology":
            return cls.CancerBiology
        elif category == "clinical trials":
            return cls.ClinicalTrials
        elif category == "developmental biology":
            return cls.DevelopmentalBiology
        elif category == "ecology":
            return cls.Ecology
        elif category == "epidemiology":
            return cls.Epidemiology
        elif category == "evolutionary biology":
            return cls.EvolutionaryBiology
        elif category == "genetics":
            return cls.Genetics
        elif category == "genomics":
            return cls.Genomics
        elif category == "immunology":
            return cls.Immunology
        elif category == "microbiology":
            return cls.Microbiology
        elif category == "molecular biology":
            return cls.MolecularBiology
        elif category == "neuroscience":
            return cls.Neuroscience
        elif category == "paleontology":
            return cls.Paleontology
        elif category == "pathology":
            return cls.Pathology
        elif category == "pharmacology and toxicology":
            return cls.PharmacologyAndToxicology
        elif category == "physiology":
            return cls.Physiology
        elif category == "plant biology":
            return cls.PlantBiology
        elif category == "scientific communication and education":
            return cls.ScientificCommunicationAndEducation
        elif category == "synthetic biology":
            return cls.SyntheticBiology
        elif category == "systems biology":
            return cls.SystemsBiology
        elif category == "zoology":
            return cls.Zoology
        else:
            return cls.Unknown


class Result:
    """
        An entry in an bioarXiv query results feed.

    Attributes
        start_date: str = None
        end_date: str = None
        days: int = None
        max_results: float
        sort_by: SortCriterion = SortCriterion.Relevance
        sort_order: SortOrder = SortOrder.Descending
    ```

    """

    def __init__(
        self,
        doi: str,
        title: str,
        authors: str,
        author_corresponding: str,
        author_corresponding_institution: str,
        version: int,
        category: Category,
        jats_xml_path: str,
        abstract: str,
        published: str,
        server: str,
        pdf_url: Optional[str] = None,
        entry_id: Optional[str] = None,
        date: datetime = _DEFAULT_TIME,
    ):
        self.doi = Result.validate_doi(doi)
        self.title = title
        self.authors = authors
        self.author_corresponding = author_corresponding
        self.author_corresponding_institution = author_corresponding_institution
        self.version = version
        self.category = category
        self.jats_xml_path = Result.validate_jats_xml(jats_xml_path)
        self.abstract = abstract
        self.published = published
        self.server = server
        self.pdf_url = pdf_url
        self.entry_id = entry_id
        self.date = Result.validate_date(date)

        self.headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 "
            "Safari/537.36",
            "Connection": "keep-alive",
        }

    @staticmethod
    def validate_doi(doi):
        """Validate a DOI."""
        return doi.replace("\\", "")

    @staticmethod
    def validate_jats_xml(jats_xml):
        """Validate a JATS XML URL."""
        return jats_xml.replace("\\", "")

    @staticmethod
    def validate_date(date):
        """Validate a date."""
        return Result._to_datetime(time.strptime(date, "%Y-%m-%d"))

    @classmethod
    def from_api_entry(cls, entry) -> "Result":
        try:
            result = cls(
                doi=entry["doi"],
                title=entry["title"],
                authors=entry["authors"],
                author_corresponding=entry["author_corresponding"],
                author_corresponding_institution=entry[
                    "author_corresponding_institution"
                ],
                date=entry["date"],
                version=entry["version"],
                category=Category.from_str(entry["category"]),
                jats_xml_path=entry["jatsxml"],
                abstract=entry["abstract"],
                published=entry["published"],
                server=entry["server"],
            )
        except KeyError as e:
            raise MissingFieldError(f"{e}")
        else:
            return result

    def __repr__(self) -> str:
        return """Result(doi={}, title={}, authors={}, author_corresponding={},
                         author_corresponding_institution={}, date={}, version={},
                         category={}, jats_xml_path={}, abstract={}, published={}, server={})""".format(
            self.doi,
            self.title,
            self.authors,
            self.author_corresponding,
            self.author_corresponding_institution,
            self.date,
            self.version,
            self.category,
            self.jats_xml_path,
            self.abstract,
            self.published,
            self.server,
        )

    def __eq__(self, other) -> bool:
        if isinstance(other, Result):
            return self.doi == other.doi
        return False

    def get_short_id(self) -> str:
        """
        Returns the short ID for this result.

        + If the result URL is `"http://arxiv.org/abs/2107.05580v1"`,
        `result.get_short_id()` returns `2107.05580v1`.

        + If the result URL is `"http://arxiv.org/abs/quant-ph/0201082v1"`,
        `result.get_short_id()` returns `"quant-ph/0201082v1"` (the pre-March
        2007 arXiv identifier format).

        For an explanation of the difference between arXiv's legacy and current
        identifiers, see [Understanding the arXiv
        identifier](https://arxiv.org/help/arxiv_identifier).
        """
        return self.doi

    async def get_pdf_url(self, session: aiohttp.ClientSession) -> str:
        doi_base = "https://doi.org"
        self.entry_id = f"{doi_base}/{self.doi}"

        async with session.get(self.entry_id, headers=self.headers) as response:
            content_path = f"{response.url}.pdf"
            await asyncio.sleep(0.001)
            return content_path

    def _get_default_filename(self, extension: str = "pdf") -> str:
        """
        A default `to_filename` function for the extension given.
        """
        nonempty_title = self.title if self.title else "UNTITLED"
        # Remove disallowed characters.
        clean_title = "_".join(re.findall(r"\w+", nonempty_title))
        return "{}.{}.{}".format(self.get_short_id(), clean_title, extension)

    async def download_pdf(
        self,
        session: aiohttp.ClientSession,
        dirpath: Path = Path("."),
        filename: str = "",
    ) -> Path:
        """
        Downloads the PDF for this result to the specified directory.

        The filename is generated by calling `to_filename(self)`.
        """
        if isinstance(dirpath, str):
            dirpath = Path(dirpath)

        if not filename:
            filename = self._get_default_filename()

        path = dirpath / filename

        self.pdf_url = await self.get_pdf_url(session)
        logger.info(f"Downloading: {filename}")
        async with session.get(
            self.pdf_url, headers=self.headers, raise_for_status=True
        ) as response:
            async with aiofiles.open(path, "wb") as f:
                async for chunk in response.content.iter_chunked(1024):
                    await asyncio.sleep(0.001)
                    await f.write(chunk)

        return path

    @staticmethod
    def _to_datetime(ts: time.struct_time) -> datetime:
        """
        Converts a UTC time.struct_time into a time-zone-aware datetime.

        This will be replaced with feedparser functionality [when it becomes
        available](https://github.com/kurtmckee/feedparser/issues/212).
        """
        return datetime.fromtimestamp(timegm(ts), tz=timezone.utc)


class MissingFieldError(Exception):
    """
    An error indicating an entry is unparseable because it lacks required
    fields.
    """

    missing_field: str
    """The required field missing from the would-be entry."""
    message: str
    """Message describing what caused this error."""

    def __init__(self, missing_field):
        self.missing_field = missing_field
        self.message = "Entry from BiorXiv missing required info"

    def __repr__(self) -> str:
        return "{}({})".format(_classname(self), repr(self.missing_field))


class SortCriterion(Enum):
    """
    A SortCriterion identifies a property by which search results can be
    sorted.

    See [the arXiv API User's Manual: sort order for return
    results](https://arxiv.org/help/api/user-manual#sort).
    """

    Relevance = "relevance"
    LastUpdatedDate = "lastUpdatedDate"
    SubmittedDate = "submittedDate"


class SortOrder(Enum):
    """
    A SortOrder indicates order in which search results are sorted according
    to the specified arxiv.SortCriterion.

    See [the arXiv API User's Manual: sort order for return
    results](https://arxiv.org/help/api/user-manual#sort).
    """

    Ascending = "ascending"
    Descending = "descending"


class Search(BaseModel):
    """
    A specification for a search of arXiv's database.

    To run a search, use `Search.run` to use a default client or `Client.run`
    with a specific client.
    """

    start_date: Optional[str] = None
    end_date: Optional[str] = None
    days: Optional[int] = None
    server: str
    max_results: float
    """
    The maximum number of results to be returned in an execution of this
    search.

    To fetch every result available, set `max_results=float('inf')`.
    """

    sort_by: SortCriterion = SortCriterion.Relevance
    """The sort criterion for results."""
    sort_order: SortOrder = SortOrder.Descending
    """The sort order for results."""

    def __repr__(self) -> str:
        return "Search(start-date={}, end-date={}, days={}, max_results={})".format(
            self.start_date,
            self.end_date,
            self.days,
            self.max_results,
        )

    # async def _result(
    #     self,
    #     offset: int,
    # ):
    #     async with aiohttp.ClientSession() as session:
    #         results = list(Client().results(self, offset))
    #         tasks = []
    #         for result in results:
    #             tasks.append(result.download_pdf(session))

    #         await asyncio.gather(*tasks)
    #         return results

    # def results(self, offset: int = 0):
    #     """
    #     Executes the specified search using a default arXiv API client.

    #     For info on default behavior, see `Client.__init__` and `Client.results`.
    #     """

    #     return asyncio.run(self._result(offset))

    def results(self, offset: int = 0) -> t.Generator[Result, None, None]:
        """
        Executes the specified search using a default arXiv API client.

        For info on default behavior, see `Client.__init__` and `Client.results`.
        """
        return Client().results(self, offset=offset)


class Client(BaseModel):
    """
    Specifies a strategy for fetching results from arXiv's API.

    This class obscures pagination and retry logic, and exposes
    `Client.results`.

    query_url_format = "http://export.arxiv.org/api/query?{}"
    The arXiv query API endpoint format.
    page_size: int
    Maximum number of results fetched in a single API request.
    delay_seconds: int
    Number of seconds to wait between API requests.
    num_retries: int
    Number of times to retry a failing API request.
    _last_request_dt: datetime
    """

    biorxiv_api: str = "https://api.biorxiv.org/details/biorxiv"
    delay_seconds: int = 3
    num_retries: int = 3
    _last_request_dt: Optional[datetime] = None

    def __repr__(self) -> str:
        return "Client(delay_seconds={}, num_retries={})".format(
            self.delay_seconds,
            self.num_retries,
        )

    def results(self, search: Search, offset: int = 0):
        """
        Uses this client configuration to fetch one page of the search results
        at a time, yielding the parsed `Result`s, until `max_results` results
        have been yielded or there are no more search results.

        If all tries fail, raises an `UnexpectedEmptyPageError` or `HTTPError`.

        Setting a nonzero `offset` discards leading records in the result set.
        When `offset` is greater than or equal to `search.max_results`, the full
        result set is discarded.

        For more on using generators, see
        [Generators](https://wiki.python.org/moin/Generators).
        """

        # total_results may be reduced according to the feed's
        total_results = search.max_results
        entries = self._request(self._format_url(search))

        for entry in entries["collection"]:
            if offset < total_results:
                entry_result = Result.from_api_entry(entry)
                total_results -= 1
                yield entry_result
            else:
                break

    @tenacity.retry(
        wait=tenacity.wait_exponential(multiplier=1, min=4, max=10),
        stop=tenacity.stop_after_attempt(5),
        reraise=True,
    )
    def _request(self, url) -> dict[str, Any]:
        response = requests.get(url)
        response.raise_for_status()
        content = response.content.strip().decode()
        content = json.loads(content)
        return content

    def _format_url(self, search: Search) -> str:
        """
        Construct a request API for search that returns up to `page_size`
        results starting with the result at index `start`.
        """

        return (
            f"{self.biorxiv_api}/{search.days}d"
            if search.days is not None
            else f"{self.biorxiv_api}/{search.start_date}/{search.end_date}"
        )


class ArxivError(Exception):
    """This package's base Exception class."""

    url: str
    """The feed URL that could not be fetched."""
    retry: int
    """
    The request try number which encountered this error; 0 for the initial try,
    1 for the first retry, and so on.
    """
    message: str
    """Message describing what caused this error."""

    def __init__(self, url: str, retry: int, message: str):
        """
        Constructs an `ArxivError` encountered while fetching the specified URL.
        """
        self.url = url
        self.retry = retry
        self.message = message
        super().__init__(self.message)

    def __str__(self) -> str:
        return "{} ({})".format(self.message, self.url)


class UnexpectedEmptyPageError(ArxivError):
    """
    An error raised when a page of results that should be non-empty is empty.

    This should never happen in theory, but happens sporadically due to
    brittleness in the underlying arXiv API; usually resolved by retries.

    See `Client.results` for usage.
    """

    def __init__(self, url: str, retry: int):
        """
        Constructs an `UnexpectedEmptyPageError` encountered for the specified
        API URL after `retry` tries.
        """
        self.url = url
        super().__init__(url, retry, "Page of results was unexpectedly empty")

    def __repr__(self) -> str:
        return "{}({}, {})".format(_classname(self), repr(self.url), repr(self.retry))


class HTTPError(ArxivError):
    """
    A non-200 status encountered while fetching a page of results.

    See `Client.results` for usage.
    """

    status: int
    """The HTTP status reported by feedparser."""
    entry: feedparser.FeedParserDict
    """The feed entry describing the error, if present."""

    def __init__(self, url: str, retry: int, feed: feedparser.FeedParserDict):
        """
        Constructs an `HTTPError` for the specified status code, encountered for
        the specified API URL after `retry` tries.
        """
        self.url = url
        self.status = feed.status
        # If the feed is valid and includes a single entry, trust it's an
        # explanation.
        if not feed.bozo and len(feed.entries) == 1:
            self.entry = feed.entries[0]
        else:
            self.entry = None
        super().__init__(
            url,
            retry,
            "Page request resulted in HTTP {}: {}".format(
                self.status,
                self.entry.summary if self.entry else None,
            ),
        )

    def __repr__(self) -> str:
        return "{}({}, {}, {})".format(
            _classname(self), repr(self.url), repr(self.retry), repr(self.status)
        )


def _classname(o):
    """A helper function for use in __repr__ methods: arxiv.Result.Link."""
    return "{}".format(o.__class__.__qualname__)
