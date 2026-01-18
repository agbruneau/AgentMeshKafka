// ═══════════════════════════════════════════════════════════════════════════════
// callouts.typ — Définitions des encadrés pour la monographie
// ═══════════════════════════════════════════════════════════════════════════════

#import "@preview/showybox:2.0.4": showybox

// ═══════════════════════════════════════════════════════════════════════════════
// CALLOUTS UNIVERSELS (tous volumes)
// ═══════════════════════════════════════════════════════════════════════════════

// ---------------------------------------------------------------------------
// Définition formelle
// ---------------------------------------------------------------------------
#let callout-definition(body) = showybox(
  frame: (
    border-color: rgb("#1976D2"),
    title-color: rgb("#0D47A1"),
    body-color: rgb("#E3F2FD"),
    thickness: 1.5pt,
    radius: 4pt,
  ),
  title-style: (
    color: white,
    weight: "bold",
    boxed-style: (
      anchor: (x: left, y: horizon),
      radius: (top-left: 4pt, bottom-right: 4pt),
    ),
  ),
  title: [#emoji.book.open Définition formelle],
  body
)

// ---------------------------------------------------------------------------
// Perspective stratégique
// ---------------------------------------------------------------------------
#let callout-strategic(body) = showybox(
  frame: (
    border-color: rgb("#388E3C"),
    title-color: rgb("#1B5E20"),
    body-color: rgb("#E8F5E9"),
    thickness: 1.5pt,
    radius: 4pt,
  ),
  title-style: (
    color: white,
    weight: "bold",
    boxed-style: (
      anchor: (x: left, y: horizon),
      radius: (top-left: 4pt, bottom-right: 4pt),
    ),
  ),
  title: [#emoji.dart Perspective stratégique],
  body
)

// ---------------------------------------------------------------------------
// Exemple concret
// ---------------------------------------------------------------------------
#let callout-example(body) = showybox(
  frame: (
    border-color: rgb("#F57C00"),
    title-color: rgb("#E65100"),
    body-color: rgb("#FFF3E0"),
    thickness: 1.5pt,
    radius: 4pt,
  ),
  title-style: (
    color: white,
    weight: "bold",
    boxed-style: (
      anchor: (x: left, y: horizon),
      radius: (top-left: 4pt, bottom-right: 4pt),
    ),
  ),
  title: [#emoji.bulb Exemple concret],
  body
)

// ═══════════════════════════════════════════════════════════════════════════════
// CALLOUTS VOLUME II (Infrastructure)
// ═══════════════════════════════════════════════════════════════════════════════

// ---------------------------------------------------------------------------
// Note technique
// ---------------------------------------------------------------------------
#let callout-technical(body) = showybox(
  frame: (
    border-color: rgb("#607D8B"),
    title-color: rgb("#37474F"),
    body-color: rgb("#ECEFF1"),
    thickness: 1.5pt,
    radius: 4pt,
  ),
  title-style: (
    color: white,
    weight: "bold",
    boxed-style: (
      anchor: (x: left, y: horizon),
      radius: (top-left: 4pt, bottom-right: 4pt),
    ),
  ),
  title: [#emoji.gear Note technique],
  body
)

// ---------------------------------------------------------------------------
// Bonnes pratiques
// ---------------------------------------------------------------------------
#let callout-best-practices(body) = showybox(
  frame: (
    border-color: rgb("#4CAF50"),
    title-color: rgb("#2E7D32"),
    body-color: rgb("#C8E6C9"),
    thickness: 1.5pt,
    radius: 4pt,
  ),
  title-style: (
    color: white,
    weight: "bold",
    boxed-style: (
      anchor: (x: left, y: horizon),
      radius: (top-left: 4pt, bottom-right: 4pt),
    ),
  ),
  title: [#emoji.checkmark.box Bonnes pratiques],
  body
)

// ---------------------------------------------------------------------------
// Attention
// ---------------------------------------------------------------------------
#let callout-warning(body) = showybox(
  frame: (
    border-color: rgb("#F44336"),
    title-color: rgb("#C62828"),
    body-color: rgb("#FFEBEE"),
    thickness: 1.5pt,
    radius: 4pt,
  ),
  title-style: (
    color: white,
    weight: "bold",
    boxed-style: (
      anchor: (x: left, y: horizon),
      radius: (top-left: 4pt, bottom-right: 4pt),
    ),
  ),
  title: [#emoji.warning Attention],
  body
)

// ═══════════════════════════════════════════════════════════════════════════════
// CALLOUTS VOLUME III (Kafka)
// ═══════════════════════════════════════════════════════════════════════════════

// ---------------------------------------------------------------------------
// Note de terrain (structuré)
// ---------------------------------------------------------------------------
#let callout-field-note(
  contexte: none,
  defi: none,
  solution: none,
  lecon: none,
  body: none,
) = showybox(
  frame: (
    border-color: rgb("#FFA000"),
    title-color: rgb("#FF6F00"),
    body-color: rgb("#FFF8E1"),
    thickness: 1.5pt,
    radius: 4pt,
  ),
  title-style: (
    color: white,
    weight: "bold",
    boxed-style: (
      anchor: (x: left, y: horizon),
      radius: (top-left: 4pt, bottom-right: 4pt),
    ),
  ),
  title: [#emoji.construction Note de terrain],
  [
    #if contexte != none [
      *Contexte* : #contexte
      #v(4pt)
    ]
    #if defi != none [
      *Défi* : #defi
      #v(4pt)
    ]
    #if solution != none [
      *Solution* : #solution
      #v(4pt)
    ]
    #if lecon != none [
      *Leçon* : #lecon
    ]
    #if body != none [
      #v(4pt)
      #body
    ]
  ]
)

// ---------------------------------------------------------------------------
// Décision architecturale (structuré)
// ---------------------------------------------------------------------------
#let callout-decision(
  contexte: none,
  analyse: none,
  decision: none,
  justification: none,
  body: none,
) = showybox(
  frame: (
    border-color: rgb("#3F51B5"),
    title-color: rgb("#1A237E"),
    body-color: rgb("#E8EAF6"),
    thickness: 1.5pt,
    radius: 4pt,
  ),
  title-style: (
    color: white,
    weight: "bold",
    boxed-style: (
      anchor: (x: left, y: horizon),
      radius: (top-left: 4pt, bottom-right: 4pt),
    ),
  ),
  title: [#emoji.building.classical Décision architecturale],
  [
    #if contexte != none [
      *Contexte* : #contexte
      #v(4pt)
    ]
    #if analyse != none [
      *Analyse* : #analyse
      #v(4pt)
    ]
    #if decision != none [
      *Décision* : #decision
      #v(4pt)
    ]
    #if justification != none [
      *Justification* : #justification
    ]
    #if body != none [
      #v(4pt)
      #body
    ]
  ]
)

// ---------------------------------------------------------------------------
// Anti-patron
// ---------------------------------------------------------------------------
#let callout-antipattern(body) = showybox(
  frame: (
    border-color: rgb("#E91E63"),
    title-color: rgb("#880E4F"),
    body-color: rgb("#FCE4EC"),
    thickness: 1.5pt,
    radius: 4pt,
  ),
  title-style: (
    color: white,
    weight: "bold",
    boxed-style: (
      anchor: (x: left, y: horizon),
      radius: (top-left: 4pt, bottom-right: 4pt),
    ),
  ),
  title: [#emoji.no.entry Anti-patron],
  body
)

// ═══════════════════════════════════════════════════════════════════════════════
// CALLOUTS VOLUME IV (Iceberg)
// ═══════════════════════════════════════════════════════════════════════════════

// ---------------------------------------------------------------------------
// Étude de cas (structuré, titre dynamique)
// ---------------------------------------------------------------------------
#let callout-case-study(
  name: "",
  secteur: none,
  defi: none,
  solution: none,
  resultats: none,
  body: none,
) = showybox(
  frame: (
    border-color: rgb("#03A9F4"),
    title-color: rgb("#01579B"),
    body-color: rgb("#E1F5FE"),
    thickness: 1.5pt,
    radius: 4pt,
  ),
  title-style: (
    color: white,
    weight: "bold",
    boxed-style: (
      anchor: (x: left, y: horizon),
      radius: (top-left: 4pt, bottom-right: 4pt),
    ),
  ),
  title: [#emoji.chart.bar Étude de cas : #name],
  [
    #if secteur != none [
      *Secteur* : #secteur
      #v(4pt)
    ]
    #if defi != none [
      *Défi* : #defi
      #v(4pt)
    ]
    #if solution != none [
      *Solution* : #solution
      #v(4pt)
    ]
    #if resultats != none [
      *Résultats* : #resultats
    ]
    #if body != none [
      #v(4pt)
      #body
    ]
  ]
)

// ---------------------------------------------------------------------------
// Migration (structuré, titre dynamique)
// ---------------------------------------------------------------------------
#let callout-migration(
  name: "",
  de: none,
  vers: none,
  strategie: none,
  resultats: none,
  body: none,
) = showybox(
  frame: (
    border-color: rgb("#9C27B0"),
    title-color: rgb("#4A148C"),
    body-color: rgb("#F3E5F5"),
    thickness: 1.5pt,
    radius: 4pt,
  ),
  title-style: (
    color: white,
    weight: "bold",
    boxed-style: (
      anchor: (x: left, y: horizon),
      radius: (top-left: 4pt, bottom-right: 4pt),
    ),
  ),
  title: [#emoji.arrows.cycle Migration : #name],
  [
    #if de != none [
      *De* : #de
      #v(4pt)
    ]
    #if vers != none [
      *Vers* : #vers
      #v(4pt)
    ]
    #if strategie != none [
      *Stratégie* : #strategie
      #v(4pt)
    ]
    #if resultats != none [
      *Résultats* : #resultats
    ]
    #if body != none [
      #v(4pt)
      #body
    ]
  ]
)

// ---------------------------------------------------------------------------
// Performance (titre dynamique)
// ---------------------------------------------------------------------------
#let callout-performance(name: "", body) = showybox(
  frame: (
    border-color: rgb("#00BCD4"),
    title-color: rgb("#006064"),
    body-color: rgb("#E0F7FA"),
    thickness: 1.5pt,
    radius: 4pt,
  ),
  title-style: (
    color: white,
    weight: "bold",
    boxed-style: (
      anchor: (x: left, y: horizon),
      radius: (top-left: 4pt, bottom-right: 4pt),
    ),
  ),
  title: [#emoji.chart.increasing Performance : #name],
  body
)

// ═══════════════════════════════════════════════════════════════════════════════
// CALLOUTS VOLUME V (Renaissance)
// ═══════════════════════════════════════════════════════════════════════════════

// ---------------------------------------------------------------------------
// Figure historique (structuré, titre dynamique)
// ---------------------------------------------------------------------------
#let callout-historical(
  name: "",
  epoque: none,
  domaines: none,
  contribution: none,
  lecon: none,
  body: none,
) = showybox(
  frame: (
    border-color: rgb("#FBC02D"),
    title-color: rgb("#F57F17"),
    body-color: rgb("#FFF9C4"),
    thickness: 1.5pt,
    radius: 4pt,
  ),
  title-style: (
    color: white,
    weight: "bold",
    boxed-style: (
      anchor: (x: left, y: horizon),
      radius: (top-left: 4pt, bottom-right: 4pt),
    ),
  ),
  title: [#emoji.art Figure historique : #name],
  [
    #if epoque != none [
      *Époque* : #epoque
      #v(4pt)
    ]
    #if domaines != none [
      *Domaines* : #domaines
      #v(4pt)
    ]
    #if contribution != none [
      *Contribution* : #contribution
      #v(4pt)
    ]
    #if lecon != none [
      *Leçon pour aujourd'hui* : #lecon
    ]
    #if body != none [
      #v(4pt)
      #body
    ]
  ]
)

// ---------------------------------------------------------------------------
// Réflexion
// ---------------------------------------------------------------------------
#let callout-reflection(body) = showybox(
  frame: (
    border-color: rgb("#9E9E9E"),
    title-color: rgb("#424242"),
    body-color: rgb("#F5F5F5"),
    thickness: 1.5pt,
    radius: 4pt,
  ),
  title-style: (
    color: white,
    weight: "bold",
    boxed-style: (
      anchor: (x: left, y: horizon),
      radius: (top-left: 4pt, bottom-right: 4pt),
    ),
  ),
  title: [#emoji.thought.bubble Réflexion],
  body
)

// ---------------------------------------------------------------------------
// Manifeste
// ---------------------------------------------------------------------------
#let callout-manifesto(body) = showybox(
  frame: (
    border-color: rgb("#795548"),
    title-color: rgb("#3E2723"),
    body-color: rgb("#EFEBE9"),
    thickness: 1.5pt,
    radius: 4pt,
  ),
  title-style: (
    color: white,
    weight: "bold",
    boxed-style: (
      anchor: (x: left, y: horizon),
      radius: (top-left: 4pt, bottom-right: 4pt),
    ),
  ),
  title: [#emoji.scroll Manifeste],
  body
)

// ═══════════════════════════════════════════════════════════════════════════════
// CALLOUT GÉNÉRIQUE (fallback)
// ═══════════════════════════════════════════════════════════════════════════════

#let callout-generic(title: "Note", color: rgb("#607D8B"), body) = showybox(
  frame: (
    border-color: color,
    title-color: color.darken(20%),
    body-color: color.lighten(90%),
    thickness: 1.5pt,
    radius: 4pt,
  ),
  title-style: (
    color: white,
    weight: "bold",
    boxed-style: (
      anchor: (x: left, y: horizon),
      radius: (top-left: 4pt, bottom-right: 4pt),
    ),
  ),
  title: title,
  body
)
