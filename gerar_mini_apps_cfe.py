"""
NEXOR -- GERADOR AUTOMATICO 44 MINI-APPS CFE v1
Gera index.html para cada dominio CFE com:
  · Quiz 1 trilíngue (EN/PT/ES)
  · Flashcards trilíngues
  · Badge embutido (base64)
  · Template v5 aprovado

Pula corruption_bribery (S1D06) — ja existe como s1d06_v5.html

USO:
    python gerar_mini_apps_cfe.py

OUTPUT:
    mini_apps/cfe/{domain_key}/index.html
    (44 arquivos)
"""

import json, base64, os, re
from pathlib import Path
from datetime import datetime

# ═══ CONFIGURACAO ═══════════════════════════════════════════
QUIZZES_DIR   = r"static\quizzes\cfe"
FLASHCARD_DIR = r"static\flashcards\cfe"
BADGES_DIR    = r"static\badges\cfe"
OUTPUT_DIR    = r"mini_apps\cfe"

# ═══ MAPA DE DOMINIOS ════════════════════════════════════════
DOMAINS = [
    {"id":"s1d01","key":"accounting_concepts","code":"S1D01","name":"Accounting Concepts & Financial Analysis","section":1,"badge_name":"Financial Analysis Specialist"},
    {"id":"s1d02","key":"financial_statement_fraud","code":"S1D02","name":"Financial Statement Fraud","section":1,"badge_name":"Financial Statement Fraud Specialist"},
    {"id":"s1d03","key":"cash_receipts_fraud","code":"S1D03","name":"Asset Misappropriation — Cash Receipts","section":1,"badge_name":"Cash Receipts Fraud Specialist"},
    {"id":"s1d04","key":"fraudulent_disbursements","code":"S1D04","name":"Asset Misappropriation — Disbursements","section":1,"badge_name":"Disbursements Fraud Specialist"},
    {"id":"s1d05","key":"inventory_fraud","code":"S1D05","name":"Asset Misappropriation — Inventory & Assets","section":1,"badge_name":"Inventory Fraud Specialist"},
    # S1D06 pulado — ja existe
    {"id":"s1d07","key":"data_theft_ip","code":"S1D07","name":"Theft of Data & Intellectual Property","section":1,"badge_name":"Data Protection Specialist"},
    {"id":"s1d08","key":"identity_theft_cyberfraud","code":"S1D08","name":"Identity Theft & Cyberfraud","section":1,"badge_name":"Cyber Fraud Specialist"},
    {"id":"s1d09","key":"financial_institution_fraud","code":"S1D09","name":"Financial Institution Fraud & Money Laundering","section":1,"badge_name":"Financial Crimes Specialist"},
    {"id":"s1d10","key":"securities_fraud","code":"S1D10","name":"Securities & Investment Fraud","section":1,"badge_name":"Securities Fraud Specialist"},
    {"id":"s1d11","key":"payment_fraud","code":"S1D11","name":"Payment Fraud","section":1,"badge_name":"Payment Fraud Specialist"},
    {"id":"s1d12","key":"insurance_fraud","code":"S1D12","name":"Insurance Fraud","section":1,"badge_name":"Insurance Fraud Specialist"},
    {"id":"s1d13","key":"consumer_fraud","code":"S1D13","name":"Consumer Fraud & Scams","section":1,"badge_name":"Consumer Protection Specialist"},
    {"id":"s1d14","key":"bankruptcy_fraud","code":"S1D14","name":"Bankruptcy Fraud","section":1,"badge_name":"Bankruptcy Fraud Specialist"},
    {"id":"s1d15","key":"tax_fraud","code":"S1D15","name":"Tax Fraud","section":1,"badge_name":"Tax Fraud Specialist"},
    {"id":"s1d16","key":"healthcare_fraud","code":"S1D16","name":"Health Care Fraud","section":1,"badge_name":"Healthcare Fraud Specialist"},
    {"id":"s1d17","key":"government_fraud","code":"S1D17","name":"Government & Public Sector Fraud","section":1,"badge_name":"Government Fraud Specialist"},
    {"id":"s1d18","key":"procurement_contract_fraud","code":"S1D18","name":"Procurement & Contract Fraud","section":1,"badge_name":"Procurement Fraud Specialist"},
    {"id":"s1d19","key":"international_fraud","code":"S1D19","name":"International & Cross-Border Fraud","section":1,"badge_name":"International Fraud Specialist"},
    {"id":"s1d20","key":"emerging_fraud","code":"S1D20","name":"Emerging Fraud & Technology","section":1,"badge_name":"Emerging Threats Specialist"},
    {"id":"s2d01","key":"investigation_planning","code":"S2D01","name":"Planning & Conducting Fraud Examination","section":2,"badge_name":"Investigation Planning Specialist"},
    {"id":"s2d02","key":"legal_issues_investigations","code":"S2D02","name":"Legal Issues in Investigations","section":2,"badge_name":"Legal Issues Specialist"},
    {"id":"s2d03","key":"law_cfe","code":"S2D03","name":"Law Related to Fraud","section":2,"badge_name":"Fraud Law Specialist"},
    {"id":"s2d04","key":"legal_system_overview","code":"S2D04","name":"Overview of the Legal System","section":2,"badge_name":"Legal System Specialist"},
    {"id":"s2d05","key":"criminal_prosecutions","code":"S2D05","name":"Criminal Prosecutions","section":2,"badge_name":"Criminal Prosecution Specialist"},
    {"id":"s2d06","key":"non_criminal_actions","code":"S2D06","name":"Non-Criminal Actions","section":2,"badge_name":"Civil Actions Specialist"},
    {"id":"s2d07","key":"individual_rights","code":"S2D07","name":"Individual Rights During Examinations","section":2,"badge_name":"Individual Rights Specialist"},
    {"id":"s2d08","key":"evidence_principles","code":"S2D08","name":"Basic Principles of Evidence","section":2,"badge_name":"Evidence Principles Specialist"},
    {"id":"s2d09","key":"collecting_evidence","code":"S2D09","name":"Collecting Evidence","section":2,"badge_name":"Evidence Collection Specialist"},
    {"id":"s2d10","key":"sources_information","code":"S2D10","name":"Sources of Information","section":2,"badge_name":"Information Sources Specialist"},
    {"id":"s2d11","key":"data_analysis_tools","code":"S2D11","name":"Data Analysis & Reporting Tools","section":2,"badge_name":"Data Analysis Specialist"},
    {"id":"s2d12","key":"tracing_assets","code":"S2D12","name":"Tracing Illicit Transactions & Assets","section":2,"badge_name":"Asset Tracing Specialist"},
    {"id":"s2d13","key":"interview_techniques","code":"S2D13","name":"Interview Theory & Application","section":2,"badge_name":"Interview Techniques Specialist"},
    {"id":"s2d14","key":"covert_operations","code":"S2D14","name":"Covert Operations","section":2,"badge_name":"Covert Operations Specialist"},
    {"id":"s2d15","key":"report_writing","code":"S2D15","name":"Report Writing","section":2,"badge_name":"Report Writing Specialist"},
    {"id":"s2d16","key":"expert_witness","code":"S2D16","name":"Testifying as Expert Witness","section":2,"badge_name":"Expert Witness Specialist"},
    {"id":"s3d01","key":"criminal_behavior","code":"S3D01","name":"Understanding Criminal Behavior","section":3,"badge_name":"Criminal Behavior Specialist"},
    {"id":"s3d02","key":"occupational_fraud","code":"S3D02","name":"Occupational Fraud","section":3,"badge_name":"Occupational Fraud Specialist"},
    {"id":"s3d03","key":"corporate_governance","code":"S3D03","name":"Corporate Governance","section":3,"badge_name":"Corporate Governance Specialist"},
    {"id":"s3d04","key":"auditor_responsibilities","code":"S3D04","name":"Management & Auditors Responsibilities","section":3,"badge_name":"Auditor Responsibilities Specialist"},
    {"id":"s3d05","key":"fraud_risk_assessment","code":"S3D05","name":"Fraud Risk Assessment","section":3,"badge_name":"Risk Assessment Specialist"},
    {"id":"s3d06","key":"prevention_deterrence","code":"S3D06","name":"Internal Controls & Anti-Fraud Programs","section":3,"badge_name":"Internal Controls Specialist"},
    {"id":"s3d07","key":"fraud_prevention_programs","code":"S3D07","name":"Fraud Prevention Programs","section":3,"badge_name":"Prevention Programs Specialist"},
    {"id":"s3d08","key":"fraud_risk_management","code":"S3D08","name":"Fraud Risk Management","section":3,"badge_name":"Risk Management Specialist"},
    {"id":"s3d09","key":"ethics_fraud_examiners","code":"S3D09","name":"Ethics for Fraud Examiners","section":3,"badge_name":"Ethics Specialist"},
]

# ═══ HELPERS ══════════════════════════════════════════════════
def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)

def load_badge_b64(domain_id):
    # Tenta carregar badge do diretorio de badges
    badge_file = Path(BADGES_DIR) / f"CFE_{domain_id.upper()}.png"
    # Normaliza nome do arquivo (S1D01, S2D01, S3D01...)
    # Tenta varios formatos de nome
    candidates = [
        Path(BADGES_DIR) / f"CFE_{domain_id.upper()}.png",
        Path(BADGES_DIR) / f"CFE_SID{domain_id[-2:]}.png",  # S1D01 -> SID01
        Path(BADGES_DIR) / f"CFE_{domain_id[:2].upper()}D{domain_id[-2:]}.png",  # S1D01 -> S1D01
    ]
    for c in candidates:
        if c.exists():
            return base64.b64encode(c.read_bytes()).decode()
    return None

def merge_fc(fc_en, fc_pt, fc_es):
    """Mescla flashcards dos 3 idiomas"""
    merged = []
    cards_en = fc_en.get("cards", [])
    cards_pt = fc_pt.get("cards", [])
    cards_es = fc_es.get("cards", [])
    for i, card in enumerate(cards_en):
        c_pt = cards_pt[i] if i < len(cards_pt) else card
        c_es = cards_es[i] if i < len(cards_es) else card
        merged.append({
            "id": card["id"],
            "topic": card["topic"],
            "front": {
                "en": card["front"].get("en", ""),
                "pt": c_pt["front"].get("pt", ""),
                "es": c_es["front"].get("es", "")
            },
            "back": {
                "en": card["back"].get("en", ""),
                "pt": c_pt["back"].get("pt", ""),
                "es": c_es["back"].get("es", "")
            }
        })
    return merged

def generate_mini_app(domain, q1en, q1pt, q1es, fc_merged, badge_b64):
    """Gera o HTML completo do mini-app para um dominio"""

    # Serializa dados como base64 para evitar conflito de aspas
    q1_b64 = {
        "en": base64.b64encode(json.dumps(q1en, ensure_ascii=False).encode()).decode(),
        "pt": base64.b64encode(json.dumps(q1pt, ensure_ascii=False).encode()).decode(),
        "es": base64.b64encode(json.dumps(q1es, ensure_ascii=False).encode()).decode(),
    }
    fc_b64 = base64.b64encode(json.dumps(fc_merged, ensure_ascii=False).encode()).decode()

    dom_id   = domain["id"]       # s1d06
    dom_code = domain["code"]     # S1D06
    dom_name = domain["name"]     # Corruption, Bribery...
    dom_sec  = domain["section"]  # 1
    bdg_name = domain["badge_name"]

    sec_label_pt = f"Seção {dom_sec}"
    sec_label_en = f"Section {dom_sec}"
    sec_label_es = f"Sección {dom_sec}"

    lk_key = f"nx_cfe_{dom_id}"

    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0">
<title>NEXOR · {dom_code} · {dom_name}</title>
<style>
*{{box-sizing:border-box;margin:0;padding:0;-webkit-tap-highlight-color:rgba(217,119,6,0.15)}}
:root{{
  --bg:#FAFAFA;--bg2:#EFEFEF;--tx:#0D0D0D;--tx2:#555;--tx3:#888;
  --bd:rgba(0,0,0,0.12);--bd2:rgba(0,0,0,0.22);--card:#FFFFFF;
  --amber:#D97706;--amberBg:#FEF3C7;--amberTx:#92400E;
  --green:#16A34A;--greenBg:#F0FDF4;
  --red:#DC2626;--redBg:#FEF2F2;
  --blue:#2563EB;
  --font:-apple-system,BlinkMacSystemFont,'Segoe UI',system-ui,sans-serif;
}}
.dark{{
  --bg:#0D0D0D;--bg2:#1A1A1A;--tx:#F0F0F0;--tx2:#888;--tx3:#555;
  --bd:rgba(255,255,255,0.09);--bd2:rgba(255,255,255,0.16);--card:#161616;
  --amber:#F59E0B;--amberBg:#1C1400;--amberTx:#FCD34D;
  --green:#22C55E;--greenBg:#052e16;
  --red:#EF4444;--redBg:#1c0505;
  --blue:#3B82F6;
}}
body{{font-family:var(--font);background:var(--bg);color:var(--tx);min-height:100vh;-webkit-text-size-adjust:100%}}
.topbar{{padding:12px 16px;display:flex;align-items:center;justify-content:space-between;position:-webkit-sticky;position:sticky;top:0;background:#92400E;z-index:100}}
.topbar-left{{display:flex;align-items:center;gap:10px}}
.back-btn,.icon-btn,.lang-btn,.tab,.fc-btn,.btn-pri,.btn-sec,.na-btn,.sim-btn{{touch-action:manipulation;-webkit-appearance:none;font-family:var(--font);cursor:pointer}}
.back-btn{{width:30px;height:30px;border:1.5px solid rgba(255,255,255,0.3);border-radius:6px;background:rgba(255,255,255,0.15);color:#FFF;font-size:16px;font-weight:600;display:flex;align-items:center;justify-content:center}}
.logo{{font-size:15px;font-weight:600;letter-spacing:0.08em;color:#FFF}}
.logo-dot{{color:#FCD34D}}
.topbar-right{{display:flex;align-items:center;gap:5px}}
.lang-toggle{{display:flex;gap:3px}}
.lang-btn{{font-size:11px;font-weight:600;padding:5px 9px;border-radius:6px;background:rgba(255,255,255,0.15);color:#FFF;border:1.5px solid rgba(255,255,255,0.3)}}
.lang-btn.active{{background:#FFF;color:#92400E;border-color:#FFF}}
.divider-v{{width:0.5px;height:16px;background:rgba(255,255,255,0.3);margin:0 2px}}
.icon-btn{{width:30px;height:30px;border:1.5px solid rgba(255,255,255,0.3);border-radius:6px;background:rgba(255,255,255,0.15);color:#FFF;font-size:14px;display:flex;align-items:center;justify-content:center}}
.hero{{padding:20px 16px 16px;border-bottom:0.5px solid var(--bd)}}
.domain-code{{font-size:10px;font-weight:600;letter-spacing:0.12em;color:var(--tx3);margin-bottom:4px}}
.domain-title{{font-size:18px;font-weight:700;color:var(--tx);margin-bottom:2px;line-height:1.3}}
.domain-sub{{font-size:12px;color:var(--tx2);margin-bottom:14px}}
.progress-row{{display:flex;align-items:center;gap:8px;margin-bottom:4px}}
.progress-track{{flex:1;height:4px;border-radius:2px;background:var(--bd2);overflow:hidden}}
.progress-fill{{height:100%;border-radius:2px;background:var(--amber);transition:width .4s}}
.progress-lbl{{font-size:11px;color:var(--amber);font-weight:600;white-space:nowrap}}
.stats-row{{display:flex;gap:16px;margin-top:12px;flex-wrap:wrap}}
.stat{{display:flex;flex-direction:column;gap:1px}}
.stat-val{{font-size:16px;font-weight:600;color:var(--tx)}}
.stat-val.amber{{color:var(--amber)}}
.stat-lbl{{font-size:9px;color:var(--tx3);letter-spacing:0.07em}}
.tabs{{display:flex;border-bottom:0.5px solid var(--bd);padding:0 16px;overflow-x:auto;-webkit-overflow-scrolling:touch}}
.tab{{padding:12px 0;margin-right:20px;font-size:13px;font-weight:500;color:var(--tx3);border-bottom:2px solid transparent;white-space:nowrap;-webkit-user-select:none;user-select:none;background:transparent;border-left:none;border-right:none;border-top:none}}
.tab.active{{color:var(--tx);border-bottom-color:var(--amber)}}
.content{{padding:16px;max-width:680px;margin:0 auto}}
.section-lbl{{font-size:10px;font-weight:600;letter-spacing:0.1em;color:var(--tx3);margin-bottom:12px}}
.fc-nav{{display:flex;align-items:center;justify-content:space-between;margin-bottom:14px}}
.fc-counter{{font-size:13px;color:var(--tx2)}}
.fc-nav-btns{{display:flex;gap:6px}}
.nav-btn{{width:34px;height:34px;border:1px solid var(--bd);border-radius:6px;display:flex;align-items:center;justify-content:center;background:var(--bg2);color:var(--tx);font-size:20px;line-height:1;touch-action:manipulation;-webkit-appearance:none}}
.tts-btn{{background:transparent;border:none;font-size:14px;padding:4px 6px;color:var(--amber);opacity:.7;flex-shrink:0;touch-action:manipulation;min-width:28px;min-height:28px;display:flex;align-items:center;justify-content:center}}
.tts-btn.playing{{opacity:1;color:var(--red)}}
.fc-progress-bar{{height:3px;background:var(--bd2);border-radius:2px;overflow:hidden;margin-bottom:14px}}
.fc-progress-fill{{height:100%;background:var(--amber);border-radius:2px;transition:width .3s}}
.flashcard{{border:1.5px solid var(--amber);border-radius:10px;min-height:240px;cursor:pointer;margin-bottom:14px;touch-action:manipulation}}
.fc-face{{width:100%;min-height:240px;border-radius:8px;padding:20px;background:var(--card);display:flex;flex-direction:column;justify-content:space-between}}
.fc-face.hidden{{display:none}}
.fc-side-row{{display:flex;align-items:center;justify-content:space-between;margin-bottom:8px}}
.fc-side{{font-size:9px;font-weight:600;letter-spacing:0.1em;color:var(--tx3)}}
.fc-text{{font-size:15px;color:var(--tx);line-height:1.6;flex:1}}
.fc-hint{{font-size:11px;color:var(--tx3);text-align:center;margin-top:10px}}
.fc-actions{{display:flex;gap:8px;margin-top:14px}}
.fc-btn{{flex:1;padding:12px;border-radius:7px;font-size:13px;font-weight:600;border:1.5px solid var(--bd);background:var(--bg2);color:var(--tx);min-height:44px}}
.fc-btn.know{{background:var(--amber);color:#fff;border-color:var(--amber)}}
.q-header{{display:flex;align-items:center;justify-content:space-between;margin-bottom:14px;flex-wrap:wrap;gap:8px}}
.q-meta{{display:flex;align-items:center;gap:8px;flex-wrap:wrap}}
.q-num{{font-size:13px;color:var(--tx2)}}
.q-attempt{{font-size:10px;font-weight:600;padding:3px 8px;border-radius:5px;background:var(--amberBg);color:var(--amberTx)}}
.q-timer{{font-size:12px;font-weight:700;color:var(--amber);background:var(--amberBg);padding:3px 9px;border-radius:5px;font-variant-numeric:tabular-nums}}
.q-diff-easy{{font-size:10px;font-weight:600;padding:3px 9px;border-radius:5px;background:#f0fdf4;color:#16a34a}}
.q-diff-standard{{font-size:10px;font-weight:600;padding:3px 9px;border-radius:5px;background:var(--amberBg);color:var(--amberTx)}}
.q-diff-hard{{font-size:10px;font-weight:600;padding:3px 9px;border-radius:5px;background:#fef2f2;color:#dc2626}}
.dark .q-diff-easy{{background:#052e16;color:#22c55e}}
.dark .q-diff-hard{{background:#1c0505;color:#ef4444}}
.q-prog-track{{height:2px;background:var(--bd);border-radius:1px;overflow:hidden;margin-bottom:18px}}
.q-prog-fill{{height:100%;background:var(--amber);transition:width .3s}}
.q-text-row{{display:flex;align-items:flex-start;gap:8px;margin-bottom:16px}}
.q-text{{font-size:14px;line-height:1.7;color:var(--tx);flex:1}}
.options{{display:flex;flex-direction:column;gap:7px;margin-bottom:16px}}
.option{{padding:13px 14px;border:0.5px solid var(--bd);border-radius:8px;display:flex;align-items:center;gap:8px;font-size:13px;line-height:1.5;background:var(--card);color:var(--tx);touch-action:manipulation;min-height:44px;-webkit-user-select:none;user-select:none;cursor:pointer}}
.opt-left{{display:flex;align-items:center;gap:8px;flex:1}}
.opt-letter{{width:22px;height:22px;min-width:22px;border:none;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:10px;font-weight:700;color:var(--amberTx);flex-shrink:0;background:var(--amberBg)}}
.opt-tts{{background:transparent;border:none;font-size:12px;padding:4px;color:var(--amber);opacity:.5;flex-shrink:0;min-width:28px;min-height:28px;touch-action:manipulation}}
.option.selected{{border-color:var(--amber)}}
.option.selected .opt-letter{{background:var(--amber);color:#fff}}
.option.correct{{border:1.5px solid var(--green);background:var(--greenBg)}}
.option.correct .opt-letter{{background:var(--green);color:#fff}}
.option.wrong{{border:1.5px solid var(--red);background:var(--redBg)}}
.option.wrong .opt-letter{{background:var(--red);color:#fff}}
.option.reveal{{border:1.5px solid var(--green);background:var(--greenBg)}}
.option.reveal .opt-letter{{background:var(--green);color:#fff}}
.option.disabled{{cursor:default;pointer-events:none}}
.feedback{{padding:12px 14px;border-radius:8px;margin-bottom:12px;display:none}}
.feedback.show{{display:block}}
.feedback.ok{{background:var(--greenBg);border:1px solid var(--green);color:var(--green)}}
.feedback.err{{background:var(--redBg);border:1px solid var(--red);color:var(--red)}}
.fb-row{{display:flex;align-items:center;justify-content:space-between;gap:8px}}
.fb-hdr{{font-weight:700;font-size:14px}}
.just-box{{padding:12px 14px;border-radius:8px;background:var(--bg2);border:0.5px solid var(--bd);margin-bottom:14px;display:none}}
.just-box.show{{display:block}}
.just-row{{display:flex;align-items:center;justify-content:space-between;margin-bottom:5px}}
.just-label{{font-size:10px;font-weight:700;letter-spacing:0.08em;color:var(--tx3)}}
.just-text{{font-size:12px;line-height:1.6;color:var(--tx2)}}
.btn-row{{display:flex;gap:8px;justify-content:flex-end;margin-top:4px}}
.btn-pri{{padding:12px 20px;background:var(--amber);color:#fff;border:none;border-radius:7px;font-size:13px;font-weight:600;min-height:44px}}
.btn-sec{{padding:12px 20px;background:var(--bg2);color:var(--tx);border:1px solid var(--bd);border-radius:7px;font-size:13px;font-weight:500;min-height:44px}}
.quiz2-locked{{padding:32px 16px;text-align:center}}
.quiz2-lock-icon{{font-size:36px;margin-bottom:10px}}
.quiz2-lock-msg{{font-size:13px;line-height:1.6;color:var(--tx2)}}
.quiz2-lock-prog{{font-size:12px;color:var(--amber);margin-top:8px;font-weight:600}}
.sc-top{{text-align:center;padding:24px 16px;border-bottom:0.5px solid var(--bd)}}
.sc-pct{{font-size:52px;font-weight:700;color:var(--amber)}}
.sc-level{{font-size:13px;color:var(--tx2);margin-top:6px}}
.sc-time{{font-size:12px;color:var(--tx3);margin-top:4px}}
.sc-bars{{padding:16px;border-bottom:0.5px solid var(--bd)}}
.sc-bar-row{{display:flex;align-items:center;gap:10px;margin-bottom:12px}}
.sc-bar-lbl{{font-size:12px;color:var(--tx2);width:58px;flex-shrink:0}}
.sc-bar-track{{flex:1;height:4px;background:var(--bd2);border-radius:2px;overflow:hidden}}
.sc-bar-fill{{height:100%;background:var(--amber);border-radius:2px;transition:width .6s}}
.sc-bar-pct{{font-size:12px;font-weight:600;color:var(--tx);width:32px;text-align:right}}
.sc-act{{padding:16px;display:flex;gap:8px;border-bottom:0.5px solid var(--bd)}}
.sc-hist{{padding:16px}}
.sc-hist-lbl{{font-size:10px;font-weight:600;letter-spacing:0.1em;color:var(--tx3);margin-bottom:10px}}
.sc-hist-row{{display:flex;align-items:center;justify-content:space-between;padding:8px 0;border-bottom:0.5px solid var(--bd);font-size:13px}}
.sc-hist-row:last-child{{border-bottom:none}}
.sc-hist-date{{color:var(--tx2);font-size:12px}}
.sc-hist-score{{font-weight:600;color:var(--tx)}}
.sc-best{{font-size:10px;padding:2px 7px;border-radius:4px;background:var(--amberBg);color:var(--amberTx);font-weight:600}}
.badge-wrap{{padding:16px;border-top:0.5px solid var(--bd)}}
.badge-card{{border:0.5px solid #333;border-radius:10px;padding:14px;display:flex;align-items:center;gap:14px;background:#0D0D0D;transition:all .3s}}
.badge-card.earned{{border-color:var(--amber)}}
.badge-img-wrap{{width:48px;height:48px;flex-shrink:0;display:flex;align-items:center;justify-content:center;background:#0D0D0D}}
.badge-img{{width:44px;height:44px;object-fit:contain;filter:none;transition:filter .5s}}
.badge-img.earned{{filter:none}}
.badge-name{{font-size:13px;font-weight:600;color:#FFFFFF;margin-bottom:2px}}
.badge-desc{{font-size:12px;color:rgba(255,255,255,0.6)}}
.badge-tag{{font-size:10px;font-weight:600;padding:3px 9px;border-radius:5px;white-space:nowrap;background:#1A1A1A;color:rgba(255,255,255,0.5);border:0.5px solid #444}}
.badge-tag.earned{{background:var(--amber);color:#fff;border-color:var(--amber)}}
@keyframes badgeEarned{{0%{{transform:scale(0.3) rotate(-15deg);opacity:0}}60%{{transform:scale(1.15) rotate(3deg)}}100%{{transform:scale(1) rotate(0);opacity:1}}}}
.badge-anim{{animation:badgeEarned .7s ease-out}}
@media(max-width:480px){{.domain-title{{font-size:16px}}.q-text{{font-size:13px}}.option{{padding:11px 12px}}.fc-text{{font-size:14px}}.sc-pct{{font-size:44px}}.stats-row{{gap:12px}}}}
</style>
</head>
<body>
<div id="app">

<div class="topbar">
  <div class="topbar-left">
    <button class="back-btn" id="btn-back">&#8592;</button>
    <div class="logo">NEXOR<span class="logo-dot">_</span></div>
  </div>
  <div class="topbar-right">
    <div class="lang-toggle">
      <button class="lang-btn active" id="btn-pt">PT</button>
      <button class="lang-btn" id="btn-en">EN</button>
      <button class="lang-btn" id="btn-es">ES</button>
    </div>
    <div class="divider-v"></div>
    <button class="icon-btn" id="btn-theme">&#127769;</button>
  </div>
</div>

<div class="hero">
  <div class="domain-code" id="dc">{dom_code} · CFE 2026</div>
  <div class="domain-title">{dom_name}</div>
  <div class="domain-sub" id="dsub"></div>
  <div class="progress-row">
    <div class="progress-track"><div class="progress-fill" id="hprog" style="width:0%"></div></div>
    <div class="progress-lbl" id="hpct">0%</div>
  </div>
  <div class="stats-row">
    <div class="stat"><div class="stat-val amber" id="stscore">&#8212;</div><div class="stat-lbl" id="lscore">SCORE</div></div>
    <div class="stat"><div class="stat-val" id="stattempts">0</div><div class="stat-lbl" id="lattempts">ATTEMPTS</div></div>
    <div class="stat"><div class="stat-val" id="stflash">0/50</div><div class="stat-lbl" id="lflash">FLASHCARDS</div></div>
    <div class="stat"><div class="stat-val amber" id="stlevel">&#9733;&#9734;&#9734;</div><div class="stat-lbl" id="llevel">LEVEL</div></div>
  </div>
</div>

<div class="tabs">
  <button class="tab active" id="tbn-flash">Flashcards</button>
  <button class="tab" id="tbn-quiz1">Quiz 1</button>
  <button class="tab" id="tbn-quiz2">Quiz 2 <span id="q2lock">&#128274;</span></button>
  <button class="tab" id="tbn-score">Scorecard</button>
</div>

<!-- FLASHCARDS -->
<div id="tab-flash">
<div class="content">
  <div class="section-lbl" id="fcsec">FLASHCARDS</div>
  <div class="fc-progress-bar"><div class="fc-progress-fill" id="fcprog" style="width:0%"></div></div>
  <div class="fc-nav">
    <div class="fc-counter" id="fcctr">Card 1 / 50</div>
    <div class="fc-nav-btns">
      <button class="nav-btn" id="btn-fcprev">&#8249;</button>
      <button class="nav-btn" id="btn-fcnext">&#8250;</button>
    </div>
  </div>
  <div class="flashcard" id="flashcard">
    <div class="fc-face" id="fcf">
      <div class="fc-side-row">
        <div class="fc-side" id="fcfront-lbl">FRONT</div>
        <button class="tts-btn" id="tts-fcf">&#128266;</button>
      </div>
      <div class="fc-text" id="fcfront-txt"></div>
      <div class="fc-hint" id="fchint">Tap to reveal</div>
    </div>
    <div class="fc-face hidden" id="fcb">
      <div class="fc-side-row">
        <div class="fc-side" id="fcback-lbl">BACK</div>
        <button class="tts-btn" id="tts-fcb">&#128266;</button>
      </div>
      <div class="fc-text" id="fcback-txt"></div>
      <div class="fc-actions">
        <button class="fc-btn" id="btn-no">Don't know</button>
        <button class="fc-btn know" id="btn-yes">Know it</button>
      </div>
    </div>
  </div>
</div>
</div>

<!-- QUIZ 1 -->
<div id="tab-quiz1" style="display:none">
<div class="content">
  <div class="q-header">
    <div class="q-meta">
      <span class="q-num" id="q1num">Q 1/50</span>
      <span class="q-attempt" id="q1att">ATT 1</span>
      <span class="q-timer" id="q1tmr">00:00</span>
    </div>
    <div id="q1diff"></div>
  </div>
  <div class="q-prog-track"><div class="q-prog-fill" id="q1prog" style="width:2%"></div></div>
  <div class="q-text-row">
    <div class="q-text" id="q1txt"></div>
    <button class="tts-btn" id="tts-q1">&#128266;</button>
  </div>
  <div class="options" id="q1opts"></div>
  <div class="feedback" id="q1fb">
    <div class="fb-row"><span class="fb-hdr" id="q1fbhdr"></span><button class="tts-btn" id="tts-q1fb">&#128266;</button></div>
  </div>
  <div class="just-box" id="q1jbox">
    <div class="just-row"><div class="just-label" id="q1jlok">&#10003; JUSTIFICATION</div><button class="tts-btn" id="tts-q1jok">&#128266;</button></div>
    <div class="just-text" id="q1jok"></div>
    <br>
    <div class="just-row"><div class="just-label" id="q1jlwrong">&#10007; DISTRACTORS</div><button class="tts-btn" id="tts-q1jwrong">&#128266;</button></div>
    <div class="just-text" id="q1jwrong"></div>
  </div>
  <div class="btn-row">
    <button class="btn-sec" id="q1prev" style="display:none">Prev</button>
    <button class="btn-pri" id="q1cfm">Confirm</button>
    <button class="btn-pri" id="q1nxt" style="display:none">Next</button>
  </div>
</div>
</div>

<!-- QUIZ 2 -->
<div id="tab-quiz2" style="display:none">
<div class="content">
  <div id="q2locked" class="quiz2-locked">
    <div class="quiz2-lock-icon">&#128274;</div>
    <div class="quiz2-lock-msg" id="q2lockmsg"></div>
    <div class="quiz2-lock-prog" id="q2lockprog"></div>
  </div>
  <div id="q2active" style="display:none">
    <div class="q-header">
      <div class="q-meta">
        <span class="q-num" id="q2num">Q 1/50</span>
        <span class="q-attempt" id="q2att">ATT 1</span>
        <span class="q-timer" id="q2tmr">00:00</span>
      </div>
      <div id="q2diff"></div>
    </div>
    <div class="q-prog-track"><div class="q-prog-fill" id="q2prog" style="width:2%"></div></div>
    <div class="q-text-row">
      <div class="q-text" id="q2txt"></div>
      <button class="tts-btn" id="tts-q2">&#128266;</button>
    </div>
    <div class="options" id="q2opts"></div>
    <div class="feedback" id="q2fb">
      <div class="fb-row"><span class="fb-hdr" id="q2fbhdr"></span><button class="tts-btn" id="tts-q2fb">&#128266;</button></div>
    </div>
    <div class="just-box" id="q2jbox">
      <div class="just-row"><div class="just-label" id="q2jlok">&#10003; JUSTIFICATION</div><button class="tts-btn" id="tts-q2jok">&#128266;</button></div>
      <div class="just-text" id="q2jok"></div>
      <br>
      <div class="just-row"><div class="just-label" id="q2jlwrong">&#10007; DISTRACTORS</div><button class="tts-btn" id="tts-q2jwrong">&#128266;</button></div>
      <div class="just-text" id="q2jwrong"></div>
    </div>
    <div class="btn-row">
      <button class="btn-sec" id="q2prev" style="display:none">Prev</button>
      <button class="btn-pri" id="q2cfm">Confirm</button>
      <button class="btn-pri" id="q2nxt" style="display:none">Next</button>
    </div>
  </div>
</div>
</div>

<!-- SCORECARD -->
<div id="tab-score" style="display:none">
  <div class="sc-top">
    <div class="sc-pct" id="scpct">&#8212;</div>
    <div class="sc-level" id="sclvl"></div>
    <div class="sc-time" id="sctime"></div>
  </div>
  <div class="sc-bars">
    <div class="section-lbl" id="scbdlbl">PERFORMANCE BY DIFFICULTY</div>
    <div class="sc-bar-row"><div class="sc-bar-lbl">Easy</div><div class="sc-bar-track"><div class="sc-bar-fill" id="sbeasy" style="width:0%"></div></div><div class="sc-bar-pct" id="speasy">0%</div></div>
    <div class="sc-bar-row"><div class="sc-bar-lbl">Standard</div><div class="sc-bar-track"><div class="sc-bar-fill" id="sbstd" style="width:0%"></div></div><div class="sc-bar-pct" id="spstd">0%</div></div>
    <div class="sc-bar-row"><div class="sc-bar-lbl">Hard</div><div class="sc-bar-track"><div class="sc-bar-fill" id="sbhard" style="width:0%"></div></div><div class="sc-bar-pct" id="sphard">0%</div></div>
  </div>
  <div class="sc-act">
    <button class="btn-sec" style="flex:1" id="btnretake">Try again</button>
    <button class="btn-pri" style="flex:1" id="btnscores">Scores</button>
  </div>
  <div class="sc-hist">
    <div class="sc-hist-lbl" id="schistlbl">ATTEMPT HISTORY</div>
    <div id="schistlist"></div>
  </div>
</div>

<!-- BADGE -->
<div class="badge-wrap">
  <div class="section-lbl" id="bdgtitlelbl">DOMAIN BADGE</div>
  <div class="badge-card" id="bdgcard">
    <div class="badge-img-wrap">
      <img class="badge-img" id="bdgimg" src="data:image/png;base64,{badge_b64}" alt="{dom_code}">
    </div>
    <div style="flex:1">
      <div class="badge-name" id="bdgname">{bdg_name}</div>
      <div class="badge-desc" id="bdgdesc"></div>
    </div>
    <div class="badge-tag" id="bdgtag">need 80%</div>
  </div>
</div>

</div>

<script>
var QS1 = {{
  en: JSON.parse(atob('{q1_b64["en"]}')),
  pt: JSON.parse(atob('{q1_b64["pt"]}')),
  es: JSON.parse(atob('{q1_b64["es"]}'))
}};
var QS2 = {{en:[],pt:[],es:[]}};
var FC  = JSON.parse(atob('{fc_b64}'));

var TX = {{
  pt:{{sub:'CFE 2026 · {dom_code} · 50 questões · 50 flashcards',
    lscore:'MELHOR SCORE',lattempts:'TENTATIVAS',lflash:'FLASHCARDS',llevel:'NÍVEL',
    fcsec:'FLASHCARDS · {{d}} / 50 DOMINADOS',fcfront:'FRENTE',fcback:'VERSO',fchint:'Toque para ver a resposta',
    bno:'Não sei',byes:'Sei',qnum:'Q {{n}}/50',att:'TENTATIVA {{n}}',
    bcfm:'Confirmar',bnxt:'Próxima',bprv:'Anterior',bfin:'Finalizar',
    bok:'✓ Correto!',berr:'✗ Incorreto — resposta correta: {{l}}',
    jok:'✓ JUSTIFICATIVA',jwrong:'✗ DISTRÁTORES',
    scbd:'DESEMPENHO POR DIFICULDADE',schist:'HISTÓRICO',
    bretake:'Tentar novamente',bscores:'Scores',
    bdgtitle:'BADGE DO DOMÍNIO',bdgname:'{bdg_name}',
    bdglocked:'Atinja 80% para conquistar',bdgearned:'Badge conquistado!',bdgearnedtag:'✓ Conquistado!',
    lvlt:'★☆☆ Candidate in Training',lvlp:'★★☆ Candidate in Progress',lvlr:'★★★ Exam Ready',
    nohist:'Nenhuma tentativa ainda',cin:'Concluído em',
    q2locked:'Complete o Quiz 1 com ≥ 70% para desbloquear',q2best:'Melhor Q1:',attsuffix:'· Tentativa {{n}}',finish:'Finalizar'}},
  en:{{sub:'CFE 2026 · {dom_code} · 50 questions · 50 flashcards',
    lscore:'BEST SCORE',lattempts:'ATTEMPTS',lflash:'FLASHCARDS',llevel:'LEVEL',
    fcsec:'FLASHCARDS · {{d}} / 50 MASTERED',fcfront:'FRONT',fcback:'BACK',fchint:'Tap to reveal answer',
    bno:"Don't know",byes:'Know it',qnum:'Q {{n}}/50',att:'ATTEMPT {{n}}',
    bcfm:'Confirm',bnxt:'Next',bprv:'Previous',bfin:'Finish',
    bok:'✓ Correct!',berr:'✗ Incorrect — correct answer: {{l}}',
    jok:'✓ JUSTIFICATION',jwrong:'✗ DISTRACTORS',
    scbd:'PERFORMANCE BY DIFFICULTY',schist:'ATTEMPT HISTORY',
    bretake:'Try again',bscores:'Scores',
    bdgtitle:'DOMAIN BADGE',bdgname:'{bdg_name}',
    bdglocked:'Score 80%+ to earn this badge',bdgearned:'Badge earned!',bdgearnedtag:'✓ Earned!',
    lvlt:'★☆☆ Candidate in Training',lvlp:'★★☆ Candidate in Progress',lvlr:'★★★ Exam Ready',
    nohist:'No attempts yet',cin:'Completed in',
    q2locked:'Complete Quiz 1 with ≥ 70% to unlock',q2best:'Best Q1:',attsuffix:'· Attempt {{n}}',finish:'Finish'}},
  es:{{sub:'CFE 2026 · {dom_code} · 50 preguntas · 50 flashcards',
    lscore:'MEJOR PUNTAJE',lattempts:'INTENTOS',lflash:'FLASHCARDS',llevel:'NIVEL',
    fcsec:'FLASHCARDS · {{d}} / 50 DOMINADOS',fcfront:'FRENTE',fcback:'REVERSO',fchint:'Toque para ver la respuesta',
    bno:'No sé',byes:'Lo sé',qnum:'P {{n}}/50',att:'INTENTO {{n}}',
    bcfm:'Confirmar',bnxt:'Siguiente',bprv:'Anterior',bfin:'Finalizar',
    bok:'✓ ¡Correcto!',berr:'✗ Incorrecto — respuesta correcta: {{l}}',
    jok:'✓ JUSTIFICACIÓN',jwrong:'✗ DISTRACTORES',
    scbd:'RENDIMIENTO POR DIFICULTAD',schist:'HISTORIAL',
    bretake:'Intentar de nuevo',bscores:'Scores',
    bdgtitle:'INSIGNIA DEL DOMINIO',bdgname:'{bdg_name}',
    bdglocked:'Alcanza 80%+ para obtener esta insignia',bdgearned:'¡Insignia obtenida!',bdgearnedtag:'✓ ¡Obtenida!',
    lvlt:'★☆☆ Candidato en Formación',lvlp:'★★☆ Candidato en Progreso',lvlr:'★★★ Listo para el Examen',
    nohist:'Ningún intento todavía',cin:'Completado en',
    q2locked:'Complete el Quiz 1 con ≥ 70% para desbloquear',q2best:'Mejor Q1:',attsuffix:'· Intento {{n}}',finish:'Finalizar'}}
}};

var lang=localStorage.getItem('nx_lang')||'pt';
var dark=localStorage.getItem('nx_dark')==='1';
var fcDone=JSON.parse(localStorage.getItem('{lk_key}_fcd')||'[]');
var h1=JSON.parse(localStorage.getItem('{lk_key}_h1')||'[]');
var h2=JSON.parse(localStorage.getItem('{lk_key}_h2')||'[]');
var fcQueue=[],fcIdx=0,fcShowing='front';
function mkQ(){{return {{qs:[],cur:0,ans:[],ok:0,bad:0,done:false,t0:null,sec:0,tint:null,att:0,bd:{{}}}};}}
var Q1=mkQ(),Q2=mkQ();

function tr(k,v){{var s=(TX[lang]||TX.en)[k]||k;if(v)Object.keys(v).forEach(function(x){{s=s.replace('{{'+x+'}}',v[x]);}});return s;}}
function g(id){{return document.getElementById(id);}}
function st(id,val){{var e=g(id);if(e)e.textContent=val;}}
function best(){{return h1.length?Math.max.apply(null,h1.map(function(h){{return h.s;}})):0;}}
function unlocked(){{return best()>=70;}}
function fmt(s){{return String(Math.floor(s/60)).padStart(2,'0')+':'+String(s%60).padStart(2,'0');}}
function shuf(a){{var b=a.slice();for(var i=b.length-1;i>0;i--){{var j=Math.floor(Math.random()*(i+1));var t=b[i];b[i]=b[j];b[j]=t;}}return b;}}
function shuffOpts(q){{var opts=q.options.slice(),ct=opts[q.correct];for(var i=opts.length-1;i>0;i--){{var j=Math.floor(Math.random()*(i+1));var t=opts[i];opts[i]=opts[j];opts[j]=t;}}return Object.assign({{}},q,{{options:opts,correct:opts.indexOf(ct)}});}}

var _ttsOn=false,_ttsBtn=null;
function ttsStop(){{if(window.speechSynthesis)window.speechSynthesis.cancel();_ttsOn=false;if(_ttsBtn){{_ttsBtn.innerHTML='&#128266;';_ttsBtn.classList.remove('playing');}}_ttsBtn=null;}}
function ttsTgl(elId,btnId){{var txt=g(elId)?g(elId).textContent:'';var btn=g(btnId);if(_ttsOn){{ttsStop();return;}}if(!window.speechSynthesis||!txt)return;try{{_ttsOn=true;_ttsBtn=btn;if(btn){{btn.innerHTML='&#9209;';btn.classList.add('playing');}}var u=new SpeechSynthesisUtterance(txt);u.lang=lang==='pt'?'pt-BR':lang==='es'?'es-419':'en-US';u.onend=u.onerror=function(){{ttsStop();}};window.speechSynthesis.speak(u);}}catch(e){{ttsStop();}}}}
function ttsTxt(txt,btn){{if(_ttsOn){{ttsStop();return;}}if(!window.speechSynthesis||!txt)return;try{{_ttsOn=true;_ttsBtn=btn||null;if(btn){{btn.innerHTML='&#9209;';btn.classList.add('playing');}}var u=new SpeechSynthesisUtterance(txt);u.lang=lang==='pt'?'pt-BR':lang==='es'?'es-419':'en-US';u.onend=u.onerror=function(){{ttsStop();}};window.speechSynthesis.speak(u);}}catch(e){{ttsStop();}}}}
function ttsQ(num,btn){{var q=num===1?Q1:Q2;if(!q.qs.length)return;var qo=q.qs[q.cur],L=['A','B','C','D'];ttsTxt(qo.text+'. '+qo.options.map(function(o,i){{return L[i]+'. '+o.replace(/^[A-Da-d]\\.\\s*/,'');}}).join('. '),btn);}}

function applyTheme(){{document.body.classList.toggle('dark',dark);g('btn-theme').innerHTML=dark?'&#9728;':'&#127769;';}}
function applyLangBtns(){{['pt','en','es'].forEach(function(l){{var b=g('btn-'+l);if(b)b.classList.toggle('active',l===lang);}});}}

function applyLang(){{
  st('dsub',tr('sub'));
  st('lscore',tr('lscore'));st('lattempts',tr('lattempts'));st('lflash',tr('lflash'));st('llevel',tr('llevel'));
  st('fcfront-lbl',tr('fcfront'));st('fcback-lbl',tr('fcback'));st('fchint',tr('fchint'));
  st('btn-no',tr('bno'));st('btn-yes',tr('byes'));
  st('q1cfm',tr('bcfm'));st('q1nxt',tr('bnxt'));st('q1prev',tr('bprv'));
  st('q2cfm',tr('bcfm'));st('q2nxt',tr('bnxt'));st('q2prev',tr('bprv'));
  st('q1jlok',tr('jok'));st('q1jlwrong',tr('jwrong'));
  st('q2jlok',tr('jok'));st('q2jlwrong',tr('jwrong'));
  st('scbdlbl',tr('scbd'));st('schistlbl',tr('schist'));
  st('btnretake',tr('bretake'));st('btnscores',tr('bscores'));
  st('bdgtitlelbl',tr('bdgtitle'));st('bdgname',tr('bdgname'));
  st('q2lockmsg',tr('q2locked'));
  var b=best();st('q2lockprog',b>0?tr('q2best')+' '+b+'%':'');
  updateFcSec();updateBadge();renderScore();
}}

function setLang(l){{
  ttsStop();lang=l;localStorage.setItem('nx_lang',l);applyLangBtns();
  clearInterval(Q1.tint);clearInterval(Q2.tint);
  Q1=mkQ();Q2=mkQ();fcIdx=0;fcShowing='front';
  applyLang();
  ['flash','quiz1','quiz2','score'].forEach(function(x){{g('tab-'+x).style.display='none';}});
  document.querySelectorAll('.tab').forEach(function(t){{t.classList.remove('active');}});
  g('tab-flash').style.display='block';g('tbn-flash').classList.add('active');
  renderFC();
}}

function showTab(name){{
  ttsStop();
  ['flash','quiz1','quiz2','score'].forEach(function(x){{g('tab-'+x).style.display='none';}});
  document.querySelectorAll('.tab').forEach(function(t){{t.classList.remove('active');}});
  g('tab-'+name).style.display='block';g('tbn-'+name).classList.add('active');
  if(name==='flash')renderFC();
  if(name==='quiz1'){{if(!Q1.qs.length)startQ(1);else renderQ(1);}}
  if(name==='quiz2'){{
    if(!unlocked()){{g('q2locked').style.display='block';g('q2active').style.display='none';}}
    else{{g('q2locked').style.display='none';g('q2active').style.display='block';if(!Q2.qs.length)startQ(2);else renderQ(2);}}
  }}
  if(name==='score')renderScore();
}}

function fcTxt(card,side){{var o=side==='front'?card.front:card.back;return(o&&(o[lang]||o.en))||'';}}
function updateFcSec(){{
  st('fcsec',tr('fcsec',{{d:fcDone.length}}));
  var p=g('fcprog');if(p)p.style.width=(fcDone.length/FC.length*100)+'%';
  st('stflash',fcDone.length+'/50');
}}
function buildQ(){{fcQueue=FC.map(function(c){{return c.id;}});}}
function renderFC(){{
  if(!fcQueue.length)buildQ();
  var idx=fcIdx%fcQueue.length;
  var card=FC.find(function(c){{return c.id===fcQueue[idx];}})||FC[0];
  st('fcfront-txt',fcTxt(card,'front'));st('fcback-txt',fcTxt(card,'back'));
  st('fcctr','Card '+(fcIdx+1)+' / '+fcQueue.length);
  g('fcf').classList.remove('hidden');g('fcb').classList.add('hidden');fcShowing='front';
  updateFcSec();
}}
function fcFlip(){{
  ttsStop();
  if(fcShowing==='front'){{g('fcf').classList.add('hidden');g('fcb').classList.remove('hidden');fcShowing='back';}}
  else{{g('fcb').classList.add('hidden');g('fcf').classList.remove('hidden');fcShowing='front';}}
}}
function fcAns(knows){{
  ttsStop();var id=fcQueue[fcIdx%fcQueue.length];
  if(knows){{if(fcDone.indexOf(id)<0){{fcDone.push(id);localStorage.setItem('{lk_key}_fcd',JSON.stringify(fcDone));}}
    fcQueue.splice(fcIdx%fcQueue.length,1);if(!fcQueue.length)buildQ();if(fcIdx>=fcQueue.length)fcIdx=0;}}
  else{{fcIdx=(fcIdx+1)%fcQueue.length;}}
  updateHero();renderFC();
}}

function startQ(n){{
  var q=n===1?Q1:Q2,h=n===1?h1:h2,src=n===1?(QS1[lang]||QS1.en):(QS2[lang]||QS2.en);
  if(!src||!src.length)return;
  clearInterval(q.tint);
  q.qs=shuf(src.slice()).map(shuffOpts);
  q.cur=0;q.ans=new Array(q.qs.length).fill(null);
  q.ok=0;q.bad=0;q.done=false;q.t0=Date.now();q.sec=0;q.att=h.length+1;
  q.bd={{EASY:{{t:0,o:0}},STANDARD:{{t:0,o:0}},HARD:{{t:0,o:0}}}};
  var tid=n===1?'q1tmr':'q2tmr';
  q.tint=setInterval(function(){{q.sec=Math.floor((Date.now()-q.t0)/1000);st(tid,fmt(q.sec));}},1000);
  renderQ(n);
}}

function renderQ(n){{
  ttsStop();var q=n===1?Q1:Q2,p=n===1?'q1':'q2';
  var qo=q.qs[q.cur],L=['A','B','C','D'];
  st(p+'num',tr('qnum',{{n:q.cur+1}}));st(p+'att',tr('att',{{n:q.att}}));
  var diff=(qo.difficulty||'STANDARD').toUpperCase();
  var cls=diff==='EASY'?'q-diff-easy':diff==='HARD'?'q-diff-hard':'q-diff-standard';
  g(p+'diff').innerHTML='<span class="'+cls+'">'+diff+'</span>';
  g(p+'prog').style.width=(q.cur/q.qs.length*100)+'%';
  st(p+'txt',qo.text);
  var oel=g(p+'opts');oel.innerHTML='';
  qo.options.forEach(function(opt,i){{
    var d=document.createElement('div');d.className='option';
    var txt=opt.replace(/^[A-Da-d]\\.\\s*/,'');var ii=i;
    d.innerHTML='<div class="opt-left"><span class="opt-letter">'+L[i]+'</span><span>'+txt+'</span></div><button class="opt-tts">&#128266;</button>';
    d.querySelector('.opt-tts').onclick=function(e){{e.stopPropagation();ttsTxt(L[ii]+'. '+txt,this);}};
    d.onclick=function(){{selOpt(n,ii);}};
    oel.appendChild(d);
  }});
  g(p+'fb').className='feedback';g(p+'jbox').className='just-box';
  g(p+'cfm').style.display='inline-block';st(p+'cfm',tr('bcfm'));
  g(p+'nxt').style.display='none';
  g(p+'prev').style.display=q.cur>0?'inline-block':'none';st(p+'prev',tr('bprv'));
  q.done=false;
}}

function selOpt(n,i){{
  var q=n===1?Q1:Q2,p=n===1?'q1':'q2';
  if(q.done)return;q.ans[q.cur]=i;
  document.querySelectorAll('#'+p+'opts .option').forEach(function(o,idx){{
    o.classList.toggle('selected',idx===i);
    var l=o.querySelector('.opt-letter');
    l.style.background=idx===i?'var(--amber)':'var(--amberBg)';
    l.style.color=idx===i?'#fff':'var(--amberTx)';
  }});
}}

function qConfirm(n){{
  var q=n===1?Q1:Q2,p=n===1?'q1':'q2';
  var c=q.ans[q.cur];if(c===null||c===undefined)return;
  q.done=true;var qo=q.qs[q.cur],L=['A','B','C','D'],ok=c===qo.correct;
  var diff=(qo.difficulty||'STANDARD').toUpperCase();
  if(!q.bd[diff])q.bd[diff]={{t:0,o:0}};q.bd[diff].t++;
  if(ok){{q.ok++;q.bd[diff].o++;}}else{{q.bad++;}}
  var opts=document.querySelectorAll('#'+p+'opts .option');
  opts.forEach(function(o){{o.classList.add('disabled');}});
  opts[c].querySelector('.opt-letter').style='';
  if(ok){{opts[c].className='option correct';g(p+'fb').className='feedback ok show';st(p+'fbhdr',tr('bok'));}}
  else{{opts[c].className='option wrong';opts[qo.correct].querySelector('.opt-letter').style='';opts[qo.correct].className='option reveal';g(p+'fb').className='feedback err show';st(p+'fbhdr',tr('berr',{{l:L[qo.correct]}}));}}
  g(p+'jbox').className='just-box show';
  st(p+'jlok',tr('jok'));st(p+'jlwrong',tr('jwrong'));
  st(p+'jok',qo.justification_correct||'');st(p+'jwrong',qo.justification_wrong||'');
  g(p+'cfm').style.display='none';g(p+'nxt').style.display='inline-block';
  st(p+'nxt',q.cur>=q.qs.length-1?tr('finish'):tr('bnxt'));
}}

function qNext(n){{var q=n===1?Q1:Q2;if(q.cur<q.qs.length-1){{q.cur++;renderQ(n);window.scrollTo(0,0);}}else finishQ(n);}}
function qPrev(n){{var q=n===1?Q1:Q2;if(q.cur>0){{q.cur--;q.done=false;renderQ(n);}}}}
function finishQ(n){{
  var q=n===1?Q1:Q2,h=n===1?h1:h2;clearInterval(q.tint);
  var s=Math.round(q.ok/q.qs.length*100);
  h.push({{s:s,tm:fmt(q.sec),sec:q.sec,dt:new Date().toLocaleDateString(lang==='pt'?'pt-BR':lang==='es'?'es-419':'en-US'),att:q.att,bd:q.bd}});
  localStorage.setItem(n===1?'{lk_key}_h1':'{lk_key}_h2',JSON.stringify(h));
  updateHero();showTab('score');
}}
function retake(){{startQ(1);showTab('quiz1');}}

function renderScore(){{
  if(!h1.length){{
    st('scpct','\\u2014');st('sclvl',tr('nohist'));st('sctime','');
    g('schistlist').innerHTML='<div style="color:var(--tx3);font-size:13px;padding:8px 0">'+tr('nohist')+'</div>';
    ['easy','std','hard'].forEach(function(x){{g('sb'+x).style.width='0%';g('sp'+x).textContent='0%';}});return;
  }}
  var last=h1[h1.length-1],bst=Math.max.apply(null,h1.map(function(h){{return h.s;}}));
  st('scpct',last.s+'%');
  var lv=last.s>=80?tr('lvlr'):last.s>=60?tr('lvlp'):tr('lvlt');
  st('sclvl',lv+' '+tr('attsuffix',{{n:last.att}}));
  st('sctime',last.tm?(tr('cin')+' '+last.tm):'');
  var bd=last.bd||{{}};
  function sb(sid,pid,dk){{var pct=bd[dk]&&bd[dk].t>0?Math.round(bd[dk].o/bd[dk].t*100):0;g(sid).style.width=pct+'%';g(pid).textContent=pct+'%';}}
  sb('sbeasy','speasy','EASY');sb('sbstd','spstd','STANDARD');sb('sbhard','sphard','HARD');
  var html='';
  h1.slice().reverse().forEach(function(h){{
    html+='<div class="sc-hist-row"><div class="sc-hist-date">'+h.dt+' · '+tr('att',{{n:h.att}})+(h.tm?' · '+h.tm:'')+'</div>';
    html+='<div style="display:flex;align-items:center;gap:8px"><span class="sc-hist-score">'+h.s+'%</span>';
    if(h.s===bst)html+='<span class="sc-best">&#9733;</span>';
    html+='</div></div>';
  }});
  g('schistlist').innerHTML=html;
}}

function updateHero(){{
  var b=best();
  g('hprog').style.width=b+'%';st('hpct',b+'%');
  st('stscore',b>0?b+'%':'\\u2014');st('stattempts',h1.length);
  st('stflash',fcDone.length+'/50');
  st('stlevel',b>=80?'★★★':b>=60?'★★☆':'★☆☆');
  updateBadge();
  var lk=g('q2lock');if(lk)lk.innerHTML=unlocked()?'':'&#128274;';
  st('q2lockprog',b>0?tr('q2best')+' '+b+'%':'');
}}
function updateBadge(){{
  var b=best(),earned=b>=80;
  var card=g('bdgcard'),img=g('bdgimg'),tag=g('bdgtag');if(!card)return;
  card.classList.toggle('earned',earned);img.classList.toggle('earned',earned);
  if(earned){{img.classList.add('badge-anim');localStorage.setItem('{lk_key}_badge','true');}}
  tag.className=earned?'badge-tag earned':'badge-tag';
  tag.textContent=earned?tr('bdgearnedtag'):(b>0?b+'% · '+(80-b)+'% left':'need 80%');
  st('bdgdesc',earned?tr('bdgearned'):tr('bdglocked'));
}}

// Eventos estaticos
g('btn-back').onclick=function(){{window.location.href='../../cfe/index.html';}};
g('btn-theme').onclick=function(){{dark=!dark;localStorage.setItem('nx_dark',dark?'1':'0');applyTheme();}};
g('btn-pt').onclick=function(){{setLang('pt');}};
g('btn-en').onclick=function(){{setLang('en');}};
g('btn-es').onclick=function(){{setLang('es');}};
g('tbn-flash').onclick=function(){{showTab('flash');}};
g('tbn-quiz1').onclick=function(){{showTab('quiz1');}};
g('tbn-quiz2').onclick=function(){{showTab('quiz2');}};
g('tbn-score').onclick=function(){{showTab('score');}};
g('flashcard').onclick=function(){{fcFlip();}};
g('btn-fcprev').onclick=function(){{ttsStop();fcIdx=(fcIdx-1+(fcQueue.length||1))%(fcQueue.length||1);renderFC();}};
g('btn-fcnext').onclick=function(){{ttsStop();fcIdx=(fcIdx+1)%(fcQueue.length||1);renderFC();}};
g('btn-no').onclick=function(e){{e.stopPropagation();fcAns(false);}};
g('btn-yes').onclick=function(e){{e.stopPropagation();fcAns(true);}};
g('tts-fcf').onclick=function(e){{e.stopPropagation();ttsTgl('fcfront-txt','tts-fcf');}};
g('tts-fcb').onclick=function(e){{e.stopPropagation();ttsTgl('fcback-txt','tts-fcb');}};
g('tts-q1').onclick=function(){{ttsQ(1,this);}};
g('tts-q2').onclick=function(){{ttsQ(2,this);}};
g('tts-q1fb').onclick=function(){{ttsTgl('q1fbhdr','tts-q1fb');}};
g('tts-q2fb').onclick=function(){{ttsTgl('q2fbhdr','tts-q2fb');}};
g('tts-q1jok').onclick=function(){{ttsTgl('q1jok','tts-q1jok');}};
g('tts-q1jwrong').onclick=function(){{ttsTgl('q1jwrong','tts-q1jwrong');}};
g('tts-q2jok').onclick=function(){{ttsTgl('q2jok','tts-q2jok');}};
g('tts-q2jwrong').onclick=function(){{ttsTgl('q2jwrong','tts-q2jwrong');}};
g('q1cfm').onclick=function(){{qConfirm(1);}};
g('q1nxt').onclick=function(){{qNext(1);}};
g('q1prev').onclick=function(){{qPrev(1);}};
g('q2cfm').onclick=function(){{qConfirm(2);}};
g('q2nxt').onclick=function(){{qNext(2);}};
g('q2prev').onclick=function(){{qPrev(2);}};
g('btnretake').onclick=function(){{retake();}};
g('btnscores').onclick=function(){{renderScore();}};

if(/iPhone|iPad|iPod/.test(navigator.userAgent)){{
  document.body.addEventListener('touchstart',function(){{}},{{passive:true}});
}}

window.addEventListener('load',function(){{
  applyTheme();applyLangBtns();
  buildQ();applyLang();renderFC();updateHero();
}});
</script>
</body>
</html>"""
    return html


# ═══ MAIN ═════════════════════════════════════════════════════
def main():
    print("=" * 70)
    print("  NEXOR -- GERADOR AUTOMATICO 44 MINI-APPS CFE v1")
    print(f"  {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("=" * 70)

    badges_dir = Path(BADGES_DIR)
    ok = 0
    falhou = []

    for i, domain in enumerate(DOMAINS):
        dom_id  = domain["id"]
        dom_key = domain["key"]
        dom_code = domain["code"]

        print(f"\n  [{i+1}/{len(DOMAINS)}] {dom_code} · {dom_key}")

        # Carrega quizzes
        q1_en_path = Path(QUIZZES_DIR) / dom_key / "quiz_001_en.json"
        q1_pt_path = Path(QUIZZES_DIR) / dom_key / "quiz_001_pt.json"
        q1_es_path = Path(QUIZZES_DIR) / dom_key / "quiz_001_es.json"

        for p in [q1_en_path, q1_pt_path, q1_es_path]:
            if not p.exists():
                print(f"  FALTA: {p}")
                falhou.append(dom_id)
                continue

        try:
            q1en = json.load(open(str(q1_en_path), encoding="utf-8"))["questions"]
            q1pt = json.load(open(str(q1_pt_path), encoding="utf-8"))["questions"]
            q1es = json.load(open(str(q1_es_path), encoding="utf-8"))["questions"]
        except Exception as e:
            print(f"  ERRO quiz: {e}")
            falhou.append(dom_id)
            continue

        # Carrega flashcards
        fc_en_path = Path(FLASHCARD_DIR) / dom_key / "flashcards_en.json"
        fc_pt_path = Path(FLASHCARD_DIR) / dom_key / "flashcards_pt.json"
        fc_es_path = Path(FLASHCARD_DIR) / dom_key / "flashcards_es.json"

        try:
            fc_en = json.load(open(str(fc_en_path), encoding="utf-8"))
            fc_pt = json.load(open(str(fc_pt_path), encoding="utf-8"))
            fc_es = json.load(open(str(fc_es_path), encoding="utf-8"))
            fc_merged = merge_fc(fc_en, fc_pt, fc_es)
        except Exception as e:
            print(f"  ERRO flashcards: {e}")
            falhou.append(dom_id)
            continue

        # Carrega badge
        # Tenta nome CFE_SID01.png para S1, CFE_S2D01.png para S2/S3
        sec = domain["section"]
        if sec == 1:
            badge_fname = f"CFE_SID{dom_id[-2:]}.png"
        else:
            badge_fname = f"CFE_{dom_code}.png"

        badge_path = badges_dir / badge_fname
        if not badge_path.exists():
            # Tenta nome alternativo
            alt = badges_dir / f"CFE_{dom_code}.png"
            if alt.exists():
                badge_path = alt
            else:
                print(f"  AVISO badge nao encontrado: {badge_fname} — usando placeholder")
                badge_b64 = ""
        else:
            badge_b64 = base64.b64encode(badge_path.read_bytes()).decode()

        # Gera HTML
        try:
            html = generate_mini_app(domain, q1en, q1pt, q1es, fc_merged, badge_b64)
        except Exception as e:
            print(f"  ERRO gerando HTML: {e}")
            falhou.append(dom_id)
            continue

        # Salva
        out_path = Path(OUTPUT_DIR) / dom_key / "index.html"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(str(out_path), "w", encoding="utf-8") as f:
            f.write(html)

        print(f"  OK → {out_path} ({len(html):,} chars)")
        ok += 1

    print("\n" + "=" * 70)
    print(f"  CONCLUIDO: {ok}/{len(DOMAINS)} mini-apps gerados")
    if falhou:
        print(f"  FALHARAM: {', '.join(falhou)}")
    print(f"  Output: {OUTPUT_DIR}/")
    print("=" * 70)


if __name__ == "__main__":
    main()
