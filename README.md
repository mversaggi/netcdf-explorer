

### Generate output.css for Tailwind styling
1. Install Tailwind: `npm install tailwindcss @tailwindcss/cli`
2. Generate output.css: `npx @tailwindcss/cli -i .\static\src\input.css -o .\static\src\output.css`
   1. Add `--watch` after the output path to dynamically generate output.css as CSS changes are made.

### Run App Standalone
1. Install `uv`: https://docs.astral.sh/uv/getting-started/installation/
2. Install Python 3.13: `uv python install 3.13`
3. Run the app: `uv run flask --app "src\netcdf_explorer\app:create_app({'FLASK_ENV':'development'})" run`