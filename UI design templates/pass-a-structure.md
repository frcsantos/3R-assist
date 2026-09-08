# Design — Pass A: Estrutura das Telas

> M2.5, Pass A — Low-fi (wireframes, boxes + labels)
> Pergunta respondida: onde cada coisa fica? Qual o formato da navegação?
> Fidelidade: nenhuma — apenas estrutura e hierarquia.
>
> Pass B (visual/estilo) e Pass C (protótipo interativo) são opcionais no Minimal tier.
> Decidir antes de iniciar M3.

---

## Forma da navegação

**Padrão:** Top navigation bar, sempre visível.

```
[Logo: Assist3R]  [Analisar]  [Buscar]          [Entrar / email]
```

- **Analisar** (S1) — rota padrão, ativa no estado vazio
- **Buscar** (S4) — busca direta com filtros estruturados
- **Entrar / email** — auth state toggle; usuário logado vê email truncado + acesso a S5
- **Sugerir método** (S6) — não está no nav principal; acessível via link no rodapé e em S3

**Fluxo primário:** S1 → S2 → S3 (análise de protocolo)
**Fluxo secundário:** S4 (busca direta, sem IA)
**Fluxo de suporte:** S5 (histórico), S6 (sugestão)

---

## S1 — Input

```
┌─────────────────────────────────────────────────────────────────┐
│ [nav: Analisar* | Buscar]                      [Entrar]         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   Descreva seu protocolo experimental                            │
│   Em português ou inglês.                                        │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ [PT] [EN]   ← toggle de idioma                           │   │
│  │                                                          │   │
│  │  Área de texto livre (6+ linhas)                         │   │
│  │  placeholder: "Utilizamos camundongos Wistar para..."    │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│  [Analisar protocolo →]                                          │
│                                                                  │
│  ─────────────────────────────────────────────────────────────  │
│  Já sabe o que procura? [Busca direta →]                        │
│                                                                  │
│  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  · │
│  Continuar sem conta (anônimo) — histórico disponível após       │
│  cadastro                                                        │
└─────────────────────────────────────────────────────────────────┘
```

**Decisões estruturais:**
- Toggle PT/EN dentro do campo, não fora — contexto imediato para o usuário
- CTA única — sem ambiguidade sobre o que acontece ao submeter
- Bypass anônimo visível mas discreto (não proeminente o suficiente para parecer o caminho principal)
- Link para S4 abaixo do CTA principal — não concorre com o fluxo primário

---

## S2 — Parâmetros extraídos

```
┌─────────────────────────────────────────────────────────────────┐
│ [nav]                                                            │
├─────────────────────────────────────────────────────────────────┤
│  ← Editar protocolo                        [Alta confiança]     │
│                                                                  │
│  Parâmetros extraídos                                            │
│  Confirme ou corrija antes de buscar.                            │
│                                                                  │
│  Modelo biológico    [campo editável: Mus musculus            ]  │
│  Objetivo            [campo editável: Teste de toxicidade ag. ]  │
│  Procedimento        [campo editável: Inalação                ]  │
│  Endpoint            [campo vazio/destacado — incompleto      ]  │
│  Área de aplicação   [campo editável: Segurança de substâncias]  │
│                                                                  │
│  "Endpoint incompleto pode reduzir precisão"                     │
│                                                    [Buscar →]   │
└─────────────────────────────────────────────────────────────────┘
```

**Decisões estruturais:**
- Gate obrigatório: busca não roda ao sair de S1; passa sempre por S2
- Campos editáveis inline — sem modal, sem nova tela
- Indicador de confiança no header (alto/médio/baixo)
- Campo vazio/incompleto destacado visualmente (não bloqueante — usuário pode prosseguir)
- CTA única: "Buscar alternativas"

---

## S3 — Resultados

```
┌─────────────────────────────────────────────────────────────────┐
│ [nav]                                                            │
├─────────────────────────────────────────────────────────────────┤
│  4 alternativas encontradas           [Exportar PDF] [CSV]      │
│  Mus musculus · toxicidade aguda · inalação · segurança          │
│                                                                  │
│  Filtrar: [Classe 3Rs ↓]  [Jurisdição ↓]                       │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  [Substituição] [Brasil/Intl.] [ECVAM validado]   95%   │    │
│  │  EPISKIN™ in vitro acute inhalation testing              │    │
│  │  Correspondências: modelo biológico · procedimento       │    │
│  │  [EURL ECVAM TSAR]  [OECD TG 439]                       │    │
│  └─────────────────────────────────────────────────────────┘    │
│  [card 2 — 82%]                                                  │
│  [card 3 — 61%]                                                  │
│                                                                  │
│  ─────────────────────────────────────────────────────────────  │
│  Esta consulta foi útil?  [1] [2] [3] [4] [5]                   │
│  + campo de comentário opcional                                  │
│                                                                  │
│  Sugerir método não listado →                                    │
└─────────────────────────────────────────────────────────────────┘
```

**Decisões estruturais:**
- Resumo dos parâmetros usados logo abaixo do header — âncora para o usuário
- Filtros em bar horizontal (não sidebar) — corpus pequeno não justifica sidebar
- Cards ordenados por score, badge 3Rs em primeiro lugar
- Parâmetros correspondentes por extenso no card — transparência da recomendação (H4)
- Exportação visível para anônimos, mas bloqueada ao clicar (convida a criar conta)
- Feedback (F11) inline no final da lista, sempre visível — não opt-in
- Link para S6 no final da tela, não no nav

---

## S4 — Busca direta

```
┌─────────────────────────────────────────────────────────────────┐
│ [nav: Buscar*]                                                   │
├─────────────────────────────────────────────────────────────────┤
│  ┌───────────────────┐  ┌──────────────────────────────────────┐│
│  │ Filtros           │  │ 20 métodos no banco de dados         ││
│  │                   │  │                                      ││
│  │ Classe 3Rs        │  │ [card: EPISKIN™]                     ││
│  │ [Todas      ↓]    │  │   [Substituição] [Brasil/Intl.]      ││
│  │                   │  │   [ECVAM]                            ││
│  │ Endpoint          │  │                                      ││
│  │ [Todos      ↓]    │  │ [card: RHE model]                    ││
│  │                   │  │   [Substituição] [Intl.]             ││
│  │ Área              │  │   [ALT Web]                          ││
│  │ [Todas      ↓]    │  │                                      ││
│  │                   │  │ [card: ...]                          ││
│  │ Jurisdição        │  │                                      ││
│  │ [Todas      ↓]    │  │                                      ││
│  │                   │  └──────────────────────────────────────┘│
│  │ [Buscar]          │                                          │
│  └───────────────────┘                                          │
└─────────────────────────────────────────────────────────────────┘
```

**Decisões estruturais:**
- Sidebar de filtros (único caso de sidebar no app) — painel fixo à esquerda para comparação iterativa de filtros
- Resultados sem score — busca estruturada não gera ranking semântico
- Sem extração de parâmetros — W2 não passa por S2
- "N métodos no banco de dados" como contexto para o usuário

---

## S5 — Histórico

```
┌─────────────────────────────────────────────────────────────────┐
│ [nav]                                     [pesq@usp.br ↓]      │
├─────────────────────────────────────────────────────────────────┤
│  Histórico de consultas                                          │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ 21 Mai  "camundongo Wistar · inalação aguda..."           │   │
│  │          4 resultados          [Ver ↓]  [PDF]  [CSV]     │   │
│  └──────────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ 18 Mai  "ratos Sprague-Dawley · hepatotoxicidade..."      │   │
│  │          2 resultados          [Ver ↓]  [PDF]  [CSV]     │   │
│  └──────────────────────────────────────────────────────────┘   │
│  [consulta expandida — resultados inline]                        │
│                                                                  │
│  ─────────────────────────────────────────────────────────────  │
│  [Nova consulta →]                                               │
└─────────────────────────────────────────────────────────────────┘
```

**Decisões estruturais:**
- Rota protegida — anônimos redirecionados para S1 com convite de cadastro
- Expansão inline (accordion), sem navegação para nova tela
- Export por consulta (PDF e CSV) — não export global
- CTA "Nova consulta" no final — jornada contínua

---

## S6 — Sugestão de método

```
┌─────────────────────────────────────────────────────────────────┐
│ [nav]                                                            │
├─────────────────────────────────────────────────────────────────┤
│  Sugerir um método                                               │
│  Sugestões são revisadas pela equipe antes de publicação.        │
│                                                                  │
│  Nome do método    [campo: ex. EpiDerm™ skin irritation     ]    │
│  URL da fonte      [campo: https://...                      ]    │
│  Classe 3Rs        [seletor: Substituição / Redução / Ref. ↓]   │
│  Notas (opcional)  [textarea: contexto, endpoint, ref. reg.]     │
│                                                                  │
│  [Enviar sugestão]                                               │
│                                                                  │
│  ─────────────────────────────────────────────────────────────  │
│  ℹ  Sua sugestão entra numa fila de curadoria manual.           │
│     Não há prazo definido de publicação.                         │
└─────────────────────────────────────────────────────────────────┘
```

**Decisões estruturais:**
- Formulário mínimo — 4 campos, 1 obrigatório (nome)
- Auth não obrigatório — email do usuário logado pré-preenchido se disponível
- Nota de expectativa gerenciada: sem prazo — evita frustração

---

## Checklist de validação do Pass A

- [ ] Toda feature do Minimal (F01–F14) tem superfície de UI correspondente
- [ ] Todo workflow em 2.10 pode ser percorrido de ponta a ponta neste mapa
- [ ] Um não-envolvido consegue executar a tarefa primária sem orientação (testar com 1 pessoa antes do M3)
- [ ] Nenhuma decisão de design contradiz `spec.md` ou `decisions.md`

---

## Questões em aberto para Pass B

1. Tom visual: ferramenta científica formal vs. acessível para pesquisadores juniores?
2. Densidade de informação nos cards de resultado: quantos campos são exibidos por padrão vs. expandidos?
3. Mobile: a tela S2 (5 campos editáveis) funciona em viewport estreito? Considerar stacking vertical.
4. Idioma padrão da UI: PT com EN como opção, ou detecção automática?

---

*Pass A concluído. Referência para M3: `/design/pass-a-structure.md`*
