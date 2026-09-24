# GHIMONEY Impact Report: NGTAProtocol/Roadmemo

> Provisional result of methodology `GHIM-IMPACT-0.2`. Weights and anchors are hypotheses. No human review was performed and this result is not used for funding.

## Summary

| Output | Value |
|---|---|
| Impact | **INSUFFICIENT_EVIDENCE**: no final Impact Score |
| Evidence Coverage | 35% |
| Confidence | 77% (base 77%, risk factor 1.00) |
| Risk | LOW (0 signal(s)) |

Impact, Coverage, Confidence and Risk are independent outputs: Coverage, Confidence and Risk never change the Impact Score.

### Why there is no Impact Score

- coverage 0.35 below minimum 0.60
- 2 core dimension(s) missing (adoption, dependency), maximum 1

## Dimensions

| Dimension | Original weight | Recalculated weight | Status | Score | Metric coverage | Confidence |
|---|---|---|---|---|---|---|
| adoption | 25% | — | NOT_AVAILABLE | — | 0% | — |
| dependency | 25% | — | INSUFFICIENT_EVIDENCE | — | 0% | — |
| maintenance | 15% | — | INSUFFICIENT_EVIDENCE | — | 40% | — |
| quality | 15% | — | VERIFIED | 0.0 | 50% | 80% |
| security | 10% | — | VERIFIED | 0.0 | 100% | 60% |
| community | 10% | — | VERIFIED | 0.0 | 100% | 90% |

**Missing dimensions:** adoption, dependency, maintenance. Missing dimensions are not counted as zero.

## Risk

No risk signal triggered.

A risk signal is an anomaly to be reviewed, not evidence of fraud.
Checks not evaluated for lack of data: commit_burst, author_concentration.

## Evidence

| Metric | Availability | Raw value | Normalized | Method | Confidence | Note |
|---|---|---|---|---|---|---|
| ci_workflows_present | UNKNOWN | — | — | boolean | — | no GitHub Actions workflows: CI may run on another service, so absence is not evidence of no CI |
| commits_last_365d | VERIFIED | 0 | 0.0 | log_saturating(anchor=500) | 90% | empty repository |
| community_profile_files | VERIFIED | 0.00 | 0.0 | fraction | 80% | present: none |
| days_since_last_commit | NOT_APPLICABLE | — | — | log_decay(anchor=365) | — | empty repository: no commit exists |
| distinct_authors_last_365d | VERIFIED | 0 | 0.0 | log_saturating(anchor=50) | 90% |  |
| releases_last_365d | UNKNOWN | — | — | log_saturating(anchor=12) | — | no GitHub Releases: the project may release through tags or package registries, so absence is not evidence of zero releases |
| security_policy_present | VERIFIED | False | 0.0 | boolean | 60% | no SECURITY.md in: SECURITY.md, .github/SECURITY.md, docs/SECURITY.md |
| signal.forks_count | VERIFIED | 0 | — | signal: recorded, not scored | 90% |  |
| signal.max_commit_window_share | NOT_APPLICABLE | — | — | signal: recorded, not scored | — | no commits in window |
| signal.published_security_advisories | VERIFIED | 0 | — | signal: recorded, not scored | 90% | recorded only: advisories show a disclosure process as much as a weakness |
| signal.repository_age_days | VERIFIED | 66.92 | — | signal: recorded, not scored | 80% |  |
| signal.stargazers_count | VERIFIED | 0 | — | signal: recorded, not scored | 90% |  |
| signal.subscribers_count | VERIFIED | 0 | — | signal: recorded, not scored | 90% |  |
| signal.top_author_share_last_365d | NOT_APPLICABLE | — | — | signal: recorded, not scored | — | no commits in window |
| total_contributors | VERIFIED | 0 | 0.0 | log_saturating(anchor=200) | 90% | empty repository |

## Reproducibility

- Project ID: `ghp-839ec4726f0897b8` (GitHub repository id 1305924435)
- Methodology: `GHIM-IMPACT-0.2`, config `0.2.0`, hash `a33b51b0fb7c95b552f52066a379be6b3adf1491577d6eaed2c0e5246a6303df`
- Snapshot: `673bfbc551c97708` as of 2026-09-24T16:05:04Z, hash `673bfbc551c97708a501bd9f1542781689db86a5820b097db3f8c1066f26d76d`
- Sources: github-rest-api (2022-11-28)
- Report hash: `e5acb8ca4fec0a0105e3ff270d71e725776916272481dacbf530c09423544770`

Same snapshot + same methodology + same configuration produce the same report.
