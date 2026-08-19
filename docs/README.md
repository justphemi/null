# CybergateFX &mdash; Analysis-phase documentation

This folder contains the four documents produced for the analysis phase
of the CybergateFX project:

| # | Document                                  | Purpose                                                                                  |
|---|-------------------------------------------|------------------------------------------------------------------------------------------|
| 1 | [`1-user-story.md`](1-user-story.md)         | Personas, user stories in *As a / I want / so that* format, acceptance criteria.       |
| 2 | [`2-use-case.md`](2-use-case.md)             | Use case diagram (Mermaid) + per-use-case description (actor, trigger, flows, exceptions). |
| 3 | [`3-sequence-diagram.md`](3-sequence-diagram.md) | Sequence diagrams (Mermaid) for the three core flows + step-by-step traces.        |
| 4 | [`4-class-diagram.md`](4-class-diagram.md)   | Class diagram (Mermaid), per-class field/method tables, relationship catalogue.        |

## How to view the diagrams

All three diagrams are in [Mermaid](https://mermaid.js.org) syntax. They
render natively on:

- GitHub and GitLab
- The VS Code Markdown preview (`Ctrl+Shift+V`)
- Obsidian, Joplin, Typora and other Markdown editors that ship with
  Mermaid support

If your viewer does not render Mermaid, the diagrams are paired with
plain-text descriptions so you can still read the structure.

## Mapping back to the code

| Doc       | Code locations                                                                                            |
|-----------|-----------------------------------------------------------------------------------------------------------|
| User story| `accounts/views.py`, `mentors/views.py`, `bookings/views.py`                                              |
| Use case  | Each UC ID (e.g. UC-05) maps to a URL pattern in `accounts/urls.py`, `mentors/urls.py`, `bookings/urls.py`. |
| Sequence  | Same as use case; the *actors* are the browser + view + ORM + DB.                                        |
| Class     | `accounts/models.py`, `mentors/models.py`, `bookings/models.py`.                                          |
