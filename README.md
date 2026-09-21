# DocumentaryForge

**Evidence-First AI Documentary Factory**

## Project identity

Factory project:

`documentaryforge_001`

Factory name:

`DocumentaryForge`

Current test documentary:

`indus_valley_001`

*The Lost Civilization of the Indus Valley*

The Indus Valley documentary is a test production used to validate the
factory. It is not the name or identity of the factory itself.

## Architecture

DocumentaryForge is designed to support many documentary productions.

Each documentary receives its own documentary ID and production state.

The factory is persistent in GitHub; Kaggle is used for execution and GPU
compute.

## Research chain

`source -> evidence -> atomic claim -> corroboration -> script`

## Core rules

- Do not use search-engine HTML scraping as the primary research interface.
- OpenAlex/Crossref records sharing a DOI count as one independent work.
- Abstract/metadata is not full text.
- Wikipedia is orientation/reference unless independently supported.
- Wikimedia Commons search results are not themselves media assets.
- Do not treat environmental change as proof of civilization-wide collapse.
- Do not call the Indus script deciphered without explicit supporting evidence.
- Distinguish exchange evidence from claims about trade scale/organization.
- Preserve outputs and checkpoints after every stage.
