**Endpoint (desfecho):** Em toxicologia/farmacologia, é o efeito biológico ou parâmetro mensurável que um estudo se propõe a avaliar — a resposta que o teste captura, não a substância testada nem o método em si. Consenso terminológico em ecotoxicologia regulatória (OECD, ECHA, ANVISA usam o termo nesse sentido).
Exemplos de endpoint: irritação ocular, corrosão cutânea, sensibilização cutânea (alergenicidade), genotoxicidade, toxicidade aguda, fototoxicidade, pirogenicidade. Cada um responde a uma pergunta regulatória distinta (ex.: "esta substância corrói a pele?" → endpoint = corrosão cutânea).

**Método:** Uma técnica discreta e validável que produz um dado mensurável para um único endpoint_category — ex.: TG 439 EpiSkin produz um valor de viabilidade celular que classifica irritação cutânea. 

**Metodologia:** Um desenho experimental ou estratégia mais ampla que responde a uma pergunta de pesquisa, potencialmente combinando ou sequenciando múltiplos métodos — ex.: uma IATA (Integrated Approach to Testing and Assessment) que combina in silico + in vitro + confirmação in vivo, ou um desenho de estudo comportamental completo.

**Rota:** Descreve como a substância de teste entra em contato com o sistema biológico — não o tipo de sistema biológico - nos métodos de substituição ele refere a quais rotas do protocolo original este método é compatível para substituir — use null quando for compatível com qualquer rota.

**Aplicação (application):** Finalidade ou uso pretendido de um estudo ou método (ex.: pesquisa básica, uso regulatório, ensino). Antigo “domínio do estudo” (study_domain).

**Uso de animais (`animal_use`):** Como um método do catálogo utiliza animais ou materiais derivados de animais — um único valor de vocabulário controlado em `methods`, usado para curadoria, filtragem e exibição nos cards de resultado. Valores (definições canônicas no ADR-026):
- **Nenhum** — nenhum animal e nenhum material de origem animal é utilizado.
- **Material derivado de animal** — são usados produtos obtidos de animais (soros, anticorpos, enzimas, …), sem que animais sejam mortos para a coleta de tecido deste método.
- **Subproduto de abatedouro** — tecidos/órgãos de animais já abatidos para alimentação ou outros fins primários (ex.: córneas bovinas pós-abate no EVEIT).
- **Animais sacrificados para tecido** — animais são mortos especificamente para obter tecido para o método.
- **Animais vivos** — animais vivos são usados no procedimento.
- **Misto ou variável** — mais de uma das opções acima claramente se aplica, ou o uso varia.

Pode ser null durante a curadoria quando o documento de origem não sustenta claramente uma classificação; null significa “não classificado”, nunca “Nenhum”.

**Contagem de animais (`animal_counts`):** Número estruturado de animais extraído do protocolo submetido: **Fêmeas**, **Machos**, **Total**, **Por grupo**. Somente subcampos explicitamente declarados no texto do protocolo são preenchidos; valores derivados são proibidos (ADR-017). Null quando o protocolo não tem coorte experimental de animais significativa (ex.: subprodutos de abate — ver exemplo EVEIT no `parameter_model.md` §8). Exibido no S2; ver `parameter_model.md` §4.