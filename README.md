# Courses

Your typical courses platform.

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

3. Add this to a `.env` file in the root directory

   ```bash
   FLASK_APP=src # Specify the module that contains the app factory
   # i.e. the create_app function
   FLASK_DEBUG=1 # Enable debug mode by default
   SECRET_KEY=some-strong-random-key
   ```

4. Initialize the db (be sure to be in the root directory)

   ```bash
   uv run flask init-db
   ```

5. Run the app (also in the root directory)

   ```bash
   uv run flask
   ```
