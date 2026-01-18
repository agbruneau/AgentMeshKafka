// ═══════════════════════════════════════════════════════════════════════════════
// volume.typ — Template principal pour un volume individuel
// ═══════════════════════════════════════════════════════════════════════════════

// Import des composants
#import "callouts.typ": *
#import "cover.typ": cover-page
#import "toc.typ": custom-toc, part-header

// ═══════════════════════════════════════════════════════════════════════════════
// CONFIGURATION DU DOCUMENT
// Ces variables doivent être définies avant l'import du template
// ═══════════════════════════════════════════════════════════════════════════════

// Variables par défaut (à surcharger)
#let volume-number = "I"
#let volume-title = "Titre du Volume"
#let volume-subtitle = "Sous-titre"
#let volume-color = rgb("#1E3A5F")
#let author = "André-Guy Bruneau"
#let year = "2026"

// ═══════════════════════════════════════════════════════════════════════════════
// TEMPLATE PRINCIPAL
// ═══════════════════════════════════════════════════════════════════════════════

#let volume-template(
  volume-number: "I",
  title: "Titre du Volume",
  subtitle: "Sous-titre",
  accent-color: rgb("#1E3A5F"),
  author: "André-Guy Bruneau",
  year: "2026",
  body,
) = {
  // ---------------------------------------------------------------------------
  // MÉTADONNÉES DU DOCUMENT
  // ---------------------------------------------------------------------------
  set document(
    title: [Volume #volume-number — #title],
    author: author,
    keywords: (
      "entreprise agentique",
      "architecture",
      "agents cognitifs",
      "Apache Kafka",
      "transformation numérique",
    ),
  )

  // ---------------------------------------------------------------------------
  // PAGE DE COUVERTURE
  // ---------------------------------------------------------------------------
  cover-page(
    volume-number: volume-number,
    title: title,
    subtitle: subtitle,
    author: author,
    year: year,
    accent-color: accent-color,
  )

  // ---------------------------------------------------------------------------
  // CONFIGURATION DE PAGE
  // ---------------------------------------------------------------------------
  set page(
    paper: "a4",
    margin: (
      top: 2.5cm,
      bottom: 2.5cm,
      left: 2cm,
      right: 2cm,
    ),
    // En-tête
    header: context {
      if counter(page).get().first() > 2 [
        #set text(size: 9pt, fill: rgb("#666666"))
        #grid(
          columns: (1fr, 1fr),
          align: (left, right),
          [Volume #volume-number — #title],
          [#emph(here().position().page.repr())],
        )
        #v(-4pt)
        #line(length: 100%, stroke: 0.5pt + rgb("#CCCCCC"))
      ]
    },
    // Pied de page
    footer: context {
      if counter(page).get().first() > 2 [
        #align(center)[
          #set text(size: 10pt, fill: rgb("#333333"))
          — #counter(page).display() —
        ]
      ]
    },
    // Numérotation
    numbering: "1",
  )

  // ---------------------------------------------------------------------------
  // TYPOGRAPHIE
  // ---------------------------------------------------------------------------

  // Police principale
  set text(
    font: ("Libertinus Serif", "Linux Libertine", "Times New Roman"),
    size: 11pt,
    lang: "fr",
    region: "CA",
    hyphenate: true,
  )

  // Paragraphes
  set par(
    justify: true,
    leading: 0.65em,
    first-line-indent: 0pt,
  )

  // ---------------------------------------------------------------------------
  // TITRES
  // ---------------------------------------------------------------------------

  // H1 - Titre de chapitre
  show heading.where(level: 1): it => {
    pagebreak(weak: true)
    v(1cm)
    text(
      size: 24pt,
      weight: "bold",
      fill: accent-color,
      it.body,
    )
    v(0.5cm)
    line(length: 30%, stroke: 2pt + accent-color.lighten(50%))
    v(1cm)
  }

  // H2 - Sections
  show heading.where(level: 2): it => {
    v(1cm)
    text(
      size: 18pt,
      weight: "bold",
      fill: rgb("#333333"),
      it.body,
    )
    v(0.5cm)
  }

  // H3 - Sous-sections
  show heading.where(level: 3): it => {
    v(0.8cm)
    text(
      size: 14pt,
      weight: "bold",
      fill: rgb("#444444"),
      it.body,
    )
    v(0.3cm)
  }

  // H4 - Points de détail
  show heading.where(level: 4): it => {
    v(0.5cm)
    text(
      size: 12pt,
      weight: "bold",
      fill: rgb("#555555"),
      it.body,
    )
    v(0.2cm)
  }

  // ---------------------------------------------------------------------------
  // LISTES
  // ---------------------------------------------------------------------------

  set list(
    marker: ([•], [◦], [▪], [▫]),
    indent: 20pt,
    body-indent: 8pt,
  )

  set enum(
    indent: 20pt,
    body-indent: 8pt,
  )

  // ---------------------------------------------------------------------------
  // CODE
  // ---------------------------------------------------------------------------

  // Code inline
  show raw.where(block: false): box.with(
    fill: rgb("#F5F5F5"),
    inset: (x: 3pt, y: 0pt),
    outset: (y: 3pt),
    radius: 2pt,
  )

  // Blocs de code
  show raw.where(block: true): it => {
    set text(font: ("Fira Code", "Consolas", "Monaco"), size: 9pt)
    block(
      width: 100%,
      fill: rgb("#F8F8F8"),
      inset: 12pt,
      radius: 4pt,
      stroke: (left: 3pt + rgb("#CCCCCC")),
      it,
    )
  }

  // ---------------------------------------------------------------------------
  // TABLEAUX
  // ---------------------------------------------------------------------------

  set table(
    stroke: (x, y) => {
      if y == 0 { (bottom: 2pt + rgb("#333333")) }
      else { (bottom: 0.5pt + rgb("#E0E0E0")) }
    },
    fill: (x, y) => {
      if y == 0 { rgb("#F5F5F5") }
      else if calc.rem(y, 2) == 0 { rgb("#FAFAFA") }
    },
    inset: 8pt,
  )

  // ---------------------------------------------------------------------------
  // BLOCKQUOTES (non-callout)
  // ---------------------------------------------------------------------------

  show quote: it => {
    block(
      width: 100%,
      fill: rgb("#FAFAFA"),
      inset: (left: 16pt, right: 12pt, top: 12pt, bottom: 12pt),
      stroke: (left: 4pt + rgb("#CCCCCC")),
      radius: (right: 4pt),
      text(style: "italic", it.body),
    )
  }

  // ---------------------------------------------------------------------------
  // LIENS
  // ---------------------------------------------------------------------------

  show link: it => {
    text(fill: rgb("#1976D2"), it)
  }

  // ---------------------------------------------------------------------------
  // LIGNES HORIZONTALES
  // ---------------------------------------------------------------------------

  show line: it => {
    v(12pt)
    it
    v(12pt)
  }

  // ---------------------------------------------------------------------------
  // TABLE DES MATIÈRES
  // ---------------------------------------------------------------------------

  custom-toc(
    title: "Table des Matières",
    title-size: 24pt,
    accent-color: accent-color,
    depth: 3,
  )

  // ---------------------------------------------------------------------------
  // CONTENU
  // ---------------------------------------------------------------------------

  body
}

// ═══════════════════════════════════════════════════════════════════════════════
// COULEURS PAR VOLUME (référence)
// ═══════════════════════════════════════════════════════════════════════════════

#let volume-colors = (
  "I": rgb("#1E3A5F"),   // Bleu profond
  "II": rgb("#2D5016"),  // Vert forêt
  "III": rgb("#8B4513"), // Brun Kafka
  "IV": rgb("#4A148C"),  // Violet Iceberg
  "V": rgb("#B8860B"),   // Or Renaissance
)
