# DSH — procedura przechwytywania z JIMS

**Status:** BINDING. Wczytaj ten plik na starcie sesji i trzymaj go, dopóki worklista nie jest domknięta.
**Dla:** DeepSeek Harness, Team Lead, stacja operatora, sprawy `1RC191003776` (trial) i `CAAP-26-0000625` (apelacja).
**Źródło:** audyt sesji `session-081d2245-eb88-4a73-82fb-4fad14a38813` (2026-11-03). Ta procedura zastępuje instrukcję „MAXIMIZE EFFICIENCY — NO LIMITS” na czas crawlu sądowego.
**Nie jest poradą prawną.** Zero składania, podpisywania, płacenia. Luki oznaczaj `GAP` / `for counsel`.

Kanon (publiczny, bez logowania):

https://raw.githubusercontent.com/NikoPikoFriko/the95xrecord-code/procedure/jims-capture/DSH-JIMS-CAPTURE-PROCEDURE.md

Nie parafrazuj reguł „na luźno”. Jak procedura ma się zmienić, nowy commit na tej gałęzi, nie cicha edycja w trakcie klikania w JIMS.

---

## 0. Jedno zdanie

Równolegle wolno publikować i liczyć hashe. Klikać w JIMS wolno **dokładnie jednemu** workerowi, w **jednej** przeglądarce, i dopiero po sprawdzeniu ledgeru.

Sesja z 2026-11-03 umiała zbierać dowody (19 PDF JEFS, apelacja 20/20 z URL `DocumentRetrievalServlet` z `Zone.Identifier`, audytor przeliczał bajty). Rozjechała się, gdy cztery strumienie plus Argon co 15 minut plus panel HTML weszły w tę samą sesję JSF. Trial nigdy nie otworzył `documentsTable`: `previous operation is still settling`, RPC timeout 30 s, `A page frame is not responding`.

---

## 1. Reguły, których nie wolno zmiękczyć

1. **Jeden zamek przeglądarki.** Przeglądarka, w której działa JIMS (w tej sesji `64cfb09a` — profil, gdzie eCourt Kōkua jest na allow-liście), należy wyłącznie do capturera. Przed startem: wylistuj sesje `bsk`, potwierdź żywe id, zapisz je w `CURSOR-capturer.json`. Argon, dashboard, publisher, auditor i każdy drugi agent **nie nawigują** tego okna, dopóki zamek nie spadnie.
2. **JIMS jest szeregowy.** JSF/ICEfaces, jeden ViewState, jedne ciasteczka sesji. Dwa taby z tym samym view state unieważniają się nawzajem. Paralelizm crawlu wymaga **osobnej przeglądarki i osobnego profilu z osobnym logowaniem**, albo kolejki. „No limits” na jednej sesji jest błędem, nie przyspieszeniem.
3. **Skip przed kliknięciem.** Ledger append-only: `captures/ledger.jsonl`. Klucz: `(case_id, dkt, code, sha256)`. Jeśli sha256 już jest — stan `ALREADY`, zero requestów do sądu.
4. **Bramka sprawy na stronie 1, przed ingestem.** Tekst strony 1 musi zawierać `1RC191003776` albo `CAAP-26-0000625` zgodny z wierszem worklisty. Inaczej kwarantanna `wrong-case`, plik nie wchodzi do biblioteki i nie jest liczony. Numery docketów **nakładają się** między trialem a apelacją. W sesji `Dkt 4 EXH` i `Dkt 9 NEF` były apelacją, a weszły jako trial, bo klucz był samym numerem.
5. **Tytuł = tekst wiersza JIMS albo `null`.** Nigdy linia z caption („STATE OF HAWAII”, „ASSOCIATION OF APARTMENT OWNERS”, nazwisko strony). Fałszywy tytuł jest gorszy niż brak.
6. **Przycisk certified bywa wyłączony.** W modalu: 1. Submit = zwykła kopia (włączony), 2. Submit = certified (często disabled), 3. = cancel. Nie obiecuj „certified copy zawsze”. Nie klikaj wyłączonego. Piętra, i tylko te:
   - `CERTIFIED` — w tekście jest zdanie clerk: `I do hereby certify that the foregoing is a full, true and correct copy of the official court record` (szukaj i `-layout`, i `-raw`; pieczęć bywa w stopce na istniejącym tekście).
   - `COURT-URL` — zwykła kopia plus URL `DocumentRetrievalServlet` z NTFS `Zone.Identifier`.
   - `TEXT-ONLY` — jest tekst z portalu, nie ma PDF.
   - `NO-PDF` — wiersz docketu bez dokumentu (`has_pdf=N`).
   Podpis ed25519, timestamp Bitcoina, trzy lustra i karty na X **nie zastępują** URL-a sądu. Najpierw równość: bajty PDF = sha256 = URL servletu z chwili pobrania.
7. **Apelacja przed trialem.** Strona apelacji to ~20 wierszy i klika się w 1–2 s. Trial to ~503 docket / ~468 dokumentów w jednym widoku JSF; samo otwarcie potrafi przekroczyć budżet RPC 30 s. Trial tylko po domknięciu apelacji, z filtrem tabeli albo paginacją. Nigdy pełne 468 wierszy na tym samym DevTools co publisher.
8. **Trzy porażki = stop.** `connection lost` / RPC timeout / `still settling` / `permission_denied: target covered|removed` — resync raz, retry raz, potem checkpoint i zamknij sesję przeglądarki. Nie odtwarzaj kliknięcia na ślepo. Nie zostawiaj wiszącego taba.
9. **Cel się nie zmienia w locie.** Dopóki worklista nie ma stanu na każdym wierszu, zakazane są: nowa architektura strony, wątki X, kolejna warstwa „nieatakowalności”, konsolidacja kont Google, konsultacja Argon w tej przeglądarce. Argon czyta ledger **po** zwolnieniu zamka albo z innej przeglądarki. Konsultacja co 15 minut w trakcie crawlu to samoblokada.
10. **PDF-y nie idą do gita.** Git = kod + `ledger.jsonl` + skrypty. Bajty = magazyn po hashu. Sesja utknęła na `.git` ~834 MB, 5022 loose objects, pusty remote, limit GitHuba 2 GB. Przed jakimkolwiek pushem: `git gc`. Nie commituj `Downloads`.

---

## 2. Rurociąg (kolejność twarda)

### A. Inwentarz (read-only, jedna sesja)

Zbierz wiersze docketu do `WORKLIST.tsv`: `case_id, dkt, code, filed, title_or_null, has_pdf, grade`.

Nie pobieraj PDF na tym etapie. Jeśli tabela trialu nie wstaje, zapisz `BLOCKED` z dokładnym błędem narzędzia i zejdź. Nie otwieraj drugiej sesji „na próbę” w tej samej przeglądarce.

### B. Capturer (jedyny, kto klika)

Dla każdego wiersza worklisty, po kolei:

1. Sprawdź ledger. Hit → `ALREADY`, następny wiersz.
2. `has_pdf=N` i brak przycisku dokumentu → `NO-PDF`, bez klikania Submit.
3. Otwórz modal. Certified disabled → bierz zwykłą kopię i zapisz `form=COURT-URL`, nie udawaj CERT.
4. Plik ląduje w `Downloads` jako PDF. **Nie wysyłaj go od razu do Drive.**
5. W ciągu tej samej minuty, lokalnie:
   - sha256 pełnego pliku,
   - skopiuj strumień NTFS `Zone.Identifier` (tam jest URL `DocumentRetrievalServlet?id=…` oraz strefa),
   - `pdftotext` strony 1, bramka case_id,
   - policz strony,
   - dopisz **jeden** wiersz JSON do `captures/ledger.jsonl` (append, nigdy rewrite całości w sposób, który gubi historię).
6. Dopiero potem lustro (krok C).
7. Następny klik dopiero, gdy wiersz ledgeru jest na dysku i hash się zgadza.

Pola wiersza ledgeru (wszystkie obowiązkowe; brak = wiersz nieważny):

```json
{
  "ts": "2026-11-03T21:00:00-10:00",
  "case_id": "CAAP-26-0000625",
  "dkt": "12",
  "code": "DOC",
  "filed": "2026-10-09",
  "title": null,
  "title_source": "jims-row|null",
  "form": "CERTIFIED|COURT-URL|TEXT-ONLY",
  "sha256": "<hex>",
  "bytes": 0,
  "pages": 0,
  "court_url": "https://jimspss1.courts.state.hi.us/...DocumentRetrievalServlet?id=...",
  "zone_identifier_raw": "<ADS>",
  "page1_case_gate": "pass",
  "source": "JIMS",
  "browser_id": "<id>",
  "status": "CAPTURED"
}
```

`court_url` pusty przy `form=COURT-URL` = wiersz nieważny, nie publikuj.

### C. Szpula lokalna, potem chmura

Nie ściągaj „od razu do Google Drive / GCS”. Drive gubi ADS `Zone.Identifier`, a to jest dowód pochodzenia.

- Szpula: katalog lokalny na kilkadziesiąt sekund (`staging/`).
- Lustro **po** hashu i ledgerze: `rclone copyto` na ścieżkę niezmienną
  `sha256/<dwa pierwsze znaki>/<pełny sha256>.pdf`
  na Drive (i ewentualnie R2 / Box). **Bez nadpisywania.** Jeśli obiekt o tym sha istnieje, nie wysyłaj drugi raz.
- Obok PDF: `sha256/<hh>/<sha256>.receipt.json` z polami ledgeru (URL, ADS, case gate).
- Chmura jest magazynem publikacji, nie miejscem pierwszego kontaktu z sądem.

### D. Publisher

Czyta **tylko** ledger i obiekty, których zdalny sha256 wraca taki sam. Nie dotyka JIMS. Na stronę wchodzi plik dopiero, gdy:

- `page1_case_gate=pass`,
- sha256(staging) = sha256(remote) = pole ledgeru,
- przy `COURT-URL` jest niepusty `court_url`.

Na stronie, przy dokumencie, widoczne dla człowieka i w JSON: sprawa, dkt, code, sha256, form, court_url albo jawny brak (`TEXT-ONLY` / `GAP`). Żadnego „certified”, jeśli form nim nie jest.

### E. Auditor (osobna rola, nie capturer)

Przelicza hashe z serwowanych bajtów, nie z pamięci agenta. Fałsz: plik na stronie bez wiersza ledgeru, wiersz `COURT-URL` bez URL, zła sprawa na stronie 1, dwa różne sha pod jednym (case, dkt, code) bez wyjaśnionego `supersedes`. Raport = lista PASS/FAIL ze ścieżkami, nie proza.

---

## 3. Roster

Trzy role, nie sześć. Więcej na czas crawlu tylko zwiększa koszt koordynacji.

| Rola | Wolno | Zakaz |
|---|---|---|
| capturer | jedyna przeglądarka JIMS, staging, append ledgeru | deploy, Argon, edycja strony, drugi tab JIMS |
| publisher | ledger → strona, lustro sha256 | przeglądarka JIMS |
| auditor | czytanie strony, re-hash, raport FAIL | klikanie w sąd, „naprawianie” przez ponowne pobranie |

Wspólna tablica zadań **zanim** ktokolwiek wstanie. Rozłączne `write_scopes`. Capturer kończy się, gdy worklista jest domknięta, nie gdy „wydaje się, że dużo zszedł”.

Dashboard: statyczny HTML z ledgeru, serwowany lokalnie, **otwierany przez operatora**. Agent go nie nawiguje w przeglądarce sądowej. Instrukcja „ten sam browser co Jeffs i Kokua” jest wyłączona na czas tej procedury.

---

## 4. Stany wiersza (jedno z czterech)

`CAPTURED` | `ALREADY` | `NO-PDF` | `BLOCKED`

`BLOCKED` niesie dosłowny komunikat narzędzia i numer wiersza wznowienia. Bez tego wiersz nie istnieje.

**Done** = każdy wiersz worklisty ma dokładnie jeden z tych stanów i dowód w ledgerze albo w `BLOCKER.md`. Apelacja `CAAP-26-0000625` pierwsza. Trial `1RC191003776` drugi. Nie deklaruj „full court crawl”, jeśli trial stoi na `BLOCKED`.

Worklista, która już coś wie: 75 z 78 kandydatów trial NOCD/NTCE/NOCDA miało `has_pdf=N` (same noty). Trzy PDF-y (dkt 466, 467, 468) były już w bibliotece. 10 z 12 nowych zrzutów apelacji było bajt w bajt tym, co już leżało — nową wartością był URL sądu, nie plik. Dlatego skip-before-click jest obowiązkowy, nie optymalizacją.

---

## 5. Czego nie robić (wprost z tej sesji)

- Nie stawiaj czterech agentów na jednym `bsk`.
- Nie dokładaj celu („zrób stronę nieatakowalną”, X.com, SQLite-WASM, R2, Bitcoin), dopóki brakuje `court_url` na wierszach, które już są na stronie.
- Nie nazywaj pliku z samego numeru docketu.
- Nie zgaduj tytułu z nagłówka stron.
- Nie publikuj apelacji pod kluczem trialu.
- Nie traktuj wyłączonego Submit certified jako sukcesu certyfikacji.
- Nie ruszaj konsolidacji kont Google. Decyzja operatora z tej sesji: **C — sama topologia, bez scalania.**
- Nie wklejaj sekretów, tokenów, haseł JIMS ani OAuth do tego pliku, sesji, gita, Box comments.

Terminy wyczytane z akt (nie ruszaj ich, nie składaj nic): jurisdictional statement **9 listopada 2026**, opening brief **7 grudnia 2026**. To kontekst priorytetu, nie polecenie wniesienia pisma.

---

## 6. Cel do wklejenia jako jedyny aktywny goal

```text
Jedyny aktywny cel: domknąć worklistę JIMS dla CAAP-26-0000625, potem 1RC191003776.

Procedura BINDING (przeczytaj w całości, nie streszczaj):
https://raw.githubusercontent.com/NikoPikoFriko/the95xrecord-code/procedure/jims-capture/DSH-JIMS-CAPTURE-PROCEDURE.md

Jeden zamek przeglądarki JIMS. Argon, dashboard i inni agenci nie dotykają tego okna.
Ledger append-only captures/ledger.jsonl. Klucz (case_id, dkt, code, sha256).
Przed kliknięciem: sha jest → ALREADY.
Strona 1 musi potwierdzić case_id albo kwarantanna wrong-case.
Tytuł = wiersz JIMS albo null.
Form tylko CERTIFIED | COURT-URL | TEXT-ONLY. Disabled certified Submit ≠ CERTIFIED.
Po każdym pliku, zanim następny klik: hash, kopia Zone.Identifier, wiersz ledgeru,
potem rclone copyto na sha256/<hh>/<sha>.pdf bez nadpisywania.
PDF nie wchodzi do gita.
Trzy kolejne błędy mostka = checkpoint i stop.
Done = każdy wiersz worklisty jest CAPTURED | ALREADY | NO-PDF | BLOCKED z dowodem.
Bez składania, podpisywania i płacenia. Luki: GAP, for counsel.
```

---

## 7. Definition of done dla samej procedury (wdrożenie przez DeepSeek)

Uznaj procedurę za wdrożoną dopiero, gdy w repo albo w skillu stacji jest **wszystko** poniżej i da się to pokazać ścieżką pliku:

1. Skill albo sekcja `AGENTS.md` / `DSH-SESSION-PROTOCOL.md`, która cytuje te 10 reguł i jest ładowana przed jakimkolwiek `bsk` na JIMS.
2. Skrypt `one_doc` (albo równoważny) z twardą bramką: odrzut, jeśli page 1 nie zawiera oczekiwanego case_id.
3. `captures/ledger.jsonl` append-only i sprawdzanie skip-before-click **przed** pierwszym requestem w nowej sesji, nie po.
4. Zapis `Zone.Identifier` do `*.receipt.json` zanim plik ruszy do rclone.
5. Ścieżka chmury `sha256/<hh>/<sha256>.pdf` bez nadpisywania.
6. Assert w publisherze: brak obiektu `COURT-URL` bez `court_url`; brak pliku apelacji w kubełku trialu.
7. Capturer odmawia startu, jeśli `bsk` pokazuje więcej niż jedną sesję na przeglądarce JIMS.
8. Zaplanowany Argon jest wstrzymany, gdy istnieje plik zamka `JIMS.lock` (capturer tworzy go na starcie i kasuje przy czystym wyjściu; po crashu zamek zostaje i wymusza decyzję operatora).

Nie oznaczaj taska „procedura wdrożona” na podstawie samego przeczytania tego pliku.
