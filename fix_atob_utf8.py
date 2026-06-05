"""
fix_atob_utf8.py — Corrige decodificação base64 para UTF-8 em todos os mini-apps
O problema: atob() decodifica como Latin-1, corrompendo caracteres UTF-8.
A solução: usar função utfDecode() que converte corretamente.
"""
from pathlib import Path

MINI_APPS_DIR = Path(r"C:\ARAGORN\aragorn_quiz\mini_apps\cfe")

# Função auxiliar a inserir no HTML
UTF8_DECODE_JS = """function utfDecode(b64){
  return decodeURIComponent(atob(b64).split('').map(function(c){
    return '%'+('00'+c.charCodeAt(0).toString(16)).slice(-2);
  }).join(''));
}
"""

# Padrão antigo — atob direto
OLD_QS1 = """var QS1 = {
  en: JSON.parse(atob('"""

NEW_QS1 = UTF8_DECODE_JS + """var QS1 = {
  en: JSON.parse(utfDecode('"""

def fix_file(path: Path) -> str:
    content = path.read_text(encoding="utf-8")
    
    # Verifica se já foi corrigido
    if "utfDecode" in content:
        return "SKIP — já corrigido"
    
    # Fix QS1
    if "var QS1 = {\n  en: JSON.parse(atob('" in content:
        content = content.replace(
            "var QS1 = {\n  en: JSON.parse(atob('",
            UTF8_DECODE_JS + "var QS1 = {\n  en: JSON.parse(utfDecode('"
        )
        content = content.replace(
            "  pt: JSON.parse(atob('",
            "  pt: JSON.parse(utfDecode('"
        )
        content = content.replace(
            "  es: JSON.parse(atob('",
            "  es: JSON.parse(utfDecode('"
        )
        # Fix FC
        content = content.replace(
            "var FC  = JSON.parse(atob('",
            "var FC  = JSON.parse(utfDecode('"
        )
        # Fix QS2 se existir
        content = content.replace(
            "var QS2_DATA = JSON.parse(atob('",
            "var QS2_DATA = JSON.parse(utfDecode('"
        )
        # Fix QS2 trilíngue
        for pattern in [
            "  en: JSON.parse(atob('",
            "  pt: JSON.parse(atob('", 
            "  es: JSON.parse(atob('"
        ]:
            content = content.replace(pattern, pattern.replace("atob(", "utfDecode("))
        
        path.write_text(content, encoding="utf-8")
        return "OK"
    
    return "SKIP — padrão não encontrado"

def main():
    ok = skip = err = 0
    for domain_dir in sorted(MINI_APPS_DIR.iterdir()):
        html = domain_dir / "index.html"
        if not html.exists():
            continue
        try:
            result = fix_file(html)
            if result == "OK":
                ok += 1
                print(f"  ✅ {domain_dir.name}")
            else:
                skip += 1
                print(f"  ⚠  {domain_dir.name} — {result}")
        except Exception as e:
            err += 1
            print(f"  ✗  {domain_dir.name} — ERRO: {e}")
    
    print(f"\nOK: {ok} · Skip: {skip} · Erros: {err}")

if __name__ == "__main__":
    main()
