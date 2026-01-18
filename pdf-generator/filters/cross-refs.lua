-- ═══════════════════════════════════════════════════════════════════════════════
-- cross-refs.lua — Filtre Pandoc pour les références inter-volumes et chapitres
-- ═══════════════════════════════════════════════════════════════════════════════

-- Configuration des volumes
local volumes = {
  ["I"] = {
    title = "Fondations de l'Entreprise Agentique",
    label = "volume-i"
  },
  ["II"] = {
    title = "Infrastructure Agentique",
    label = "volume-ii"
  },
  ["III"] = {
    title = "Apache Kafka — Guide de l'Architecte",
    label = "volume-iii"
  },
  ["IV"] = {
    title = "Apache Iceberg — Le Lakehouse Moderne",
    label = "volume-iv"
  },
  ["V"] = {
    title = "Le Développeur Renaissance",
    label = "volume-v"
  }
}

-- Registre des références (pour la validation)
local references = {}

-- Patterns de détection des références
local patterns = {
  -- Volume I, Volume II, etc.
  volume = "Volume%s+([IVX]+)",
  -- Chapitre I.5, Chapitre III.12, etc.
  chapter = "Chapitre%s+([IVX]+%.%d+)",
  -- Section I.5.2, etc.
  section = "Section%s+([IVX]+%.%d+%.%d+)",
  -- comme défini au Volume I
  volume_ref = "comme%s+défini%s+au%s+Volume%s+([IVX]+)",
  -- voir Volume II
  voir_volume = "voir%s+Volume%s+([IVX]+)",
  -- voir Chapitre III.5
  voir_chapter = "voir%s+Chapitre%s+([IVX]+%.%d+)",
  -- le Volume IV détaille
  volume_detaille = "le%s+Volume%s+([IVX]+)%s+détaille",
  -- le Chapitre I.12 explore
  chapter_explore = "le%s+Chapitre%s+([IVX]+%.%d+)%s+explore"
}

-- Convertit un numéro de volume romain en label
local function volume_to_label(roman)
  return "volume-" .. roman:lower()
end

-- Convertit un numéro de chapitre en label
local function chapter_to_label(chapter_num)
  -- I.5 -> chapter-i-5
  local volume, num = chapter_num:match("([IVX]+)%.(%d+)")
  if volume and num then
    return "chapter-" .. volume:lower() .. "-" .. num
  end
  return nil
end

-- Génère un lien Typst vers un volume
local function generate_volume_link(roman, display_text)
  local vol = volumes[roman]
  if vol then
    -- Créer un lien interne
    return string.format("#link(<%s>)[%s]", vol.label, display_text)
  end
  return display_text
end

-- Génère un lien Typst vers un chapitre
local function generate_chapter_link(chapter_num, display_text)
  local label = chapter_to_label(chapter_num)
  if label then
    return string.format("#link(<%s>)[%s]", label, display_text)
  end
  return display_text
end

-- Traitement des chaînes de texte (Str elements)
function Str(el)
  local text = el.text

  -- Détecter les références simples ne nécessitant pas de transformation
  -- Ces patterns sont trop courts pour être des références complètes

  return el
end

-- Traitement des paragraphes pour détecter les références complètes
function Para(el)
  local text = pandoc.utils.stringify(el)
  local modified = false
  local new_inlines = {}

  -- Parcourir les inlines du paragraphe
  for _, inline in ipairs(el.content) do
    if inline.t == "Str" then
      table.insert(new_inlines, inline)
    elseif inline.t == "Space" then
      table.insert(new_inlines, inline)
    else
      table.insert(new_inlines, inline)
    end
  end

  -- Pour l'instant, retourner le paragraphe tel quel
  -- Les liens seront gérés au niveau de la compilation Typst
  return el
end

-- Traitement des en-têtes pour ajouter des labels
function Header(el)
  local text = pandoc.utils.stringify(el)

  -- Détecter si c'est un titre de chapitre (niveau 1)
  if el.level == 1 then
    -- Extraire le numéro de chapitre
    local chapter_num = text:match("^Chapitre%s+([IVX]+%.%d+)")
    if not chapter_num then
      chapter_num = text:match("^([IVX]+%.%d+)")
    end

    if chapter_num then
      local label = chapter_to_label(chapter_num)
      if label then
        -- Ajouter un identifiant au header pour les références
        el.identifier = label
        -- Enregistrer la référence
        references[label] = {
          type = "chapter",
          number = chapter_num,
          title = text
        }
      end
    end
  end

  -- Détecter si c'est un titre de section (niveau 2)
  if el.level == 2 then
    local section_num = text:match("^([IVX]+%.%d+%.%d+)")
    if section_num then
      local label = "section-" .. section_num:gsub("%.", "-"):lower()
      el.identifier = label
      references[label] = {
        type = "section",
        number = section_num,
        title = text
      }
    end
  end

  return el
end

-- Traitement des liens existants
function Link(el)
  local target = el.target

  -- Vérifier si c'est une référence interne
  if target:match("^#") then
    -- Lien interne, conserver tel quel
    return el
  end

  return el
end

-- Ajouter des métadonnées sur les références trouvées (optionnel)
function Pandoc(doc)
  -- Ajouter les références au document pour utilisation ultérieure
  if next(references) then
    -- On pourrait ajouter les références aux métadonnées
    -- Pour l'instant, on les ignore
  end

  return doc
end

-- Exporter les fonctions
return {
  { Header = Header },
  { Link = Link },
  { Para = Para },
  { Pandoc = Pandoc }
}
