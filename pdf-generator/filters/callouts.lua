-- ═══════════════════════════════════════════════════════════════════════════════
-- callouts.lua — Filtre Pandoc pour transformer les blockquotes en callouts Typst
-- ═══════════════════════════════════════════════════════════════════════════════

-- Configuration des callouts
-- Ordre de détection : du plus spécifique au plus général
local callouts = {
  -- Callouts avec titres dynamiques (patterns avec capture)
  {
    pattern = "^%*%*Étude de cas%s*:%s*(.+)%*%*",
    func = "callout-case-study",
    has_dynamic_title = true,
    structured = true,
    fields = {"secteur", "defi", "solution", "resultats"}
  },
  {
    pattern = "^%*%*Migration%s*:%s*(.+)%*%*",
    func = "callout-migration",
    has_dynamic_title = true,
    structured = true,
    fields = {"de", "vers", "strategie", "resultats"}
  },
  {
    pattern = "^%*%*Performance%s*:%s*(.+)%*%*",
    func = "callout-performance",
    has_dynamic_title = true,
    structured = false
  },
  {
    pattern = "^%*%*Figure historique%s*:%s*(.+)%*%*",
    func = "callout-historical",
    has_dynamic_title = true,
    structured = true,
    fields = {"epoque", "domaines", "contribution", "lecon"}
  },

  -- Callouts structurés
  {
    pattern = "^%*%*Note de terrain%*%*",
    func = "callout-field-note",
    has_dynamic_title = false,
    structured = true,
    fields = {"contexte", "defi", "solution", "lecon"}
  },
  {
    pattern = "^%*%*Décision architecturale%*%*",
    func = "callout-decision",
    has_dynamic_title = false,
    structured = true,
    fields = {"contexte", "analyse", "decision", "justification"}
  },

  -- Callouts simples spécifiques
  {
    pattern = "^%*%*Anti%-patron%*%*",
    func = "callout-antipattern",
    has_dynamic_title = false,
    structured = false
  },
  {
    pattern = "^%*%*Note technique%*%*",
    func = "callout-technical",
    has_dynamic_title = false,
    structured = false
  },
  {
    pattern = "^%*%*Bonnes pratiques%*%*",
    func = "callout-best-practices",
    has_dynamic_title = false,
    structured = false
  },
  {
    pattern = "^%*%*Attention%*%*",
    func = "callout-warning",
    has_dynamic_title = false,
    structured = false
  },
  {
    pattern = "^%*%*Réflexion%*%*",
    func = "callout-reflection",
    has_dynamic_title = false,
    structured = false
  },
  {
    pattern = "^%*%*Manifeste%*%*",
    func = "callout-manifesto",
    has_dynamic_title = false,
    structured = false
  },

  -- Callouts universels
  {
    pattern = "^%*%*Définition formelle%*%*",
    func = "callout-definition",
    has_dynamic_title = false,
    structured = false
  },
  {
    pattern = "^%*%*Perspective stratégique%*%*",
    func = "callout-strategic",
    has_dynamic_title = false,
    structured = false
  },
  {
    pattern = "^%*%*Exemple concret%*%*",
    func = "callout-example",
    has_dynamic_title = false,
    structured = false
  },
}

-- Mapping des labels de champs structurés (français -> clé Typst)
local field_mappings = {
  ["Contexte"] = "contexte",
  ["Défi"] = "defi",
  ["Solution"] = "solution",
  ["Leçon"] = "lecon",
  ["Analyse"] = "analyse",
  ["Décision"] = "decision",
  ["Justification"] = "justification",
  ["Secteur"] = "secteur",
  ["Résultats"] = "resultats",
  ["De"] = "de",
  ["Vers"] = "vers",
  ["Stratégie"] = "strategie",
  ["Époque"] = "epoque",
  ["Domaines"] = "domaines",
  ["Contribution"] = "contribution",
  ["Leçon pour aujourd'hui"] = "lecon",
  ["Organisation"] = "contexte",
  ["Observation"] = "contexte",
  ["Recommandation"] = "lecon",
  ["Options"] = "analyse",
}

-- Convertit un texte Pandoc en string
local function stringify(el)
  if el == nil then return "" end
  return pandoc.utils.stringify(el)
end

-- Extrait le premier paragraphe d'un BlockQuote
local function get_first_line(blocks)
  if #blocks == 0 then return "" end
  local first = blocks[1]
  if first.t == "Para" or first.t == "Plain" then
    return stringify(first)
  end
  return ""
end

-- Détecte le type de callout à partir de la première ligne
local function detect_callout(first_line)
  for _, callout in ipairs(callouts) do
    local match = first_line:match(callout.pattern)
    if match then
      return callout, match
    end
    -- Essayer aussi sans capture pour les patterns simples
    if not callout.has_dynamic_title and first_line:match(callout.pattern) then
      return callout, nil
    end
  end
  return nil, nil
end

-- Parse les champs structurés d'un callout
local function parse_structured_fields(blocks, field_list)
  local fields = {}
  local current_field = nil
  local current_content = {}
  local body_content = {}
  local in_body = false

  -- Parcourir les blocs après le titre
  for i = 2, #blocks do
    local block = blocks[i]
    local text = stringify(block)

    -- Chercher un nouveau champ
    local found_field = false
    for label, key in pairs(field_mappings) do
      local pattern = "^%*" .. label .. "%*%s*:%s*"
      local content = text:match(pattern .. "(.+)")
      if content then
        -- Sauvegarder le champ précédent
        if current_field then
          fields[current_field] = table.concat(current_content, " ")
        end
        -- Nouveau champ
        current_field = key
        current_content = {content}
        found_field = true
        break
      end
    end

    -- Si pas de nouveau champ, continuer le champ courant ou ajouter au body
    if not found_field then
      if current_field then
        table.insert(current_content, text)
      else
        table.insert(body_content, text)
      end
    end
  end

  -- Sauvegarder le dernier champ
  if current_field then
    fields[current_field] = table.concat(current_content, " ")
  end

  return fields, table.concat(body_content, "\n\n")
end

-- Génère le code Typst pour un callout simple
local function generate_simple_callout(func_name, content)
  -- Échapper les caractères spéciaux Typst dans le contenu
  local escaped = content:gsub("\\", "\\\\")
                        :gsub("%[", "\\[")
                        :gsub("%]", "\\]")
                        :gsub("#", "\\#")

  return string.format("#%s[\n%s\n]", func_name, escaped)
end

-- Génère le code Typst pour un callout avec titre dynamique
local function generate_dynamic_callout(func_name, title, content, structured, fields)
  local escaped_title = title:gsub('"', '\\"')

  if structured and next(fields) then
    local params = {}
    table.insert(params, string.format('name: "%s"', escaped_title))

    for key, value in pairs(fields) do
      local escaped_value = value:gsub("\\", "\\\\")
                                 :gsub("%[", "\\[")
                                 :gsub("%]", "\\]")
                                 :gsub("#", "\\#")
      table.insert(params, string.format('%s: [%s]', key, escaped_value))
    end

    return string.format("#%s(\n  %s\n)", func_name, table.concat(params, ",\n  "))
  else
    local escaped = content:gsub("\\", "\\\\")
                          :gsub("%[", "\\[")
                          :gsub("%]", "\\]")
                          :gsub("#", "\\#")

    return string.format('#%s(name: "%s")[\n%s\n]', func_name, escaped_title, escaped)
  end
end

-- Génère le code Typst pour un callout structuré
local function generate_structured_callout(func_name, fields, body)
  local params = {}

  for key, value in pairs(fields) do
    local escaped_value = value:gsub("\\", "\\\\")
                               :gsub("%[", "\\[")
                               :gsub("%]", "\\]")
                               :gsub("#", "\\#")
    table.insert(params, string.format('%s: [%s]', key, escaped_value))
  end

  if body and body ~= "" then
    local escaped_body = body:gsub("\\", "\\\\")
                             :gsub("%[", "\\[")
                             :gsub("%]", "\\]")
                             :gsub("#", "\\#")
    table.insert(params, string.format('body: [%s]', escaped_body))
  end

  return string.format("#%s(\n  %s\n)", func_name, table.concat(params, ",\n  "))
end

-- Extrait le contenu après la première ligne (titre)
local function get_content_after_title(blocks)
  local content_parts = {}

  for i = 2, #blocks do
    local block = blocks[i]
    table.insert(content_parts, stringify(block))
  end

  return table.concat(content_parts, "\n\n")
end

-- Fonction principale de transformation des BlockQuotes
function BlockQuote(el)
  local first_line = get_first_line(el.content)

  -- Détecter le type de callout
  local callout_config, captured_title = detect_callout(first_line)

  if callout_config then
    local typst_code

    if callout_config.has_dynamic_title then
      -- Callout avec titre dynamique
      if callout_config.structured then
        local fields, body = parse_structured_fields(el.content, callout_config.fields)
        typst_code = generate_dynamic_callout(
          callout_config.func,
          captured_title,
          body,
          true,
          fields
        )
      else
        local content = get_content_after_title(el.content)
        typst_code = generate_dynamic_callout(
          callout_config.func,
          captured_title,
          content,
          false,
          {}
        )
      end

    elseif callout_config.structured then
      -- Callout structuré sans titre dynamique
      local fields, body = parse_structured_fields(el.content, callout_config.fields)
      typst_code = generate_structured_callout(callout_config.func, fields, body)

    else
      -- Callout simple
      local content = get_content_after_title(el.content)
      typst_code = generate_simple_callout(callout_config.func, content)
    end

    return pandoc.RawBlock('typst', typst_code)
  end

  -- Pas un callout reconnu, retourner tel quel
  return el
end

-- Exporter la fonction
return {
  { BlockQuote = BlockQuote }
}
