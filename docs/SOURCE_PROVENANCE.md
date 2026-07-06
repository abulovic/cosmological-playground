# Source provenance and website citation contract

`knowledge/sources.json` is the canonical registry for sources that support public research claims or should appear in the website's source interface. Prose documents may cite a stable source ID and link to the registry rather than maintaining a second, divergent bibliography.

## Required source record

Every record must preserve:

- a stable lowercase ID;
- title, creators, year, source type, and publisher;
- a canonical HTTPS URL and any useful alternate URLs;
- access date and relevant page, chapter, section, or passage locator;
- every project artifact and section in which the source is used;
- review status and limitations;
- a human-readable citation and link label for website display.

Bibliographic discovery records are not substantive evidence. A record with `bibliographic_only` review status may establish that a work exists, but a claim attributed to that work needs the original text or an explicitly identified scholarly secondary source.

## Website behavior

The website should consume `knowledge/sources.json` and:

1. display only records with `website.display: true`;
2. show the supplied citation, link label, source type, and review status;
3. group or filter sources by the analysis section or claim that uses them;
4. disclose when a link is bibliographic-only or when a source is secondary;
5. open canonical source URLs without copying paywalled or copyrighted text;
6. never imply that source inclusion equals scholarly endorsement of the prototype's interpretation.

Cosmology-card claim provenance remains embedded in each versioned card because it must point to exact claims and passages. Card sources may also be promoted into the global registry when they are useful for public browsing; their stable IDs should then match.

## Review workflow

- Add or update the registry record in the same change that introduces a sourced public claim.
- Check the canonical URL and publication metadata at the time of use.
- Record a locator precise enough for a reviewer to find the relevant material.
- Keep sourced fact, project inference, and project decision visibly distinct.
- If a source disappears, retain its citation metadata, mark the link status in review notes, and add an archival or publisher URL when legally available.
