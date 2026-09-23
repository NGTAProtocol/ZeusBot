"""GitHub REST API ingestion into a Snapshot.

Only repository metadata is read through the API. Repository code is never
cloned or executed (Directive §21).
"""

from __future__ import annotations

import os
import re
from datetime import datetime, timedelta, timezone
from typing import Any

import httpx

from ghimoney.methodology import Methodology
from ghimoney.snapshot import Response, Snapshot

API_ROOT = "https://api.github.com"
API_VERSION = "2022-11-28"
SOURCE = "github-rest-api"
TARGET_RE = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9-]{0,38})/[A-Za-z0-9._-]{1,100}$")


class IngestionError(RuntimeError):
    pass


class RateLimitError(IngestionError):
    pass


def validate_target(target: str) -> str:
    if not TARGET_RE.match(target) or target.split("/")[1] in {".", ".."}:
        raise IngestionError(f"invalid repository name {target!r}, expected owner/repository")
    return target


def _utc_now() -> datetime:
    return datetime.now(timezone.utc).replace(microsecond=0)


def iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def default_client(token: str | None = None) -> httpx.Client:
    token = token if token is not None else os.environ.get("GITHUB_TOKEN")
    headers = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": API_VERSION,
               "User-Agent": "ghimoney-impact-engine"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return httpx.Client(base_url=API_ROOT, headers=headers, timeout=30.0)


def _next_link(resp: httpx.Response) -> str | None:
    return resp.links.get("next", {}).get("url")


def _check_rate_limit(resp: httpx.Response) -> None:
    if resp.status_code in (403, 429) and resp.headers.get("x-ratelimit-remaining") == "0":
        raise RateLimitError(
            f"GitHub API rate limit exhausted (reset at epoch {resp.headers.get('x-ratelimit-reset')}); "
            "set GITHUB_TOKEN or retry later"
        )


def _json_or_none(resp: httpx.Response) -> Any:
    if not resp.content:
        return None
    try:
        return resp.json()
    except ValueError:
        return None


class GitHubIngestor:
    def __init__(self, methodology: Methodology, client: httpx.Client | None = None):
        self.m = methodology.ingestion
        self.client = client or default_client()

    def _get(self, endpoint: str, params: dict[str, Any] | None = None,
             max_pages: int = 1) -> Response:
        resp = self.client.get(endpoint, params=params)
        _check_rate_limit(resp)
        body = _json_or_none(resp)
        if resp.status_code != 200 or max_pages <= 1 or not isinstance(body, list):
            return Response(endpoint=_describe(endpoint, params), status=resp.status_code, body=body)
        items, pages, nxt = list(body), 1, _next_link(resp)
        while nxt and pages < max_pages:
            resp = self.client.get(nxt)
            _check_rate_limit(resp)
            if resp.status_code != 200:
                raise IngestionError(f"pagination of {endpoint} failed with HTTP {resp.status_code}")
            items.extend(resp.json())
            pages += 1
            nxt = _next_link(resp)
        return Response(endpoint=_describe(endpoint, params), status=200, body=items,
                        pages=pages, truncated=nxt is not None)

    def fetch(self, target: str, as_of: datetime | None = None) -> Snapshot:
        validate_target(target)
        as_of = as_of or _utc_now()
        since = iso(as_of - timedelta(days=self.m.window_days))
        base = f"/repos/{target}"
        pp = self.m.per_page

        responses: dict[str, Response] = {"repo": self._get(base)}
        if responses["repo"].status != 200:
            raise IngestionError(f"repository {target} not readable: HTTP {responses['repo'].status}")

        responses["latest_commit"] = self._get(f"{base}/commits", {"per_page": 1})
        responses["commits_window"] = self._get(
            f"{base}/commits", {"since": since, "until": iso(as_of), "per_page": pp},
            max_pages=self.m.max_pages_commits)
        responses["releases"] = self._get(f"{base}/releases", {"per_page": pp},
                                          max_pages=self.m.max_pages_releases)
        responses["contributors"] = self._get(f"{base}/contributors", {"per_page": pp},
                                              max_pages=self.m.max_pages_contributors)
        responses["community_profile"] = self._get(f"{base}/community/profile")
        responses["workflows"] = self._get(f"{base}/actions/workflows", {"per_page": 1})
        responses["security_advisories"] = self._get(f"{base}/security-advisories", {"per_page": pp})
        for path in self.m.security_policy_paths:
            responses[f"security_policy:{path}"] = self._get(f"{base}/contents/{path}")

        return Snapshot(target=target, source=SOURCE, as_of=iso(as_of), api_version=API_VERSION,
                        responses=responses)


def _describe(endpoint: str, params: dict[str, Any] | None) -> str:
    if not params:
        return endpoint
    return endpoint + "?" + "&".join(f"{k}={params[k]}" for k in sorted(params))
