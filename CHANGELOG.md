# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## [Unreleased]


## [0.1.0] - 2023-05-18

### Added

- Initial release of txt2dub.


## [0.1.1] - 2023-05-18

### Added

- Screenshots and descriptions of `tx2dub` in README.md

### Fixed

- Bottom-docked toolbars not calculating `height: auto` correctly after upgrade to textual@0.25.0, so set a fixed `height: 5`

### Changed

- Bumped textual dependency to 0.25.0


## [0.1.2] - 2023-05-22

### Fixed

- Generate function now works on Mac (#1)
- Crashes in macOS from pyobjc were resolved by downgrading for now

### Changed

- Bumped textual dependency to 0.26.0
- Pinned pyobjc dependency to downgraded 9.0.1 (Darwin only)
