"""Build expert-facing Excel templates with encoded options (dropdown validation) for the main and second-expert packages.

Sheets: Extraction (one row per case; first three columns locked), Lists (controlled vocabularies), Instrucoes (short pt-BR guide).
Routes and test systems are split into numbered columns because Excel dropdowns hold one value per cell.
Every list contains NOT_STATED so the unknown convention can be used inside the dropdowns.
"""
import csv
import os
from openpyxl import Workbook
from openpyxl.comments import Comment
from openpyxl.styles import Alignment, Font, PatternFill, Protection, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation

R = r'c:\Users\leohm\AI_projects\Assist3R\docs\protocol\reference'

LISTS = {
    'species': ['human', 'rat', 'mouse', 'rabbit', 'guinea_pig', 'dog', 'bovine', 'chicken', 'zebrafish', 'rainbow_trout',
                'horseshoe_crab', 'salmonella_typhimurium', 'escherichia_coli', 'horse', 'tachypleus_tridentatus', 'in_vitro', 'other', 'NOT_STATED'],
    'sex': ['male', 'female', 'both', 'NOT_STATED'],
    'route': ['cutaneous', 'inhalation', 'oral', 'ocular', 'intranasal', 'intratracheal', 'intravenous', 'intra-arterial', 'intramuscular',
              'subcutaneous', 'intradermal', 'intraperitoneal', 'rectal', 'vaginal', 'topical-mucosal', 'implantation', 'multiple',
              'not-applicable', 'unspecified', 'other', 'aquatic-waterborne', 'NOT_STATED'],
    'test_system': ['in_vivo', 'ex_vivo', 'in_vitro', 'in_chemico', 'in_silico', 'in_data', 'NOT_STATED'],
    'application': ['basic-research', 'translational-applied-research', 'regulatory-use', 'routine-production', 'education-training',
                    'environmental-protection', 'species-preservation', 'forensic-inquiry', 'diagnostic-testing', 'other', 'NOT_STATED'],
    'yes_no': ['yes', 'no'],
}

# (column name, kind, width, header comment)
COLS = [
    ('case_id', 'locked', 9, 'Identificador do caso (não alterar).'),
    ('source_file', 'locked', 13, 'Arquivo do artigo na pasta sources/ (não alterar).'),
    ('procedure_to_extract', 'locked', 48, 'Qual procedimento extrair. Extraia somente este (não alterar).'),
    ('expert_id', 'text', 11, 'Seu identificador (o mesmo em todas as linhas).'),
    ('minutes_spent', 'minutes', 10, 'Minutos do primeiro clique até a linha completa (número).'),
    ('study_type', 'text', 26, 'Nome curto do estudo ou modelo.'),
    ('procedure_text', 'text', 52, 'Resumo do procedimento em 1-3 frases, fiel ao texto.'),
    ('species', ('list', 'species'), 16, 'Espécie dos animais do procedimento. NOT_STATED se o texto não informa.'),
    ('strain_or_line', 'text', 18, 'Linhagem, cepa ou linha transgênica. NOT_STATED se não informada.'),
    ('sex', ('list', 'sex'), 11, 'male, female, both ou NOT_STATED.'),
    ('age_or_weight', 'text', 20, 'Idade e/ou peso na entrada, com unidade. NOT_STATED se não informado.'),
    ('animal_counts_total', 'count', 12, 'Número inteiro de animais do procedimento, ou NOT_STATED.'),
    ('animal_counts_per_group', 'text', 14, 'Animais por grupo (número ou n1/n2/n3) ou NOT_STATED.'),
    ('route_1', ('list', 'route'), 15, 'Via principal do procedimento (anestesia/sedação/eutanásia não contam).'),
    ('route_2', ('list', 'route'), 15, 'Segunda via, se houver.'),
    ('route_3', ('list', 'route'), 15, 'Terceira via, se houver.'),
    ('dose_and_frequency', 'text', 30, 'Substância(s), dose(s) com unidade e frequência. NOT_STATED se não informado.'),
    ('duration_and_timepoints', 'text', 28, 'Duração do tratamento e momentos de avaliação. NOT_STATED se não informado.'),
    ('test_system_1', ('list', 'test_system'), 13, 'Sistema de teste principal do procedimento.'),
    ('test_system_2', ('list', 'test_system'), 13, 'Segundo sistema de teste, se houver.'),
    ('application', ('list', 'application'), 22, 'Finalidade do estudo.'),
    ('endpoints', 'text', 34, 'Desfechos medidos, separados por ponto e vírgula, nos termos do artigo.'),
    ('regulatory_or_guideline_reference', 'text', 20, 'Diretriz citada (ex.: OECD TG 420) ou none.'),
    ('not_stated_fields', 'text', 24, 'Nomes dos campos que o texto NÃO informa, separados por ponto e vírgula.'),
    ('inferred_fields', 'text', 24, 'Campos que você INFERIU do texto (não estão escritos); explique em expert_notes.'),
    ('referenced_fields', 'text', 24, 'Campos que o texto apenas REMETE a outro trabalho ("como descrito anteriormente").'),
    ('ask_for_clarification', ('list', 'yes_no'), 14, 'yes se faltar informação que impeça descrever o procedimento para buscar métodos alternativos.'),
    ('clarification_questions', 'text', 40, 'Se yes: até 3 perguntas objetivas ao autor.'),
    ('expert_notes', 'text', 44, 'Observações; até 2 trechos literais (via, dose, n) entre aspas.'),
]

INSTR = [
    'Extração de referência: instruções rápidas (versão completa em LEIA-ME_instrucoes_especialista.md)',
    '',
    '1. Trabalhe sozinho(a); não use ferramentas de IA; use apenas o texto do artigo (inclusive tabelas e legendas).',
    '2. Para cada linha: abra sources/<case_id>, leia procedure_to_extract e extraia SOMENTE esse procedimento.',
    '3. As colunas com seta têm lista suspensa. Escolha um valor da lista; se o texto não informa, escolha NOT_STATED.',
    '4. Em colunas de texto livre, escreva NOT_STATED quando o texto não informa o dado.',
    '5. Via (route_1 a route_3) e sistema de teste (test_system_1/2): preencha uma coluna por valor; deixe as demais vazias.',
    '6. Anestesia, sedação e eutanásia NÃO contam como via do procedimento.',
    '7. not_stated_fields / inferred_fields / referenced_fields: liste os NOMES dos campos (separados por ponto e vírgula).',
    '   NOT_STATED = o texto não informa. INFERRED = deduzido do texto (explique em expert_notes). REFERENCED = o texto remete a outro trabalho.',
    '8. ask_for_clarification = yes quando faltar informação que impeça descrever o procedimento para buscar métodos alternativos.',
    '9. Cronometre cada caso e registre minutes_spent.',
    '10. As três primeiras colunas são protegidas (Revisão > Desproteger planilha, sem senha, se precisar editar).',
    '11. Salve como extraction_<expert_id>.xlsx e devolva à equipe.',
]

thin = Side(style='thin', color='BBBBBB')
BORDER = Border(left=thin, right=thin, top=thin, bottom=thin)


def build(src_csv, out_xlsx):
    rows = list(csv.DictReader(open(src_csv, encoding='utf-8-sig')))
    rows.sort(key=lambda r: r['case_id'])
    wb = Workbook()
    ws = wb.active
    ws.title = 'Extraction'
    lst = wb.create_sheet('Lists')
    ins = wb.create_sheet('Instrucoes')

    # Lists sheet
    ranges = {}
    for ci, (name, vals) in enumerate(LISTS.items(), 1):
        lst.cell(row=1, column=ci, value=name).font = Font(bold=True)
        for ri, v in enumerate(vals, 2):
            lst.cell(row=ri, column=ci, value=v)
        col = get_column_letter(ci)
        ranges[name] = "=Lists!$%s$2:$%s$%d" % (col, col, len(vals) + 1)
        lst.column_dimensions[col].width = 30

    # Header
    head_fill = PatternFill('solid', fgColor='1F4E78')
    lock_fill = PatternFill('solid', fgColor='E7E6E6')
    for ci, (name, kind, width, note) in enumerate(COLS, 1):
        c = ws.cell(row=1, column=ci, value=name + (' \u25BE' if isinstance(kind, tuple) else ''))
        c.font = Font(bold=True, color='FFFFFF')
        c.fill = head_fill
        c.alignment = Alignment(wrap_text=True, vertical='center')
        c.comment = Comment(note, 'Estudo')
        ws.column_dimensions[get_column_letter(ci)].width = width
    ws.row_dimensions[1].height = 34
    ws.freeze_panes = 'D2'

    # Data rows
    n = len(rows)
    last = n + 1
    for ri, r in enumerate(rows, 2):
        for ci, (name, kind, width, note) in enumerate(COLS, 1):
            c = ws.cell(row=ri, column=ci)
            c.border = BORDER
            c.alignment = Alignment(wrap_text=True, vertical='top')
            if kind == 'locked':
                c.value = r[name]
                c.fill = lock_fill
                c.protection = Protection(locked=True)
            else:
                c.protection = Protection(locked=False)
        ws.row_dimensions[ri].height = 48

    # Validations
    for ci, (name, kind, width, note) in enumerate(COLS, 1):
        col = get_column_letter(ci)
        rng = '%s2:%s%d' % (col, col, last)
        if isinstance(kind, tuple):
            dv = DataValidation(type='list', formula1=ranges[kind[1]], allow_blank=True, showErrorMessage=True,
                                errorTitle='Valor fora da lista', error='Escolha um valor da lista suspensa (ou NOT_STATED).')
            dv.promptTitle = name
            dv.prompt = note[:250]
            dv.showInputMessage = True
        elif kind == 'minutes':
            dv = DataValidation(type='decimal', operator='greaterThanOrEqual', formula1='0', allow_blank=True, showErrorMessage=True,
                                errorTitle='Número', error='Informe os minutos como número (ex.: 12 ou 12.5).')
        elif kind == 'count':
            first = '%s2' % col
            dv = DataValidation(type='custom', formula1='=OR(%s="",%s="NOT_STATED",AND(ISNUMBER(%s),%s>=0,%s=INT(%s)))' % ((first,) * 6),
                                allow_blank=True, showErrorMessage=True, errorTitle='Número inteiro ou NOT_STATED',
                                error='Informe um número inteiro de animais ou NOT_STATED.')
        else:
            continue
        ws.add_data_validation(dv)
        dv.add(rng)

    ws.protection.sheet = True
    ws.protection.formatColumns = False
    ws.protection.formatRows = False
    ws.protection.formatCells = False
    ws.protection.autoFilter = False
    ws.protection.sort = False
    ws.auto_filter.ref = 'A1:%s%d' % (get_column_letter(len(COLS)), last)

    for i, line in enumerate(INSTR, 1):
        c = ins.cell(row=i, column=1, value=line)
        if i == 1:
            c.font = Font(bold=True, size=12)
    ins.column_dimensions['A'].width = 150
    wb.move_sheet('Instrucoes', offset=-2)  # Instrucoes first
    wb.active = wb.sheetnames.index('Extraction')
    wb.save(out_xlsx)
    return n


if __name__ == '__main__':
    n1 = build(R + r'\expert_package\extraction_template.csv', R + r'\expert_package\extraction_template.xlsx')
    n2 = build(R + r'\expert_package_second\extraction_template.csv', R + r'\expert_package_second\extraction_template.xlsx')
    print('main rows', n1, '| second rows', n2)
