"""Add a neutral `procedure_to_extract` column to the expert template (and the study-team key).
Descriptions name only the animal procedure of the case; they do not mention stratum, relevance or missing information."""
import csv

R = r'c:\Users\leohm\AI_projects\Assist3R\docs\protocol\reference'
D = {
    '41149379': 'The skin irritation test in rats (Draize-type scoring of erythema and edema over 72 h).',
    '36638280': 'The oxazolone-induced contact hypersensitivity model in C57BL/6 mice treated with melittin nanoparticles.',
    '34453447': 'The primary irritancy / local lymph node assay in female BALB/c mice (ear application for 3 days).',
    '39195502': 'The LPS-induced fever model in rabbits (intravenous LPS, rectal temperature) used to test an antipyretic compound.',
    '39204150': 'The acute oral toxicity test in Swiss female mice (single oral dose, 14-day observation).',
    '39033177': 'The reproductive and developmental toxicity study in Sprague-Dawley rats (F0 and F1 generations).',
    '31732351': 'The in vivo TCDD dosing study in E-Rep transgenic reporter mice.',
    '35698798': 'The in vivo bone-marrow micronucleus test in Swiss mice treated with the plant extract.',
    '33396137': 'The waterborne nitrate exposure experiment in juvenile turbot.',
    '36839049': 'The ocular irritation test (Draize protocol) in New Zealand rabbits with the nanoparticle formulation.',
    '31696971': 'The nude-mouse subcutaneous xenograft experiment with SNHG16-knockdown hepatocellular carcinoma cells.',
    '32826981': 'The yohimbine-induced reinstatement of alcohol seeking in rats with intra-amygdala CART antibody microinjection.',
    '34788609': 'Whole-organ imaging and immunofluorescence analysis of prostate cancer and its metastases in the RapidCaP mouse model.',
    '39002748': 'The exposure experiment in juvenile hook snout carp to beta-cypermethrin and pyraclostrobin, alone and combined.',
    '39729092': 'The intracardiac injection of radiolabelled cancer cells in mice followed by PET imaging.',
    '39872463': 'The bleomycin-induced pulmonary fibrosis model in mice treated with MSC-derived exosomes.',
    '40187127': 'The zebrafish thrombosis model with Ligusticum chuanxiong powder treatment.',
    '40252789': 'The doxorubicin-induced heart failure model in rats treated with acetylcholine receptor agonists.',
    '40744994': 'The hepatocyte-specific Kctd17 knockdown experiment in mice fed a MASH-inducing diet.',
    '41045458': 'The LPS-induced systemic inflammation model in mice with ventrolateral periaqueductal gray circuit manipulation.',
    '33804656': 'The 10-day broad-spectrum antibiotic treatment in young and older mice with gut microbiota follow-up.',
    '35045097': 'The intraperitoneal injection of cannabidiol or THC in male rats with tissue distribution measurement.',
    '35933977': 'The repeated sodium dodecyl sulfate application to mouse ear skin (detergent-induced dermatitis).',
    '37426013': 'The mouse immunization and Japanese encephalitis virus challenge experiment with chimeric Tembusu virus vaccine candidates.',
    '38450510': 'The sFlt1 versus control adenovirus injection at gestation day 9 in LDLR-knockout mice, with later atherosclerosis assessment.',
    '38849933': 'The hindlimb-unloading osteoporosis model in mice.',
    '39373701': 'The behavioural testing of mice with brain-specific RagA overexpression.',
    '39540281': 'The kidney progenitor Vegfc overexpression (Six2Cre;Vegfc) mouse model and its phenotyping.',
    '41238577': 'The LPS-induced septic acute kidney injury model in mice treated with GTS-21.',
    '41254715': 'The cyclophosphamide-induced premature ovarian failure model in rats treated with platelet-rich plasma.',
}
key = list(csv.DictReader(open(R + r'\reference_case_key.csv', encoding='utf-8-sig')))
assert sorted(k['pmid'] for k in key) == sorted(D), (set(k['pmid'] for k in key) ^ set(D))
by = {k['case_id']: D[k['pmid']] for k in key}


def rewrite(path, after, rowkey):
    rows = list(csv.DictReader(open(path, encoding='utf-8-sig')))
    fn = list(rows[0].keys())
    if 'procedure_to_extract' not in fn:
        fn.insert(fn.index(after) + 1, 'procedure_to_extract')
    for r in rows:
        r['procedure_to_extract'] = by[r['case_id']]
    with open(path, 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fn)
        w.writeheader()
        w.writerows(rows)
    return len(rows)


print('template rows', rewrite(R + r'\expert_package\extraction_template.csv', 'source_file', 'case_id'))
print('key rows', rewrite(R + r'\reference_case_key.csv', 'title', 'case_id'))
