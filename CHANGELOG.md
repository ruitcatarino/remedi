# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

TL;DR for [Keep a changelog](https://keepachangelog.com/en/1.1.0/):

- One section per release with respective date and `[YANKED]` marker for bad releases;
- Releases are listed chronologically in reverse order (most recent at the top);
- All dates in `YYYY-MM-DD` format;
- There's an `[Unreleased]` section at the top for changes that will go into the next release;
- Changes should be grouped into the following categories (represented as subsections under each version):

  - **Added** for new features.
  - **Changed** for changes in existing functionality.
  - **Deprecated** for soon-to-be removed features.
  - **Removed** for now removed features.
  - **Fixed** for any bug fixes.
  - **Security** in case of vulnerabilities.

## [Unreleased]

### Changed
- Cleaned and improved endpoints in general
- Increase test coverage

## [0.0.1-alpha] - 2025-05-30

### Added
- Register, Get/Filter, Update, and Delete endpoints for User/Auth and Person
- Register and partial Get endpoints for Medication
- Get endpoint for Medication Schedules
- Early-stage tests
- Background jobs to generate future schedules, notify about missed schedules, and handle missed medications
- CI/CD pipeline to test the codebase on each push to main and publish Docker images on each tag
- Database migration handling using [aerich](https://github.com/tortoise/aerich) and [Tortoise ORM](https://github.com/tortoise/tortoise-orm) as the ORM