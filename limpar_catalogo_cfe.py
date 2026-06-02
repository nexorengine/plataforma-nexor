"""
NEXOR -- LIMPEZA CATALOGO CFE v1
Remove os dominios legacy do catalogo CFE no server.py:
  - financial_transactions (S1 Legacy)
  - fraud_investigation    (S2 Legacy)

Mantém os arquivos físicos no disco (backup).
Apenas remove do catálogo para não aparecer no dashboard.

USO:
    python limpar_catalogo_cfe.py
"""

import shutil
from datetime import datetime

SERVER_FILE = "server.py"
TIMESTAMP   = datetime.now().strftime("%Y%m%d_%H%M")

# Bloco financial_transactions a remover
OLD_FT = '''            {"id": "financial_transactions", "name": "S1 · Financial Transactions & Fraud Schemes",
             "context": "CFE Exam 2026 Section 1 — Financial Transactions and Fraud Schemes. Topics: accounting concepts, financial statement fraud (revenue recognition, channel stuffing, round-tripping), asset misappropriation (cash receipts, fraudulent disbursements, inventory), corruption and bribery, money laundering, securities fraud, payment fraud. Benford Law, Beneish M-Score, data analytics for detection."},
'''

# Bloco fraud_investigation a remover
OLD_FI = '''            {"id": "fraud_investigation", "name": "S2 · Fraud Investigation (Legacy)",
             "context": "CFE Fraud Examiners Manual 2026 Section 2 — Fraud Investigations and Legal Issues. Topics: investigation planning, evidence collection, digital forensics, interviewing techniques, report writing, legal considerations, expert testimony, data analysis. Legacy domain covering full Section 2 content."},
'''

def main():
    print("=" * 70)
    print("  NEXOR -- LIMPEZA CATALOGO CFE v1")
    print(f"  {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("=" * 70)

    # Backup
    bak = f"{SERVER_FILE}.bak_{TIMESTAMP}"
    shutil.copy2(SERVER_FILE, bak)
    print(f"\n  Backup: {bak}")

    with open(SERVER_FILE, encoding="utf-8") as f:
        content = f.read()

    removed = 0

    if OLD_FT in content:
        content = content.replace(OLD_FT, "")
        print("  OK — financial_transactions removido do catalogo")
        removed += 1
    else:
        print("  AVISO — financial_transactions nao encontrado exatamente")

    if OLD_FI in content:
        content = content.replace(OLD_FI, "")
        print("  OK — fraud_investigation removido do catalogo")
        removed += 1
    else:
        print("  AVISO — fraud_investigation nao encontrado exatamente")

    if removed > 0:
        with open(SERVER_FILE, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"\n  {removed} dominios legacy removidos do catalogo")
        print("  Arquivos fisicos preservados no disco")
    else:
        print("\n  NENHUMA alteracao realizada")

    print("\n" + "=" * 70)
    print("  CONCLUIDO")
    print("  PROXIMO PASSO:")
    print("  taskkill /f /im python.exe")
    print("  uvicorn server:app --port 8765 --reload")
    print("=" * 70)

if __name__ == "__main__":
    main()
