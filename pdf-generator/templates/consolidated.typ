// ═══════════════════════════════════════════════════════════════════════════════
// consolidated.typ — Template pour la monographie complète
// ═══════════════════════════════════════════════════════════════════════════════

// Import des composants
#import "callouts.typ": *
#import "cover.typ": cover-page-consolidated, volume-divider
#import "toc.typ": consolidated-toc

// ═══════════════════════════════════════════════════════════════════════════════
// CONFIGURATION DES VOLUMES
// ═══════════════════════════════════════════════════════════════════════════════

#let volumes-config = (
  (
    number: "I",
    title: "Fondations de l'Entreprise Agentique",
    subtitle: "De l'Interopérabilité à l'Intelligence Distribuée",
    color: rgb("#1E3A5F"),
    start-page: 1,
  ),
  (
    number: "II",
    title: "Infrastructure Agentique",
    subtitle: "Concevoir et Opérer le Maillage d'Événements Intelligent",
    color: rgb("#2D5016"),
    start-page: 0,  // Calculé dynamiquement
  ),
  (
    number: "III",
    title: "Apache Kafka — Guide de l'Architecte",
    subtitle: "Maîtriser la Plateforme de Streaming Événementiel",
    color: rgb("#8B4513"),
    start-page: 0,
  ),
  (
    number: "IV",
    title: "Apache Iceberg — Le Lakehouse Moderne",
    subtitle: "Architecture, Conception et Opérations du Data Lakehouse",
    color: rgb("#4A148C"),
    start-page: 0,
  ),
  (
    number: "V",
    title: "Le Développeur Renaissance",
    subtitle: "Capital Humain et Excellence à l'Ère de l'IA",
    color: rgb("#B8860B"),
    start-page: 0,
  ),
)

// ═══════════════════════════════════════════════════════════════════════════════
// TEMPLATE PRINCIPAL CONSOLIDÉ
// ═══════════════════════════════════════════════════════════════════════════════

#let consolidated-template(
  title: "L'Entreprise Agentique",
  subtitle: "Monographie Complète",
  author: "André-Guy Bruneau",
  year: "2026",
  body,
) = {
  // ---------------------------------------------------------------------------
  // MÉTADONNÉES DU DOCUMENT
  // ---------------------------------------------------------------------------
  set document(
    title: [#title — #subtitle],
    author: author,
    keywords: (
      "entreprise agentique",
      "agents cognitifs",
      "Apache Kafka",
      "Apache Iceberg",
      "architecture événementielle",
      "transformation numérique",
      "IA agentique",
    ),
  )

  // ---------------------------------------------------------------------------
  // PAGE DE COUVERTURE CONSOLIDÉE
  // ---------------------------------------------------------------------------
  cover-page-consolidated(
    title: title,
    subtitle: subtitle,
    author: author,
    year: year,
    volumes: volumes-config,
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
    // En-tête avec nom de volume
    header: context {
      let page-num = counter(page).get().first()
      if page-num > 4 [
        #set text(size: 9pt, fill: rgb("#666666"))
        #grid(
          columns: (1fr, 1fr),
          align: (left, right),
          [L'Entreprise Agentique],
          [],
        )
        #v(-4pt)
        #line(length: 100%, stroke: 0.5pt + rgb("#CCCCCC"))
      ]
    },
    // Pied de page
    footer: context {
      let page-num = counter(page).get().first()
      if page-num > 4 [
        #align(center)[
          #set text(size: 10pt, fill: rgb("#333333"))
          — #counter(page).display() —
        ]
      ]
    },
    numbering: "1",
  )

  // ---------------------------------------------------------------------------
  // TYPOGRAPHIE
  // ---------------------------------------------------------------------------

  set text(
    font: ("Libertinus Serif", "Linux Libertine", "Times New Roman"),
    size: 11pt,
    lang: "fr",
    region: "CA",
    hyphenate: true,
  )

  set par(
    justify: true,
    leading: 0.65em,
    first-line-indent: 0pt,
  )

  // ---------------------------------------------------------------------------
  // TITRES
  // ---------------------------------------------------------------------------

  show heading.where(level: 1): it => {
    pagebreak(weak: true)
    v(1cm)
    text(
      size: 24pt,
      weight: "bold",
      fill: rgb("#1E3A5F"),
      it.body,
    )
    v(0.5cm)
    line(length: 30%, stroke: 2pt + rgb("#CCCCCC"))
    v(1cm)
  }

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

  show raw.where(block: false): box.with(
    fill: rgb("#F5F5F5"),
    inset: (x: 3pt, y: 0pt),
    outset: (y: 3pt),
    radius: 2pt,
  )

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
  // BLOCKQUOTES
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
  // TABLE DES MATIÈRES GÉNÉRALE
  // ---------------------------------------------------------------------------

  // Page de titre pour la TOC
  pagebreak()

  align(center)[
    #v(2cm)
    #text(
      size: 28pt,
      weight: "bold",
      fill: rgb("#1E3A5F"),
      [Table des Matières Générale],
    )
    #v(1cm)
    #line(length: 50%, stroke: 2pt + rgb("#CCCCCC"))
  ]

  v(1.5cm)

  // Sommaire des volumes
  for v in volumes-config [
    #box(
      width: 100%,
      inset: (y: 10pt),
      [
        #box(
          inset: (x: 14pt, y: 7pt),
          radius: 4pt,
          fill: v.color,
          text(
            size: 12pt,
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

        #v(4pt)
        #h(100pt)
        #text(
          size: 11pt,
          style: "italic",
          fill: rgb("#666666"),
          v.subtitle,
        )
      ],
    )
  ]

  v(1cm)
  line(length: 100%, stroke: 1pt + rgb("#E0E0E0"))
  v(1cm)

  // TOC détaillée
  outline(
    title: none,
    depth: 3,
    indent: auto,
  )

  pagebreak()

  // ---------------------------------------------------------------------------
  // CONTENU
  // ---------------------------------------------------------------------------

  body
}

// ═══════════════════════════════════════════════════════════════════════════════
// FONCTIONS UTILITAIRES
// ═══════════════════════════════════════════════════════════════════════════════

// Insère un séparateur de volume
#let insert-volume-divider(volume-id) = {
  let v = volumes-config.at(int(volume-id) - 1)
  volume-divider(
    volume-number: v.number,
    title: v.title,
    subtitle: v.subtitle,
    accent-color: v.color,
  )
}

// Retourne la couleur d'un volume
#let get-volume-color(volume-id) = {
  let colors = (
    "I": rgb("#1E3A5F"),
    "II": rgb("#2D5016"),
    "III": rgb("#8B4513"),
    "IV": rgb("#4A148C"),
    "V": rgb("#B8860B"),
  )
  colors.at(volume-id, default: rgb("#1E3A5F"))
}
