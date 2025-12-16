import io
import pytest
from urllib.error import URLError
from bs4 import BeautifulSoup

import arxiv_extract as m


def soup_from_html(html: str) -> BeautifulSoup:
    return BeautifulSoup(html, "html.parser")


class DummyHTTPResponse(io.BytesIO):
    pass


class TestGetPaperInfo:
    def test_extracts_all_fields_when_conference_present(self):
        html = """
        <html><body>
          <h1 class="title mathjax">Title: My Great Paper</h1>
          <div class="authors">Authors: Alice, Bob</div>
          <table>
            <tr><td class="tablecell arxivdoi"><a href="https://doi.org/10.1000/xyz123">doi</a></td></tr>
            <tr><td class="tablecell comments mathjax">Accepted to MICCAI 2023</td></tr>
          </table>
          <div class="dateline">Submitted on 1 Jan 2022</div>
        </body></html>
        """
        info = m.get_paper_info(soup_from_html(html))
        info.implement()

        assert info.get_extracted_info() == (
            " My Great Paper",  
            " Alice, Bob",      
            "https://doi.org/10.1000/xyz123",
            "MICCAI",
            "2023",
        )

    def test_falls_back_to_arxiv_when_conference_is_missing(self):
        html = """
        <html><body>
          <h1 class="title mathjax">Title: Another Paper</h1>
          <div class="authors">Authors: Carol</div>
          <table>
            <tr><td class="tablecell arxivdoi"><a href="https://doi.org/10.1111/aaaa">doi</a></td></tr>
          </table>
          <div class="dateline">Submitted on 12 Dec 2021 (v1), last revised 03 Mar 2022</div>
        </body></html>
        """
        info = m.get_paper_info(soup_from_html(html))
        info.implement()

        title, authors, doi, venue, year = info.get_extracted_info()
        assert title == " Another Paper"
        assert authors == " Carol"
        assert doi == "https://doi.org/10.1111/aaaa"
        assert venue == "Arxiv"
        assert year == "2022"


    def test_falls_back_to_arxiv_when_conference_format_unexpected(self):
        html = """
        <html><body>
          <h1 class="title mathjax">Title: Weird Comments</h1>
          <div class="authors">Authors: Dave</div>
          <table>
            <tr><td class="tablecell arxivdoi"><a href="https://doi.org/10.2222/bbbb">doi</a></td></tr>
            <tr><td class="tablecell comments mathjax">Camera-ready version</td></tr>
          </table>
          <div class="dateline">Submitted on 5 May 2020</div>
        </body></html>
        """
        info = m.get_paper_info(soup_from_html(html))
        info.implement()

        assert info.get_extracted_info() == (
            " Weird Comments",
            " Dave",
            "https://doi.org/10.2222/bbbb",
            "Arxiv",
            "2020",
        )

    def test_raises_if_doi_tag_missing_anchor(self):
        html = """
        <html><body>
          <h1 class="title mathjax">Title: No DOI Link</h1>
          <div class="authors">Authors: Eve</div>
          <table>
            <tr><td class="tablecell arxivdoi">no anchor</td></tr>
          </table>
          <div class="dateline">Submitted on 1 Jan 2019</div>
        </body></html>
        """
        info = m.get_paper_info(soup_from_html(html))
        with pytest.raises(Exception):
            info.implement()


class TestAccessWebExtract:
    def test_returns_extracted_info_with_mocked_urlopen(self, monkeypatch):
        html_bytes = """
        <html><body>
          <h1 class="title mathjax">Title: Networkless Test</h1>
          <div class="authors">Authors: Foo, Bar</div>
          <table>
            <tr><td class="tablecell arxivdoi"><a href="https://doi.org/10.9999/test">doi</a></td></tr>
            <tr><td class="tablecell comments mathjax">Published at CVPR 2024</td></tr>
          </table>
          <div class="dateline">Submitted on 1 Jan 2023</div>
        </body></html>
        """.encode("utf-8")

        def fake_urlopen(url):
            return DummyHTTPResponse(html_bytes)

        monkeypatch.setattr(m, "urlopen", fake_urlopen)

        a = m.access_web_extract("http://example.com", "html.parser")
        extracted = a.implement()

        assert extracted == (
            " Networkless Test",
            " Foo, Bar",
            "https://doi.org/10.9999/test",
            "CVPR",
            "2024",
        )

    def test_urlerror_currently_crashes_due_to_unbound_source_code(self, monkeypatch, capsys):
        def fake_urlopen(url):
            raise URLError("boom")

        monkeypatch.setattr(m, "urlopen", fake_urlopen)

        with pytest.raises(UnboundLocalError):
            m.access_web_extract("http://bad", "html.parser")

        out = capsys.readouterr().out
        assert "This URL can't be accessed" in out
