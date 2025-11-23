# Courses

Your typical courses platform.

## Tech Stack

- Flask
- Sqlite3
- Vanilla JS

I am trying to implement as much stuff from scratch as I can,
with the least amount of libraries for this project.

## Setup

1. Clone

   ```bash
   git clone https://github.com/dracotato/courses.git
   # or via shh
   git clone git@github.com:dracotato/courses.git
   ```

2. Install dependencies (with uv)

   > see [uv installation guide](https://docs.astral.sh/uv/getting-started/installation/)
   > for how to install uv

   ```bash
   uv sync
   ```

3. Set environment variables (take a look at `.env.example`)

4. Initialize the db (be sure to be in the root directory, or set the app path manually)

   ```bash
   uv run -- flask init-db
   ```

5. Run the app (also in the root directory, or set the app path manually)

   ```bash
   uv run -- flask run
   ```

## Contributing

Push your branch and open a pull-request.

### Commit Message Format

```bash
<type>(optional scope): <short summary>

[optional body]

[optional footer]

```

#### Type

Can be any of:

- feat. (Introduces a new feature)
- refactor. (Modifies existing code)
- remove. (Deletes a part or entire files)
- fix. (Fixing a bug, visual error, or a security vulnerability)
- docs. (Documentation)
- style. (Cosmetic changes, code formatting, comments, variable renames)
- chore. (Dependency management, gitignore)

#### Scope

It's up to the writer's judgement, here are some examples:

- views.
- config.
- readme.
- ui.
- editor.

#### Summary

Use imperative mode in summary
e.g. add instead of added or adds

Make sure it's less than 72 characters
otherwise use multi-line commits. (see below)

#### Examples

- `feat: add a user table to the schema`
- `refactor: modularize utils`
- `fix(ui): remove extra top margin in the submit button`
- Multi-line commits:

  ```
  # multi-line commit
  refactor(schema): remove the username column in the user table

  # body, explain why
  the app doesn't need unique identification

  # footer, can be useful for metadata
  closes: #122
  ```

  If you need to include more info,
  add an empty line and write whatever you need. (like above)
