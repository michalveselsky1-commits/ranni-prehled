# Ranní přehled – automatický zpravodajský web

Web každý den přibližně v 8:00 Europe/Prague načítá veřejné RSS zdroje, vybere pět článků (nejprve po jednom z každé ze čtyř kategorií, pátý podle skóre), uloží archiv a publikuje statickou stránku. Jde o automatický výběr a zkrácené popisky z RSS, nikoli AI redakční rešerši nebo nezávislé ověřování. Plánované GitHub Actions mohou mít zpoždění.

## Nasazení
1. Založ si účet na github.com (pokud jej ještě nemáš).
2. Vytvoř **veřejný** repozitář například `ranni-prehled` s výchozí větví `main`.
3. Nahraj **obsah** této složky do kořene repozitáře (včetně skryté `.github/workflows/publish.yml`). Nejjednodušší je přes `git` na PC nebo rozbalit ZIP a nahrát jednotlivé soubory pomocí GitHub webového rozhraní.
4. V repozitáři přejdi do **Settings → Pages → Build and deployment → Source: GitHub Actions**.
5. V **Actions → Aktualizovat ranní přehled → Run workflow** spusť první aktualizaci ručně.
6. Po úspěšném běhu otevři `https://TVUJ-UCET.github.io/ranni-prehled/` (při jiném názvu repozitáře změň i poslední část URL).

## Změny
- `sources.json`: seznam zdrojů a kategorií.
- `build.py`: bodování a výběr zpráv.
- `.github/workflows/publish.yml`: denní plán v časovém pásmu Europe/Prague.
- `site/index.html`: vzhled webu.
- `archive/`: historie posledních 90 dnů na webu; v repozitáři zůstávají všechna uložená vydání.

## Limity
Některé RSS zdroje mohou změnit adresu nebo blokovat načítání. Web ukazuje jen články dostupné v RSS (až 72 hodin staré). Pokud není dostupný žádný zdroj, existující vydání zůstane zachováno. Výstup je veřejný. Stránka není napojena na ChatGPT ani na automatické notifikace.

## Obrázky
Každá zpráva zobrazuje obrázek z RSS (media content, thumbnail nebo obrázková příloha), pokud ho zdroj nabízí. Jinak se zobrazí lokální tematická SVG ilustrace pro danou kategorii; totéž platí při chybě načtení obrázku. Ilustrace nejsou fotografiemi popisované události.
