# 4. package manager selection

Date: 2024-05-07

## Status

Accepted

## Context

### Why Use a Package Manager:

A package manager simplifies the process of installing, managing, and updating software dependencies in a project. It ensures consistency across development environments and helps avoid version conflicts. Key reasons to use a package manager include:

- **Dependency Management**: Ensures that all project dependencies are installed and managed consistently across different environments.
- **Version Control**: Allows for specifying exact versions of dependencies, ensuring reproducibility and stability of the project.
- **Isolation**: Provides isolated environments for different projects, preventing conflicts between dependencies.
- **Ease of Installation**: Simplifies the process of installing and updating dependencies, reducing manual effort and potential errors.
- **Community Support**: Many package managers have large communities and ecosystems, providing access to a wide range of third-party libraries and tools.

### Pros and Cons of Various Package Managers:

#### pip:

**Pros:**
- Widely used and well-supported package manager for Python.
- Simple and straightforward to use, with a large ecosystem of packages available on PyPI.
- Integrates seamlessly with Python's standard library and development workflows.

**Cons:**
- Lack of built-in features for managing virtual environments and dependency resolution.
- Dependency tracking is manual, requiring developers to manage dependencies themselves.

#### poetry:

**Pros:**
- Simplifies dependency management and project configuration with a `pyproject.toml` file.
- Supports dependency resolution and deterministic builds, ensuring consistent environments.
- Provides features for managing virtual environments and packaging projects for distribution.

**Cons:**
- Still relatively new compared to other package managers, with potentially limited community support for some features.
- Requires developers to learn a new configuration format and workflow compared to traditional `setup.py` files.

#### conda:

**Pros:**
- Supports managing both Python and non-Python dependencies, making it suitable for data science and scientific computing projects.
- Provides a way to create isolated environments and install packages from its own repositories.
- Works across different platforms and operating systems, ensuring consistent behavior.

**Cons:**
- Larger installation footprint compared to other package managers, as it includes its own package repository and dependencies.
- Limited support for Python-only projects and packages compared to `pip`.

#### pipenv:

**Pros:**
- Combines package management (pip) and virtual environment management (virtualenv) into a single tool.
- Simplifies dependency management with `Pipfile` and `Pipfile.lock` files, ensuring deterministic builds.
- Provides commands for managing virtual environments and installing/updating dependencies.

**Cons:**
- Adds complexity compared to basic virtual environment tools like `virtualenv` or `venv`.
- Slower initialization and installation times due to dependency resolution.
- Limited support for Python 2 and older projects.

#### pipx:

**Pros:**
- Installs and runs Python applications in isolated environments, preventing conflicts between packages.
- Provides a way to run applications globally from the command line, making it easy to access installed tools.
- Simplifies installation and management of Python-based command-line tools.

**Cons:**
- Limited to installing command-line tools and applications, rather than general-purpose Python packages.
- Requires developers to manually manage dependencies for each installed application.


## Decision


Given the evaluation criteria provided, the choice of package manager depends on various factors such as code readability, solution architecture, testing strategy, performance, maintainability, and extensibility. Based on these criteria:

- **Code Readability**: Poetry and pipenv provide clear and structured dependency management, improving code readability compared to plain `pip` requirements files.
- **Solution Architecture and Code Design**: Poetry and conda offer features for managing project dependencies and packaging projects, which can contribute to better solution architecture and code design.
- **Testing Strategy**: All package managers support managing dependencies for testing. However, tools like Poetry and pipenv offer features for deterministic builds, ensuring consistent testing environments.
- **Performance of the Solution**: The performance impact of the package manager itself is minimal. However, tools like pipenv and poetry may have slightly longer initialization and installation times due to dependency resolution.
- **Maintainability and Extensibility**: Poetry and pipenv simplify dependency management and project configuration, making it easier to maintain and extend projects over time.

Considering these criteria, **Poetry** stands out as a strong choice for the project. It offers a modern and feature-rich approach to dependency management, ensuring code readability, solution architecture, testing strategy, performance, maintainability, and extensibility. Additionally, its deterministic builds feature ensures consistency and reliability across different environments.


## Consequences

The consequences using **Poetry** as the package manager for the project are as follows:
1. Simplified Dependency Management: Poetry simplifies the process of managing dependencies, ensuring consistent environments across different systems.
2. Conflict Resolution: Poetry helps avoid dependency conflicts by providing deterministic builds and version resolution.
3. Steeper learning curve: Developers may need to learn a new configuration format and workflow compared to traditional `setup.py` files.
