# Code Architecture

This document outlines the high-level architecture of the `photo_reader` application.

## High-Level Component Diagram

```mermaid
graph TD
    %% Entry Points
    GUI[window.py]
    CLI[split_to_wells.py]

    %% Main Logic Modules
    Base[photo/microscopebase.py]
    Spinning[photo/spinning_disk.py]
    Eva[photo/eva.py]
    Photo[photo/photo.py]
    Wells[photo/wells.py]
    Validators[photo/validators.py]
    Utils[photo/utils.py]

    %% Relationships
    GUI --> Base
    CLI --> Base
    Spinning --|> Base
    Eva --|> Base

    Base --> Photo
    Base --> Wells
    Base --> Validators
    Base --> Utils
```

## Description

- **Entry Points**: 
  - `window.py`: Provides the Graphical User Interface (GUI).
  - `split_to_wells.py`: Provides the Command Line Interface (CLI).
- **Core Logic**:
  - `photo/microscopebase.py`: Defines the `MicroscopeBase` abstract base class, which orchestrates the splitting and moving logic.
  - `photo/spinning_disk.py` & `photo/eva.py`: Concrete implementations of `MicroscopeBase` for specific microscope output formats.
- **Support Modules**:
  - `photo/photo.py`: Represents individual images and handles file copying/renaming.
  - `photo/wells.py`: Defines well positioning and naming conventions.
  - `photo/validators.py`: Provides utilities for validating file and directory paths.
  - `photo/utils.py`: Miscellaneous utility functions.
