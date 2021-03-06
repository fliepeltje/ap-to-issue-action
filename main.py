# -*- coding: utf-8 -*-
"""Convert meeting actions to GitHub issues."""

import os
import requests
import re
from dataclasses import dataclass
from time import sleep

BASE_URL = "https://api.github.com/repos/"
REPO = os.environ.get("INPUT_REPO")
TOKEN = os.environ.get("INPUT_TOKEN")
PREV_COMMIT = os.environ.get("INPUT_BEFORE")
SHA = os.environ.get("INPUT_SHA")
LOOKUP_TABLE_STRING = os.environ.get("INPUT_LOOKUP_TABLE")
LOOKUP_TABLE_ITER = (x.partition("=") for x in LOOKUP_TABLE_STRING.split())
LOOKUP_TABLE = {k.lower().strip(): v.strip() for k, _, v in LOOKUP_TABLE_ITER}
COLUMN = os.environ.get("INPUT_COLUMN")


@dataclass
class Issue:
    assignees: list[str]
    title: str
    description: str
    high_priority: bool

    @classmethod
    def from_text(cls, issue_text: str) -> "Issue":
        assignee_text, _, issue = issue_text.partition(":")
        title, _, description = issue.replace("\\n", "\n").partition("\n")
        return cls(
            assignees=[x.strip() for x in assignee_text.replace("!", "").split("|")],
            title=title.strip(),
            description=description.strip(),
            high_priority="!" in assignee_text,
        )


def extract_actions(notes: str) -> list[str]:
    return [s for s, _ in re.findall(r"AP\s((.|\n\t|\n\s\s\s\s)*)", notes)]


def get_open_issues(page: int = 1) -> list[dict]:
    issues_response = requests.get(
        url=f"{BASE_URL}{REPO}/issues",
        params={"per_page": 100, "page": page, "state": "open", "labels": "todo"},
        headers={
            "Content-Type": "application/json",
            "Authorization": f"token {TOKEN}",
        },
    )
    if "next" in issues_response.links:
        return issues_response.json() + get_open_issues(page + 1)
    else:
        return issues_response.json()


def get_diff() -> str:
    response = requests.get(
        f"{BASE_URL}{REPO}/compare/{PREV_COMMIT}...{SHA}",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"token {TOKEN}",
        },
    )
    if not response.status_code == 200:
        raise ConnectionError()

    files = response.json()["files"]
    scannable_content = ""
    for f in (f for f in files if f["filename"].endswith(".md")):
        try:
            with open(f["filename"], "r") as modified_file:
                scannable_content += "\n" + modified_file.read()
        except FileNotFoundError:
            print("Notes deleted for file", f["filename"])
    return scannable_content


def create_issue_card(issue_id: int) -> None:
    response = requests.post(
        url=f"{BASE_URL}{REPO}/projects/columns/{COLUMN}/cards",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"token {TOKEN}",
        },
        json={"content_id": issue_id},
    )
    if response.ok:
        print("Moved issue to board")
    else:
        print("Failed ot move issue")
        print(response.json())


def create_issue(issue: Issue) -> None:
    response = requests.post(
        url=f"{BASE_URL}{REPO}/issues",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"token {TOKEN}",
        },
        json={
            "title": issue.title,
            "body": issue.description,
            "labels": ["todo"],
            "assignees": [
                LOOKUP_TABLE[name.lower().strip()] for name in issue.assignees
            ],
        },
    )
    if response.status_code == 201:
        print(f"created issue: {issue}")
        issue_id = response.json()["id"]
        create_issue_card(issue_id)
    else:
        print(f"failed to create issue: {issue}\n\n")
        print(response.json())

    sleep(0.5)


def main():
    existing_issues = get_open_issues()
    diff = get_diff()
    issues = [Issue.from_text(issue_text) for issue_text in extract_actions(diff)]
    existing_issue_titles = set(x["title"] for x in existing_issues)
    to_create = (x for x in issues if x.title not in existing_issue_titles)
    for new_issue in to_create:
        create_issue(new_issue)


if __name__ == "__main__":
    main()
