# Code Architecture

This document outlines the high-level architecture of the `photo_reader` application.

## High-Level Component Diagram

```mermaid
classDiagram
    %% Entry Points (Represented as classes)
    class GUI
    class CLI
    
    %% Main Logic Modules
    class MicroscopeBase
    class SpinningDisk
    class Eva
    class Photo
    class Wells
    class Validators
    class Utils

    %% Relationships
    GUI ..> MicroscopeBase
    CLI ..> MicroscopeBase
    SpinningDisk --|> MicroscopeBase
    Eva --|> MicroscopeBase

    MicroscopeBase --> Photo
    MicroscopeBase --> Wells
    MicroscopeBase --> Validators
    MicroscopeBase --> Utils
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
