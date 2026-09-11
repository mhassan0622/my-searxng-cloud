name: Auto Web Data Scraper

on:
  schedule:
    - cron: '0 * * * *'
  workflow_dispatch:

jobs:
  scrape-web:
    runs-on: ubuntu-latest
    permissions:
      contents: write

    steps:
      - name: Checkout Code
        uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.10'

      - name: Install Libraries
        run: |
          python -m pip install --upgrade pip
          pip install requests

      - name: Run Web Scraper
        run: python scraper.py

      - name: Pull, Commit and Push data.json
        run: |
          git config --global user.name "github-actions[bot]"
          git config --global user.email "github-actions[bot]@users.noreply.github.com"
          git pull --rebase origin main
          git add data.json
          git commit -m "Updated web media catalog [skip ci]" || exit 0
          git push origin main
