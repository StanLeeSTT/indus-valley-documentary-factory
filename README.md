# Indus Valley Documentary Factory

Fresh rebuild. GitHub is the persistent source of truth; Kaggle is the execution/GPU environment.

Project: `indus_valley_001`
Documentary: *The Lost Civilization of the Indus Valley*

Run the pipeline one cell at a time during the first build, then use `scripts/run_all.py` for repeatable runs.

## Research chain
`source -> evidence -> atomic claim -> corroboration -> script`

## Hard rules
- Do not use search-engine HTML scraping as the primary research interface.
- OpenAlex/Crossref records sharing a DOI count as one independent work.
- Abstract/metadata is not full text.
- Wikipedia is orientation/reference unless independently supported.
- Wikimedia Commons search results are not themselves media assets.
- Do not treat environmental change as proof of civilization-wide collapse.
- Do not call the Indus script deciphered without explicit supporting evidence.
- Distinguish exchange evidence from claims about trade scale/organization.
- Preserve outputs and checkpoints after every stage.
