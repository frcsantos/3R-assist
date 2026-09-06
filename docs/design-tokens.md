# Design Tokens — 3R Assist

> **Canonical visual source:** Ethos Research System (`UI design templates/Ethos Theme/ethos_research_system/DESIGN.md`)
> **Implementation artifacts:** `design/tokens.css` (CSS custom properties), `design/ethos-theme.css` (Tailwind v4 `@theme` bridge — used by the frontend), `design/tailwind.preset.js` (Tailwind v3 reference / non-v4 consumers)
> Desvios no M3 requerem entrada no `execution-log.md`.

---

## Philosophy

Scientific Precision — warm off-white surfaces, flat borders (no shadows), high information density. Chromatic color is reserved for 3R badges and jurisdiction indicators only.

---

## Tipografia

| Token | Valor | Uso |
|---|---|---|
| `--font-sans` / `font-body-base` | DM Sans (fallback: system-ui) | Toda a interface |
| `--font-mono` / `font-monospace-data` | DM Mono (fallback: monospace) | Scores, IDs, parâmetros extraídos |
| `headline-lg` | 17px / 500 / 24px lh | Títulos de página e seção |
| `body-base` | 14px / 400 / 1.6 lh | Corpo |
| `nav-link` | 13px / 400 | Links de navegação |
| `card-title` | 13px / 500 / 1.4 lh | Nomes de métodos, títulos de card |
| `label-caps` | 13px / 500 / 0.04em ls | Labels de seção (uppercase) |
| `badge-button` | 12px / 500 | Badges, botões pequenos |
| `metadata` | 12px / 400 | Metadados, breadcrumbs |
| `small-label` | 11px / 500 / 0.06em ls | Labels de campo (uppercase) |
| `monospace-data` | 12px / 400 | Scores, contagens, IDs |

---

## Cores — superfícies

| Token Ethos | Hex | Uso |
|---|---|---|
| `background` / `--bg` | `#faf9f5` | Fundo de página (off-white quente) |
| `surface-container-lowest` | `#ffffff` | Cards, inputs, nav, app frame |
| `surface-container-low` | `#f5f4f0` | Painéis secundários, sidebar |
| `surface-container` | `#efeeea` | Linhas de tabela, fundos de hover |
| `surface-container-high` | `#e9e8e4` | Hover em chips, lang toggle track |
| `border-subtle` / `--border` | `#E4E2DB` | Bordas padrão |
| `border-emphasis` / `--border-md` | `#CBC9C1` | Inputs, hover em cards |
| `on-surface` / `--text-1` | `#1b1c1a` | Texto primário, CTA fill |
| `on-surface-variant` / `--text-2` | `#494740` | Texto secundário, labels |
| `text-tertiary` / `--text-3` | `#A09E96` | Placeholders, metadados fracos |

**Nota de migração Pass B → Ethos:** `--bg` era `#F7F6F2` e `--text-2` era `#6B6960`. Ethos adota `#faf9f5` e `#494740`. Aliases legados em `design/tokens.css` apontam para os valores Ethos.

---

## Cores semânticas — 3Rs

Regra: **badges 3Rs são o único uso de cor cromática estrutural na interface.**

| Classe | Background | Texto | Borda |
|---|---|---|---|
| Replacement / Substituição | `#EAF3DE` | `#27500A` | `#639922` |
| Reduction / Redução | `#FAEEDA` | `#633806` | `#BA7517` |
| Refinement / Refinamento | `#E1F5EE` | `#085041` | `#1D9E75` |

---

## Cores semânticas — jurisdição e status

| Classe | Background | Texto | Borda | Quando usar |
|---|---|---|---|---|
| Brasil / Intl. | `#E6F1FB` | `#0C447C` | `#378ADD` | validado nos dois contextos |
| Intl. apenas | `#F1EFE8` | `#5F5E5A` | `#B4B2A9` | sem validação CONCEA |
| Brasil apenas | `#FAEEDA` | `#633806` | `#BA7517` | validado CONCEA, não ECVAM |
| Info callout | `#E6F1FB` | `#0C447C` | `#378ADD` | insights automáticos (S3) |

---

## Espaçamento

| Token | Valor | Uso |
|---|---|---|
| `container-padding` | 24px | Padding lateral de página |
| `section-gap` | 48px | Entre seções principais |
| `card-gap` | 16px | Entre cards |
| `element-gap` | 12px | Entre elementos relacionados |
| `fine-gap` | 8px | Clusters de metadados |
| `gutter` | 16px | Grid gutters (12 colunas) |

---

## Raios

| Token | Valor | Uso |
|---|---|---|
| `rounded-md` | 12px (0.75rem) | Botões, chips |
| `rounded-lg` | 16px (1rem) | Cards, inputs |
| `rounded-xl` | 24px (1.5rem) | App frame externo |
| `rounded-full` | pill | Badges 3R, lang toggle |

---

## Componentes-chave

### Card de resultado
- Borda: `1px solid border-subtle`, `rounded-lg`
- Fundo: `surface-container-lowest`
- Hover: `border-emphasis` (120ms)
- Score ≤ 65%: `opacity: 0.65` (ADR-011)
- Score: `font-monospace-data`, canto superior direito

### CTA primário
- Fundo: `primary` (`#000000`), texto `on-primary`
- `rounded-md`, sem sombra
- Hover: `opacity: 0.9`

### CTA secundário
- Borda: `border-emphasis`, fundo `surface-container-lowest`
- Hover: `surface-container`

### Input de protocolo
- Shell: `surface-container-lowest`, borda `border-emphasis`, `rounded-lg`
- Focus: `border-primary`, sem glow
- Lang toggle: pills dentro do campo

### Navigation
- Altura: 64px (`h-nav`)
- Ativo: `border-b-2 border-primary`, `font-weight: 500`
- Fundo: `background`, borda inferior `border-subtle`

### Ícones
- Material Symbols Outlined, 18px
- Stroke icons custom: 14×14px, weight 1.8 (quando não usar Material)

---

## Elevação

**Strictly flat** — sem box-shadow. Profundidade via bordas e opacidade.

Exceção documentada no template de relatório (`glass-panel`): evitar em implementação MVP; usar `surface-container-lowest` + `border-subtle`.

---

## Questão aberta para validação

O tom quente (`#faf9f5`) precisa ser validado com a Karynn antes de M3 completo.

**Como testar:** mostrar templates Ethos (`entrada_de_protocolo`, `relat_rio_de_an_lise`) para 2–3 pesquisadores/CEUAs. Pergunta: "Você submeteria uma consulta usando esta ferramenta em contexto de revisão de protocolo?"

---

*Atualizado em M2.5 — Ethos theme adotado como base visual. Referência para M3 implementação frontend.*
