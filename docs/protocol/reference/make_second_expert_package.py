"""Build the second-expert package: only the 10 cases flagged for independent review, blank template, same sources and instructions.
The second expert must not see the first expert's answers (protocol section 4)."""
import csv, os, shutil

R = r'c:\Users\leohm\AI_projects\Assist3R\docs\protocol\reference'
OUT = R + r'\expert_package_second'
os.makedirs(OUT + r'\sources', exist_ok=True)
key = [k for k in csv.DictReader(open(R + r'\reference_case_key.csv', encoding='utf-8-sig')) if k['second_expert_review'] == 'yes']
ids = sorted(k['case_id'] for k in key)
assert len(ids) == 10
tmpl = [t for t in csv.DictReader(open(R + r'\expert_package\extraction_template.csv', encoding='utf-8-sig')) if t['case_id'] in ids]
fn = list(tmpl[0].keys())
for t in tmpl:
    shutil.copyfile(R + r'\expert_package\sources\\' + t['source_file'], OUT + r'\sources\\' + t['source_file'])
with open(OUT + r'\extraction_template.csv', 'w', encoding='utf-8-sig', newline='') as f:
    w = csv.DictWriter(f, fieldnames=fn)
    w.writeheader()
    w.writerows(sorted(tmpl, key=lambda r: r['case_id']))
shutil.copyfile(R + r'\expert_package\LEIA-ME_instrucoes_especialista.md', OUT + r'\LEIA-ME_instrucoes_especialista.md')
open(OUT + r'\LEIA-ME_segundo_especialista.md', 'w', encoding='utf-8').write(
    '# Segundo especialista: revisão independente de 10 casos\n\n'
    'Você recebeu 10 dos 30 casos. Siga as instruções em `LEIA-ME_instrucoes_especialista.md`, '
    'preenchendo a planilha **em branco** `extraction_template.xlsx` a partir do texto original.\n\n'
    '- **Não** consulte a extração do primeiro especialista nem converse com ele sobre estes casos antes da adjudicação.\n'
    '- Os casos usam os mesmos identificadores (RCxx). Divergências serão adjudicadas pela equipe do estudo, em consenso documentado ou por um terceiro especialista (protocolo §4, item 2).\n'
    '- Devolva `extraction_<expert_id>.xlsx` e registre `minutes_spent` por caso.\n')
print('second package cases:', ids)
print('files:', sorted(os.listdir(OUT + r'\sources')))
