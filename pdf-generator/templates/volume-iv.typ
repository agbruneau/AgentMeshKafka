// Template Typst pour Volume IV - Apache Iceberg : Le Lakehouse Moderne
// Style inspiré de modern-technique-report

#let volume-config(
  title: "Apache Iceberg",
  subtitle: "Le Lakehouse Moderne",
  volume-id: "IV",
  author: "André-Guy Bruneau",
  year: "2026",
  theme-color: rgb("#4A0080"),
  body
) = {
  // Configuration du document
  set document(
    title: "Volume " + volume-id + " — " + title,
    author: author,
  )

  // Configuration de la page
  set page(
    paper: "a4",
    margin: (
      top: 2.5cm,
      bottom: 2.5cm,
      left: 2.5cm,
      right: 2cm,
    ),
    header: context {
      let page-num = counter(page).get().first()
      if page-num > 2 {
        set text(size: 9pt, fill: luma(100))
        grid(
          columns: (1fr, 1fr),
          align: (left, right),
          [Volume #volume-id — #title],
          [L'Entreprise Agentique]
        )
        line(length: 100%, stroke: 0.5pt + luma(200))
      }
    },
    footer: context {
      let page-num = counter(page).get().first()
      if page-num > 1 {
        set text(size: 9pt)
        align(center)[#page-num]
      }
    },
  )

  // Configuration des polices
  set text(
    font: "Libertinus Serif",
    size: 11pt,
    lang: "fr",
    region: "CA",
  )

  // Paragraphes justifiés
  set par(justify: true, leading: 0.65em)

  // Configuration des titres
  show heading.where(level: 1): it => {
    pagebreak(weak: true)
    v(1cm)
    block(
      fill: theme-color.lighten(90%),
      inset: (x: 1em, y: 0.8em),
      radius: 4pt,
      width: 100%,
      [
        #set text(size: 22pt, weight: "bold", fill: theme-color)
        #it.body
      ]
    )
    v(0.8cm)
  }

  show heading.where(level: 2): it => {
    v(1.2em)
    block[
      #set text(size: 14pt, weight: "bold", fill: theme-color.darken(20%))
      #it.body
    ]
    v(0.6em)
  }

  show heading.where(level: 3): it => {
    v(1em)
    block[
      #set text(size: 12pt, weight: "bold")
      #it.body
    ]
    v(0.4em)
  }

  show heading.where(level: 4): it => {
    v(0.8em)
    block[
      #set text(size: 11pt, weight: "bold", style: "italic")
      #it.body
    ]
    v(0.3em)
  }

  // Configuration des tableaux
  set table(
    stroke: (x, y) => if y == 0 { (bottom: 1.5pt + theme-color) } else { (bottom: 0.5pt + luma(200)) },
    inset: 8pt,
    fill: (x, y) => if y == 0 { theme-color.lighten(90%) } else if calc.odd(y) { luma(248) } else { white },
  )
  show table: set text(size: 9.5pt)

  // Configuration des blocs de code
  show raw.where(block: true): it => {
    set text(font: "Consolas", size: 9pt)
    block(
      fill: luma(245),
      inset: 10pt,
      radius: 4pt,
      width: 100%,
      it
    )
  }

  show raw.where(block: false): it => {
    set text(font: "Consolas", size: 10pt)
    box(fill: luma(240), inset: (x: 3pt, y: 0pt), radius: 2pt, it)
  }

  // Style des blockquotes (callouts)
  show quote: it => {
    block(
      fill: luma(248),
      inset: (left: 1em, right: 0.8em, top: 0.6em, bottom: 0.6em),
      radius: 4pt,
      stroke: (left: 3pt + theme-color),
      width: 100%,
      [
        #set text(size: 10.5pt)
        #it.body
      ]
    )
  }

  // Style des liens
  show link: it => {
    set text(fill: theme-color)
    underline(it)
  }

  // ========================================
  // PAGE DE COUVERTURE
  // ========================================

  set page(header: none, footer: none, margin: 0pt)

  // Fond coloré
  place(
    rect(
      width: 100%,
      height: 100%,
      fill: gradient.linear(theme-color, theme-color.darken(30%), angle: 135deg)
    )
  )

  // Contenu de la couverture
  place(
    center + horizon,
    block(width: 80%)[
      #set text(fill: white)
      #set align(center)

      // Collection
      #text(size: 12pt, tracking: 0.3em, weight: "regular")[L'ENTREPRISE AGENTIQUE]

      #v(2.5cm)

      // Volume
      #text(size: 16pt, weight: "bold")[VOLUME #volume-id]

      #v(0.8cm)

      // Titre principal
      #text(size: 36pt, weight: "bold")[#title]

      #v(0.6cm)

      // Sous-titre
      #text(size: 16pt, style: "italic")[#subtitle]

      #v(4cm)

      // Ligne décorative
      #line(length: 40%, stroke: 1pt + white.transparentize(50%))

      #v(1cm)

      // Auteur
      #text(size: 14pt)[#author]

      #v(0.4cm)

      // Année
      #text(size: 12pt)[#year]
    ]
  )

  // Décoration géométrique
  place(
    bottom + right,
    dx: -2cm,
    dy: -2cm,
    circle(radius: 4cm, fill: white.transparentize(95%))
  )
  place(
    bottom + right,
    dx: -1cm,
    dy: -1cm,
    circle(radius: 2cm, fill: white.transparentize(90%))
  )

  pagebreak()

  // ========================================
  // PAGE DE TITRE INTÉRIEURE
  // ========================================

  set page(margin: (x: 3cm, y: 4cm))

  align(center)[
    #v(2cm)

    #text(size: 12pt, tracking: 0.2em)[L'ENTREPRISE AGENTIQUE]

    #v(1cm)

    #text(size: 14pt, weight: "bold", fill: theme-color)[VOLUME #volume-id]

    #v(0.5cm)

    #text(size: 28pt, weight: "bold")[#title]

    #v(0.3cm)

    #text(size: 14pt, style: "italic")[#subtitle]

    #v(3cm)

    #line(length: 30%, stroke: 0.5pt + luma(180))

    #v(1cm)

    #text(size: 12pt)[#author]

    #v(0.3cm)

    #text(size: 11pt, fill: luma(100))[#year]

    #v(2cm)

    #text(size: 10pt, fill: luma(120))[
      Architecture, Conception et Opérations du Data Lakehouse
    ]
  ]

  pagebreak()

  // ========================================
  // TABLE DES MATIÈRES
  // ========================================

  set page(
    margin: (top: 2.5cm, bottom: 2.5cm, left: 2.5cm, right: 2cm),
    header: context {
      let page-num = counter(page).get().first()
      if page-num > 2 {
        set text(size: 9pt, fill: luma(100))
        grid(
          columns: (1fr, 1fr),
          align: (left, right),
          [Volume #volume-id — #title],
          [L'Entreprise Agentique]
        )
        line(length: 100%, stroke: 0.5pt + luma(200))
      }
    },
    footer: context {
      let page-num = counter(page).get().first()
      if page-num > 1 {
        set text(size: 9pt)
        align(center)[#page-num]
      }
    },
  )

  text(size: 20pt, weight: "bold", fill: theme-color)[Table des Matières]
  v(1cm)

  outline(
    title: none,
    indent: 1.5em,
    depth: 3,
  )

  pagebreak()

  // ========================================
  // CONTENU PRINCIPAL
  // ========================================

  body

  // ========================================
  // COLOPHON
  // ========================================

  pagebreak()

  v(1fr)

  align(center)[
    #set text(size: 9pt, fill: luma(120))

    #line(length: 20%, stroke: 0.5pt + luma(200))

    #v(0.5cm)

    *Volume #volume-id — #title*

    Collection « L'Entreprise Agentique »

    #v(0.3cm)

    #author · #year

    #v(0.3cm)

    _Document généré avec Typst_
  ]
}

// Appliquer le template
#show: volume-config.with(
  title: "Apache Iceberg",
  subtitle: "Le Lakehouse Moderne",
  volume-id: "IV",
  author: "André-Guy Bruneau",
  year: "2026",
  theme-color: rgb("#4A0080"),
)
