// ═══════════════════════════════════════════════════════════════════════════════
// cover.typ — Template de page de couverture
// ═══════════════════════════════════════════════════════════════════════════════

// ---------------------------------------------------------------------------
// Page de couverture pour un volume individuel
// ---------------------------------------------------------------------------
#let cover-page(
  volume-number: "I",
  title: "Titre du Volume",
  subtitle: "Sous-titre",
  author: "André-Guy Bruneau",
  year: "2026",
  accent-color: rgb("#1E3A5F"),
) = {
  set page(
    margin: (top: 0cm, bottom: 0cm, left: 0cm, right: 0cm),
    header: none,
    footer: none,
  )

  // Fond de page
  place(
    top + left,
    rect(
      width: 100%,
      height: 100%,
      fill: white,
    ),
  )

  // Numéro de volume en arrière-plan
  place(
    center + horizon,
    dy: -2cm,
    text(
      size: 300pt,
      weight: "bold",
      fill: accent-color.lighten(85%),
      volume-number,
    ),
  )

  // Ligne décorative supérieure
  place(
    top + left,
    dy: 3cm,
    rect(
      width: 100%,
      height: 4pt,
      fill: accent-color,
    ),
  )

  // Contenu principal
  v(8cm)

  align(center)[
    // Badge "Volume"
    #box(
      inset: (x: 16pt, y: 8pt),
      radius: 4pt,
      fill: accent-color,
      text(
        size: 12pt,
        weight: "bold",
        fill: white,
        tracking: 2pt,
        [VOLUME #volume-number],
      ),
    )

    #v(2cm)

    // Titre principal
    #text(
      size: 36pt,
      weight: "bold",
      fill: accent-color,
      title,
    )

    #v(1cm)

    // Sous-titre
    #text(
      size: 18pt,
      style: "italic",
      fill: rgb("#666666"),
      subtitle,
    )

    #v(3cm)

    // Ligne décorative
    #line(
      length: 40%,
      stroke: 2pt + accent-color.lighten(50%),
    )

    #v(3cm)

    // Auteur
    #text(
      size: 14pt,
      fill: rgb("#333333"),
      author,
    )

    #v(0.5cm)

    // Année
    #text(
      size: 12pt,
      fill: rgb("#666666"),
      year,
    )
  ]

  // Ligne décorative inférieure
  place(
    bottom + left,
    dy: -3cm,
    rect(
      width: 100%,
      height: 4pt,
      fill: accent-color,
    ),
  )

  pagebreak()
}

// ---------------------------------------------------------------------------
// Page de couverture pour la monographie consolidée
// ---------------------------------------------------------------------------
#let cover-page-consolidated(
  title: "L'Entreprise Agentique",
  subtitle: "Monographie Complète",
  author: "André-Guy Bruneau",
  year: "2026",
  volumes: (
    (number: "I", title: "Fondations de l'Entreprise Agentique", color: rgb("#1E3A5F")),
    (number: "II", title: "Infrastructure Agentique", color: rgb("#2D5016")),
    (number: "III", title: "Apache Kafka — Guide de l'Architecte", color: rgb("#8B4513")),
    (number: "IV", title: "Apache Iceberg — Le Lakehouse Moderne", color: rgb("#4A148C")),
    (number: "V", title: "Le Développeur Renaissance", color: rgb("#B8860B")),
  ),
) = {
  set page(
    margin: (top: 0cm, bottom: 0cm, left: 0cm, right: 0cm),
    header: none,
    footer: none,
  )

  // Fond blanc
  place(
    top + left,
    rect(
      width: 100%,
      height: 100%,
      fill: white,
    ),
  )

  // Bande colorée en haut (dégradé des 5 volumes)
  place(
    top + left,
    stack(
      dir: ltr,
      ..volumes.map(v => rect(
        width: 20%,
        height: 1cm,
        fill: v.color,
      )),
    ),
  )

  // Contenu principal
  v(5cm)

  align(center)[
    // Titre principal
    #text(
      size: 42pt,
      weight: "bold",
      fill: rgb("#1E3A5F"),
      title,
    )

    #v(1cm)

    // Sous-titre
    #text(
      size: 20pt,
      style: "italic",
      fill: rgb("#666666"),
      subtitle,
    )

    #v(2cm)

    // Ligne décorative
    #line(
      length: 60%,
      stroke: 2pt + rgb("#CCCCCC"),
    )

    #v(1.5cm)

    // Liste des volumes
    #box(
      width: 80%,
      inset: 20pt,
      [
        #set text(size: 11pt)
        #for (i, v) in volumes.enumerate() [
          #box(
            inset: (x: 8pt, y: 4pt),
            radius: 3pt,
            fill: v.color,
            text(fill: white, weight: "bold", [Vol. #v.number]),
          )
          #h(8pt)
          #text(fill: rgb("#333333"), v.title)
          #if i < volumes.len() - 1 [
            #v(8pt)
          ]
        ]
      ],
    )

    #v(2cm)

    // Auteur
    #text(
      size: 16pt,
      fill: rgb("#333333"),
      author,
    )

    #v(0.5cm)

    // Année
    #text(
      size: 14pt,
      fill: rgb("#666666"),
      year,
    )
  ]

  // Bande colorée en bas
  place(
    bottom + left,
    stack(
      dir: ltr,
      ..volumes.map(v => rect(
        width: 20%,
        height: 1cm,
        fill: v.color,
      )),
    ),
  )

  pagebreak()
}

// ---------------------------------------------------------------------------
// Page de transition entre volumes (pour la version consolidée)
// ---------------------------------------------------------------------------
#let volume-divider(
  volume-number: "I",
  title: "Titre du Volume",
  subtitle: "Sous-titre",
  accent-color: rgb("#1E3A5F"),
) = {
  set page(
    margin: (top: 0cm, bottom: 0cm, left: 0cm, right: 0cm),
    header: none,
    footer: none,
  )

  // Fond avec couleur du volume
  place(
    top + left,
    rect(
      width: 100%,
      height: 100%,
      fill: accent-color.lighten(95%),
    ),
  )

  // Bande de couleur à gauche
  place(
    left + top,
    rect(
      width: 2cm,
      height: 100%,
      fill: accent-color,
    ),
  )

  // Numéro de volume
  place(
    left + horizon,
    dx: 3cm,
    text(
      size: 200pt,
      weight: "bold",
      fill: accent-color.lighten(70%),
      volume-number,
    ),
  )

  // Contenu
  place(
    center + horizon,
    [
      #align(center)[
        #v(2cm)

        #box(
          inset: (x: 24pt, y: 12pt),
          radius: 8pt,
          fill: accent-color,
          text(
            size: 18pt,
            weight: "bold",
            fill: white,
            tracking: 3pt,
            [VOLUME #volume-number],
          ),
        )

        #v(2cm)

        #text(
          size: 32pt,
          weight: "bold",
          fill: accent-color,
          title,
        )

        #v(1cm)

        #text(
          size: 16pt,
          style: "italic",
          fill: rgb("#666666"),
          subtitle,
        )
      ]
    ],
  )

  pagebreak()
}
