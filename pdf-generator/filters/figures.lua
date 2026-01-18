-- ═══════════════════════════════════════════════════════════════════════════════
-- figures.lua — Filtre Pandoc pour la gestion des tableaux et figures
-- ═══════════════════════════════════════════════════════════════════════════════

-- Compteurs pour la numérotation
local table_counter = 0
local figure_counter = 0
local current_chapter = ""

-- Réinitialise les compteurs pour un nouveau chapitre
local function reset_counters_for_chapter(chapter_id)
  if chapter_id ~= current_chapter then
    current_chapter = chapter_id
    table_counter = 0
    figure_counter = 0
  end
end

-- Extrait l'identifiant du chapitre d'un heading
local function extract_chapter_id(el)
  local text = pandoc.utils.stringify(el)
  -- Chercher un pattern comme "I.1", "II.5", "III.12", etc.
  local chapter_id = text:match("^[IVX]+%.%d+")
  if chapter_id then
    return chapter_id
  end
  -- Chercher aussi "Chapitre I.1" ou similaire
  chapter_id = text:match("Chapitre%s+([IVX]+%.%d+)")
  return chapter_id or ""
end

-- Traitement des en-têtes (pour tracker le chapitre courant)
function Header(el)
  if el.level == 1 then
    local chapter_id = extract_chapter_id(el)
    reset_counters_for_chapter(chapter_id)
  end
  return el
end

-- Traitement des tableaux
function Table(el)
  table_counter = table_counter + 1

  -- Générer le numéro de tableau
  local table_num
  if current_chapter ~= "" then
    table_num = string.format("Tableau %s.%d", current_chapter, table_counter)
  else
    table_num = string.format("Tableau %d", table_counter)
  end

  -- Vérifier si le tableau a une légende
  local caption = el.caption
  if caption and caption.long and #caption.long > 0 then
    -- Le tableau a déjà une légende, ajouter le numéro
    local caption_text = pandoc.utils.stringify(caption.long[1])
    local new_caption = pandoc.Inlines({
      pandoc.Strong(pandoc.Str(table_num .. " — ")),
      pandoc.Str(caption_text)
    })
    el.caption.long = {pandoc.Plain(new_caption)}
  end

  return el
end

-- Traitement des images (figures)
function Image(el)
  figure_counter = figure_counter + 1

  -- Générer le numéro de figure
  local figure_num
  if current_chapter ~= "" then
    figure_num = string.format("Figure %s.%d", current_chapter, figure_counter)
  else
    figure_num = string.format("Figure %d", figure_counter)
  end

  -- Vérifier si l'image a une légende (alt text ou title)
  local caption = el.title or pandoc.utils.stringify(el.caption)
  if caption and caption ~= "" then
    -- Ajouter le numéro à la légende
    el.title = figure_num .. " — " .. caption
  else
    el.title = figure_num
  end

  return el
end

-- Traitement des blocs de code avec légende
function CodeBlock(el)
  -- Vérifier si le bloc a une classe "caption" ou un attribut caption
  local caption = el.attributes["caption"]
  if caption then
    -- Générer un listing numéroté
    figure_counter = figure_counter + 1
    local listing_num
    if current_chapter ~= "" then
      listing_num = string.format("Listing %s.%d", current_chapter, figure_counter)
    else
      listing_num = string.format("Listing %d", figure_counter)
    end

    -- Créer un bloc Typst avec figure
    local typst_code = string.format([[
#figure(
  caption: [%s — %s],
  ```%s
%s
```
)]], listing_num, caption, el.classes[1] or "", el.text)

    return pandoc.RawBlock('typst', typst_code)
  end

  return el
end

-- Fonction pour créer une référence croisée à un tableau ou figure
function Cite(el)
  -- Vérifier si c'est une référence à un tableau ou figure
  for _, citation in ipairs(el.citations) do
    local id = citation.id
    if id:match("^tbl:") then
      -- Référence à un tableau
      local ref_num = id:gsub("^tbl:", "")
      return pandoc.Str("Tableau " .. ref_num)
    elseif id:match("^fig:") then
      -- Référence à une figure
      local ref_num = id:gsub("^fig:", "")
      return pandoc.Str("Figure " .. ref_num)
    end
  end
  return el
end

-- Exporter les fonctions
return {
  { Header = Header },
  { Table = Table },
  { Image = Image },
  { CodeBlock = CodeBlock },
  { Cite = Cite }
}
