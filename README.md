# C++ Testing Skill

A specialized skill for generalized C++ project testing. This skill helps analyze C++ project structures, identify critical functions, and generate targeted test code using frameworks like GoogleTest and Catch2.

## Features

- **Project Analysis**: Scans `CMakeLists.txt`, headers, and source files to build a module model.
- **Function Categorization**: Automatically identifies key functions (Protocol, Business, Network, Utilities) and assigns test priorities.
- **Test Generation**: Provides templates and patterns for boundary testing, async code, and mocking.
- **Automated Scripts**: Includes Python scripts for project-wide analysis and function finding.

## Repository Structure

- `SKILL.md`: The core skill definition and workflow.
- `scripts/`: Python tools for automated analysis.
- `references/`: Detailed guides on workflows, categorization, and test patterns.

## Getting Started

1. Ensure you have Python 3.x installed.
2. Use this skill with AI coding assistants (like Claude) by referencing the `SKILL.md` file.
3. Run `python scripts/analyze_project.py <your_project_path>` to start.

## License

MIT License
