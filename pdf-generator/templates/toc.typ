// ═══════════════════════════════════════════════════════════════════════════════
// toc.typ — Table des matières personnalisée
// ═══════════════════════════════════════════════════════════════════════════════

// ---------------------------------------------------------------------------
// Style de la table des matières
// ---------------------------------------------------------------------------
#let custom-toc(
  title: "Table des Matières",
  title-size: 24pt,
  accent-color: rgb("#1E3A5F"),
  depth: 3,
) = {
  // Titre de la table des matières
  align(center)[
    #text(
      size: title-size,
      weight: "bold",
      fill: accent-color,
      title,
    )
  ]

  v(1cm)

  // Ligne décorative
  line(
    length: 100%,
    stroke: 1pt + accent-color.lighten(70%),
  )

  v(1cm)

  // Contenu de la TOC avec styles personnalisés
  show outline.entry.where(level: 1): it => {
    v(8pt)
    strong(it)
  }

  show outline.entry.where(level: 2): it => {
    h(15pt)
    it
  }

  show outline.entry.where(level: 3): it => {
    h(30pt)
    text(size: 10pt, it)
  }

  outline(
    title: none,
    depth: depth,
    indent: auto,
  )

  pagebreak()
}

// ---------------------------------------------------------------------------
// Table des matières pour la version consolidée (avec volumes)
// ---------------------------------------------------------------------------
#let consolidated-toc(
  title: "Table des Matières Générale",
  title-size: 28pt,
  volumes: (),
) = {
  // Titre
  align(center)[
    #text(
      size: title-size,
      weight: "bold",
      fill: rgb("#1E3A5F"),
      title,
    )
  ]

  v(1cm)

  // Ligne décorative
  line(
    length: 100%,
    stroke: 2pt + rgb("#CCCCCC"),
  )

  v(1cm)

  // Liste des volumes comme sommaire
  for v in volumes [
    #box(
      width: 100%,
      inset: (y: 8pt),
      [
        #box(
          inset: (x: 12pt, y: 6pt),
          radius: 4pt,
          fill: v.color,
          text(
            size: 11pt,
            weight: "bold",
            fill: white,
            [Volume #v.number],
          ),
        )
        #h(12pt)
        #text(
          size: 14pt,
          weight: "bold",
          fill: v.color,
          v.title,
        )
        #box(width: 1fr, repeat[.])
        #text(
          size: 11pt,
          fill: rgb("#666666"),
          [p. #v.start-page],
        )
      ],
    )
  ]

  v(1cm)

  // Ligne décorative
  line(
    length: 100%,
    stroke: 1pt + rgb("#CCCCCC"),
  )

  v(1cm)

  // Table des matières détaillée
  show outline.entry.where(level: 1): it => {
    v(6pt)
    strong(it)
  }

  show outline.entry.where(level: 2): it => {
    h(12pt)
    it
  }

  show outline.entry.where(level: 3): it => {
    h(24pt)
    text(size: 9.5pt, it)
  }

  outline(
    title: none,
    depth: 3,
    indent: auto,
  )

  pagebreak()
}

// ---------------------------------------------------------------------------
// En-tête de partie (pour les divisions au sein d'un volume)
// ---------------------------------------------------------------------------
#let part-header(
  number: "1",
  title: "Titre de la Partie",
  accent-color: rgb("#1E3A5F"),
) = {
  pagebreak()

  v(30%)

  align(center)[
    #text(
      size: 14pt,
      weight: "bold",
      fill: accent-color.lighten(30%),
      tracking: 3pt,
      [PARTIE #number],
    )

    #v(1cm)

    #line(
      length: 20%,
      stroke: 2pt + accent-color,
    )

    #v(1cm)

    #text(
      size: 24pt,
      weight: "bold",
      fill: accent-color,
      title,
    )
  ]

  pagebreak()
}
