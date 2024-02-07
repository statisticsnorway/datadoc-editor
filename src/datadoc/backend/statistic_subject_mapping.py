from __future__ import annotations

from dataclasses import dataclass

import bs4
import requests
from bs4 import BeautifulSoup
from bs4 import ResultSet


@dataclass
class SecondarySubject:
    """Data structure for secondary subjects or 'delemne'."""

    titles: dict[str, str]
    subject_code: str
    statistic_short_names: list[str]


@dataclass
class PrimarySubject:
    """Data structure for primary subjects or 'hovedemne'."""

    titles: dict[str, str]
    subject_code: str
    secondary_subjects: list[SecondarySubject]


class StatisticSubjectMapping:
    """Allow mapping between statistic short name and primary and secondary subject."""

    def __init__(self, source_url: str) -> None:
        """Retrieves the statistical structure document from the given URL.

        Initializes the mapping dicts. Based on the values in the statistical structure document.
        """
        self.source_url = source_url
        self.secondary_subject_primary_subject_mapping: dict[str, str] = {"al03": "al"}
        self.statistic_short_name_secondary_subject_mapping: dict[str, str] = {
            "nav_statres": "al03",
        }
        self._statistic_subject_structure_xml = self._fetch_statistical_structure(
            self.source_url,
        )
        self.primary_subjects: list[
            PrimarySubject
        ] = self._parse_statistic_subject_structure_xml(
            self._statistic_subject_structure_xml,
        )

    def get_primary_subject(self, statistic_short_name: str) -> str | None:
        """Returns the primary subject for the given statistic short name by mapping it through the secondary subject.

        Looks up the secondary subject for the statistic short name, then uses that
        to look up the corresponding primary subject in the mapping dict.

        Returns the primary subject string if found, else None.
        """
        if seconday_subject := self.get_secondary_subject(statistic_short_name):
            return self.secondary_subject_primary_subject_mapping.get(
                seconday_subject,
                None,
            )

        return None

    def get_secondary_subject(self, statistic_short_name: str) -> str | None:
        """Looks up the secondary subject for the given statistic short name in the mapping dict.

        Returns the secondary subject string if found, else None.
        """
        return self.statistic_short_name_secondary_subject_mapping.get(
            statistic_short_name,
            None,
        )

    @staticmethod
    def _extract_titles(titles_xml: bs4.element.Tag) -> dict[str, str]:
        titles = {}
        for title in titles_xml.find_all("tittel"):
            titles[title["sprak"]] = title.text
        return titles

    @staticmethod
    def _fetch_statistical_structure(source_url: str) -> ResultSet:
        """Fetch statistical structure document from source_url.

        Returns a BeautifulSoup ResultSet.
        """
        response = requests.get(source_url, timeout=30)
        soup = BeautifulSoup(response.text, features="xml")
        return soup.find_all("hovedemne")

    def _parse_statistic_subject_structure_xml(
        self,
        statistical_structure_xml: ResultSet,
    ) -> list[PrimarySubject]:
        primary_subjects: list[PrimarySubject] = []
        for p in statistical_structure_xml:
            secondary_subjects: list[SecondarySubject] = [
                SecondarySubject(
                    self._extract_titles(s.titler),
                    s["emnekode"],
                    [statistikk["kortnavn"] for statistikk in s.find_all("Statistikk")],
                )
                for s in p.find_all("delemne")
            ]

            primary_subjects.append(
                PrimarySubject(
                    self._extract_titles(p.titler),
                    p["emnekode"],
                    secondary_subjects,
                ),
            )
        return primary_subjects