"""
NEXOR -- GERADOR FLASHCARDS S1D06 -- EN v1
Gera 50 flashcards para o dominio S1D06
Corruption, Bribery & Conflicts of Interest.
Blocos de 10 por chamada -- sem truncamento.

USO:
    python gerar_flashcards_s1d06.py
"""

import json
import anthropic
from pathlib import Path
from datetime import datetime

FLASHCARDS_DIR = r"static\flashcards\cfe"
MODEL          = "claude-sonnet-4-5"
MAX_TOKENS     = 8192
TIMESTAMP      = datetime.now().strftime("%Y%m%d_%H%M")

DOMAIN = {
    "domain_id":   "corruption_bribery",
    "domain_code": "S1D06",
    "domain_name": "S1D06 · Corruption, Bribery & Conflicts of Interest",
    "context": """CFE Exam 2026 S1D06 — Corruption, Bribery and Conflicts of Interest.
Topics: bribery schemes, kickbacks in procurement, bid rigging (complementary bidding,
bid suppression, bid rotation), conflicts of interest (undisclosed financial interests,
self-dealing), illegal gratuities, economic extortion, shell company corruption,
facilitation payments, FCPA anti-bribery provisions, UK Bribery Act,
OECD Anti-Bribery Convention, red flags of corruption, detection methods,
Tyco International case study."""
}

# 50 topicos para os flashcards
TOPICS = [
    # CONCEITOS BASICOS (1-10)
    "Definition of bribery in the CFE context",
    "Definition of kickback scheme",
    "Definition of conflict of interest in fraud examination",
    "Definition of illegal gratuity vs bribery",
    "Definition of economic extortion",
    "Definition of bid rigging",
    "Types of bid rigging schemes",
    "Definition of facilitation payment under FCPA",
    "Shell company role in corruption schemes",
    "Red flags of bribery in procurement",
    # FCPA E LEGISLAÇÃO (11-20)
    "FCPA anti-bribery provisions — key elements",
    "FCPA accounting provisions — books and records",
    "FCPA — who is covered (issuers and domestic concerns)",
    "FCPA — third party liability and due diligence",
    "UK Bribery Act — key differences from FCPA",
    "UK Bribery Act — corporate offense of failing to prevent bribery",
    "OECD Anti-Bribery Convention — main obligations",
    "FCPA facilitating payments exception",
    "FCPA affirmative defenses",
    "Penalties under FCPA — criminal and civil",
    # ESQUEMAS DE CORRUPÇÃO (21-30)
    "Complementary bidding scheme — how it works",
    "Bid suppression scheme — how it works",
    "Bid rotation scheme — how it works",
    "Kickback detection methods in accounts payable",
    "Conflict of interest — vendor relationship red flags",
    "Corruption in public procurement — warning signs",
    "Ghost vendor scheme in corruption context",
    "Tyco International case — key fraud lessons",
    "Economic extortion vs bribery — key distinction",
    "Self-dealing as conflict of interest",
    # DETECÇÃO E INVESTIGAÇÃO (31-40)
    "Data analytics techniques for detecting kickbacks",
    "Vendor master file analysis for corruption detection",
    "Interview techniques for corruption investigations",
    "Documentary evidence in bribery investigations",
    "Role of confidential informants in corruption cases",
    "Digital forensics in corruption investigations",
    "Asset tracing in corruption cases",
    "International cooperation in corruption investigations",
    "Whistleblower protections in corruption reporting",
    "Corporate compliance programs — key elements",
    # PREVENÇÃO E CONTROLES (41-50)
    "Internal controls to prevent procurement fraud",
    "Segregation of duties in purchasing process",
    "Due diligence on third parties and agents",
    "Code of conduct — anti-bribery provisions",
    "Anti-corruption training program components",
    "Gifts and entertainment policy — best practices",
    "Conflict of interest disclosure policy",
    "Risk-based anti-corruption compliance program",
    "Tone at the top — role in corruption prevention",
    "Anti-corruption audit procedures"
]

def save_json(path, data):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def call_api(client, prompt):
    response = client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        messages=[{"role": "user", "content": prompt}]
    )
    raw = response.content[0].text.strip()
    raw = raw.replace("```json", "").replace("```", "").strip()
    return json.loads(raw)

def generate_flashcard_block(client, topics, num_start):
    """Gera um bloco de flashcards EN."""
    topics_str = "\n".join(f"{i+1}. {t}" for i, t in enumerate(topics))

    prompt = f"""You are an expert CFE (Certified Fraud Examiner) exam content writer.

DOMAIN: {DOMAIN['domain_name']}
CONTEXT: {DOMAIN['context']}

Create exactly {len(topics)} flashcards for CFE exam preparation.
Start numbering from id={num_start}.

FLASHCARD RULES:
- FRONT: A clear, concise question or term (max 120 characters)
- BACK: A precise definition or answer (2-4 sentences max)
  + one practical example when relevant
- Language: English
- Keep legal terms: FCPA, UK Bribery Act, OECD, etc.
- Focus on what CFE candidates need to know for the exam

Topics to cover (one flashcard per topic, in order):
{topics_str}

Return ONLY valid JSON array, no markdown:
[{{
  "id": {num_start},
  "topic": "snake_case_topic",
  "front": {{
    "en": "Question or term in English"
  }},
  "back": {{
    "en": "Definition and example in English"
  }}
}}]"""

    result = call_api(client, prompt)
    for i, card in enumerate(result):
        card["id"] = num_start + i
    return result

def main():
    print("=" * 70)
    print("  NEXOR -- GERADOR FLASHCARDS S1D06 -- EN v1")
    print(f"  {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print(f"  50 flashcards · Blocos de 10")
    print("=" * 70)

    client = anthropic.Anthropic()
    all_cards = []

    # Gera em blocos de 10
    blocks = [TOPICS[i:i+10] for i in range(0, len(TOPICS), 10)]

    for i, block in enumerate(blocks):
        num_start = i * 10 + 1
        end = min(num_start + 9, 50)
        print(f"\n  Bloco {i+1}/5 · Card {num_start}-{end}... ", end="", flush=True)
        try:
            cards = generate_flashcard_block(client, block, num_start)
            all_cards.extend(cards)
            print(f"OK ({len(cards)} cards)")
        except Exception as e:
            print(f"ERRO: {e}")

    if not all_cards:
        print("  FALHOU — nenhum card gerado")
        return

    for i, card in enumerate(all_cards):
        card["id"] = i + 1

    # Salva
    out_path = Path(FLASHCARDS_DIR) / "corruption_bribery" / "flashcards_en.json"
    save_json(str(out_path), {
        "cert_id":     "cfe",
        "domain_id":   "corruption_bribery",
        "domain_code": "S1D06",
        "domain_name": DOMAIN["domain_name"],
        "lang":        "en",
        "total":       len(all_cards),
        "cards":       all_cards
    })

    print(f"\n  EN: {len(all_cards)} flashcards salvos ✅")
    print(f"  Arquivo: {out_path}")
    print("\n" + "=" * 70)
    print("  CONCLUIDO")
    print("  Proximo: traduzir para PT e ES")
    print("=" * 70)

if __name__ == "__main__":
    main()
