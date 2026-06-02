"""
NEXOR -- ATUALIZADOR CATALOGO CFE v1
Atualiza o server.py:
1. Remove referencias ao Brasil/LGPD do contexto law_cfe
2. Adiciona os 7 novos dominios CFE 2026 ao catalogo
3. Atualiza versao e contexto geral do CFE

USO:
    python atualizar_catalogo_cfe.py
"""

import re
import shutil
from datetime import datetime

SERVER_FILE = "server.py"
TIMESTAMP   = datetime.now().strftime("%Y%m%d_%H%M")

# ─────────────────────────────────────────────────────────────
# CORRECAO 1: Limpa contexto law_cfe — remove Brasil/LGPD
# ─────────────────────────────────────────────────────────────
OLD_LAW_CONTEXT = (
    '{"id": "law_cfe", "name": "Law",\n'
    '             "context": "CFE Fraud Examiners Manual 2024 — Law. Topics: criminal law, civil law, employment law, whistleblower protections, expert witness, SOX, FCPA, Brazil Lei 12.846/2013, LGPD, wire fraud, bank fraud."}'
)

NEW_LAW_CONTEXT = (
    '{"id": "law_cfe", "name": "Law — US Federal Law",\n'
    '             "context": "CFE Fraud Examiners Manual 2026 — Law. Topics: US federal fraud statutes (wire fraud 18 USC 1343, mail fraud 18 USC 1341, money laundering 18 USC 1956), FCPA anti-bribery and accounting provisions, SOX whistleblower protections, RICO, BSA/AML, Dodd-Frank, False Claims Act, Federal Sentencing Guidelines, PCAOB, SEC enforcement, DOJ prosecution procedures, expert witness testimony."}'
)

# ─────────────────────────────────────────────────────────────
# CORRECAO 2: Adiciona 7 novos dominios CFE 2026
# ─────────────────────────────────────────────────────────────
OLD_PREVENTION = (
    '{"id": "prevention_deterrence", "name": "Fraud Prevention & Deterrence",\n'
    '             "context": "CFE Fraud Examiners Manual 2024 — Fraud Prevention & Deterrence. Topics: fraud risk management, COSO framework, corporate governance, ethics programs, fraud risk assessment, internal controls, hotlines, tone at the top."}\n'
    '        ]\n'
    '    },'
)

NEW_PREVENTION_PLUS_DOMAINS = (
    '{"id": "prevention_deterrence", "name": "Fraud Prevention & Deterrence",\n'
    '             "context": "CFE Fraud Examiners Manual 2026 — Section 3: Fraud Prevention and Deterrence. Topics: Fraud Triangle and Diamond, occupational fraud statistics (ACFE Report to the Nations), corporate governance, board and audit committee responsibilities, management and auditor duties, fraud risk assessment (COSO), internal controls, anti-fraud programs, whistleblower hotlines, pre-employment screening, ethics for fraud examiners (ACFE Code)."},\n'
    '            {"id": "data_theft_ip", "name": "Theft of Data & Intellectual Property",\n'
    '             "context": "CFE Exam 2026 — Section 1 Domain S1D07: Theft of Data and Intellectual Property. Topics: trade secret definition and protection, Economic Espionage Act (EEA), Defend Trade Secrets Act (DTSA), methods of data exfiltration (USB, cloud, email), insider threat scenarios, foreign state-sponsored economic espionage, forensic evidence in IP theft, chain of custody for digital evidence, civil vs criminal remedies, cross-border IP theft jurisdiction."},\n'
    '            {"id": "insurance_fraud", "name": "Insurance Fraud",\n'
    '             "context": "CFE Exam 2026 — Section 1 Domain S1D12: Insurance Fraud. Topics: hard fraud vs soft fraud, premium diversion, staged accident schemes, arson for profit, workers compensation fraud, healthcare-related insurance fraud, life insurance fraud, multiple-claim fraud, disability fraud, Special Investigations Units (SIU), National Insurance Crime Bureau (NICB), Examination Under Oath (EUO), detection methods and civil/criminal remedies."},\n'
    '            {"id": "consumer_fraud", "name": "Consumer Fraud & Scams",\n'
    '             "context": "CFE Exam 2026 — Section 1 Domain S1D13: Consumer Fraud and Scams. Topics: advance fee fraud (419 fraud), romance scams, lottery and prize scams, elder fraud, grandparent scams, telemarketing fraud, charity fraud, investment fraud targeting consumers, online marketplace fraud, impersonation fraud, cryptocurrency consumer fraud, FTC Act Section 5, state consumer protection laws, restitution remedies."},\n'
    '            {"id": "bankruptcy_fraud", "name": "Bankruptcy Fraud",\n'
    '             "context": "CFE Exam 2026 — Section 1 Domain S1D14: Bankruptcy Fraud. Topics: bankruptcy fraud statutes (18 USC 152-157), asset concealment in petitions, false statements and oaths, bust-out schemes, fraudulent transfers (actual and constructive), preferential transfers, badges of fraud, US Trustee Program, Rule 2004 examination, phantom creditor schemes, offshore account concealment, civil and criminal remedies."},\n'
    '            {"id": "tax_fraud", "name": "Tax Fraud",\n'
    '             "context": "CFE Exam 2026 — Section 1 Domain S1D15: Tax Fraud. Topics: tax avoidance vs evasion, IRC Section 7201 (willful evasion), payroll tax fraud (trust fund), offshore tax evasion (FBAR/FATCA), tax preparer fraud, refund fraud (SIRF), abusive tax shelters, investigative methods (net worth, bank deposit, expenditure), IRS Criminal Investigation (IRS-CI), civil fraud penalty (IRC 6663), voluntary disclosure programs."},\n'
    '            {"id": "government_fraud", "name": "Government & Public Sector Fraud",\n'
    '             "context": "CFE Exam 2026 — Section 1 Domain S1D17: Government and Public Sector Fraud. Topics: procurement fraud (pre-award and post-award), grant fraud, benefits fraud (welfare, unemployment, disability, SNAP), public official corruption, False Claims Act qui tam provisions, debarment procedures, Inspector General role, Single Audit Act, Davis-Bacon Act, Anti-Kickback Act, GAO standards."},\n'
    '            {"id": "emerging_fraud", "name": "Emerging Fraud & Technology",\n'
    '             "context": "CFE Exam 2026 — Section 1 Domain S1D20: Emerging Fraud Schemes and Technology. Topics: deepfake fraud (CEO fraud, voice cloning), AI-generated documents, synthetic identity fraud, cryptocurrency fraud (rug pulls, pump and dump, DeFi exploits), NFT wash trading, blockchain analytics, ESG fraud (greenwashing, carbon credits), remote work fraud, supply chain technology fraud, dark web facilitated fraud, algorithmic manipulation."}\n'
    '        ]\n'
    '    },'
)

# ─────────────────────────────────────────────────────────────
# CORRECAO 3: Atualiza versao e nome do CFE
# ─────────────────────────────────────────────────────────────
OLD_CFE_HEADER = (
    '"id": "cfe", "version": "CFE 2024", "last_updated": "2024-01", "name": "CFE / ACFE"'
)

NEW_CFE_HEADER = (
    '"id": "cfe", "version": "CFE 2026", "last_updated": "2026-06", "name": "CFE / ACFE"'
)

def main():
    print("=" * 70)
    print("  NEXOR -- ATUALIZADOR CATALOGO CFE v1")
    print(f"  {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("=" * 70)

    # Backup
    bak = f"{SERVER_FILE}.bak_{TIMESTAMP}"
    shutil.copy2(SERVER_FILE, bak)
    print(f"\n  Backup: {bak}")

    # Le arquivo
    with open(SERVER_FILE, encoding="utf-8") as f:
        content = f.read()

    errors = []

    # Correcao 1: versao CFE
    if OLD_CFE_HEADER in content:
        content = content.replace(OLD_CFE_HEADER, NEW_CFE_HEADER)
        print("  OK — versao CFE atualizada para 2026")
    else:
        errors.append("AVISO — header CFE nao encontrado (pode ja estar atualizado)")

    # Correcao 2: contexto law_cfe
    if OLD_LAW_CONTEXT in content:
        content = content.replace(OLD_LAW_CONTEXT, NEW_LAW_CONTEXT)
        print("  OK — contexto law_cfe atualizado (Brasil/LGPD removidos)")
    else:
        errors.append("AVISO — contexto law_cfe nao encontrado exatamente")
        # Tenta remover apenas as referencias brasileiras
        content = content.replace(", Brazil Lei 12.846/2013, LGPD", "")
        content = content.replace(", Brazil Lei 12.846/2013", "")
        content = content.replace(", LGPD", "")
        print("  OK — referencias Brasil/LGPD removidas por substituicao parcial")

    # Correcao 3: adiciona novos dominios
    if OLD_PREVENTION in content:
        content = content.replace(OLD_PREVENTION, NEW_PREVENTION_PLUS_DOMAINS)
        print("  OK — 7 novos dominios CFE 2026 adicionados ao catalogo")
    else:
        errors.append("ERRO — trecho prevention_deterrence nao encontrado")
        print("  ERRO — nao foi possivel adicionar novos dominios")
        print("  Verifique manualmente o server.py")

    # Salva
    if "ERRO" not in str(errors):
        with open(SERVER_FILE, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"\n  Arquivo salvo: {SERVER_FILE}")
    else:
        print(f"\n  ARQUIVO NAO SALVO devido a erros criticos")

    if errors:
        print("\n  AVISOS:")
        for e in errors:
            print(f"    · {e}")

    print("\n" + "=" * 70)
    print("  CONCLUIDO")
    print("  PROXIMO PASSO:")
    print("  Reiniciar o servidor para aplicar as alteracoes")
    print("  (feche e reabra o servidor ou use Ctrl+C e reinicie)")
    print("=" * 70)

if __name__ == "__main__":
    main()
