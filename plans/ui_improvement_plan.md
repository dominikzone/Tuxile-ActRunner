# Plan Poprawy Wizualnej Overlayu PoE Linux QCL

Celem jest zwiększenie czytelności instrukcji, zwłaszcza gdy tekstu jest dużo, oraz poprawa ogólnej estetyki UI.

## 1. Wyrównanie i Marginesy
- **Plik:** `main.py`
- **Zmiana:** Zmień `self.step_label.setAlignment(Qt.AlignmentFlag.AlignCenter)` na `Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter`.
- **Marginesy:** Zwiększ marginesy kontenera (`self.container_layout.setContentsMargins(15, 10, 15, 10)`).

## 2. Listy Punktowe (Bullet Points)
- **Plik:** `main.py` -> `update_step_ui`
- **Logika:** Podziel tekst instrukcji na zdania (używając kropek jako separatora) i sformatuj je jako `<ul><li>...</li></ul>`.

## 3. Rozszerzona Paleta Kolorów
- **Logika:** Użyj regex lub prostych zamian dla słów kluczowych:
  - `Kill`, `Defeat`, `Clear` -> `#ff4d4d` (Czerwony)
  - `Help`, `Talk`, `Quest` -> `#50fa7b` (Zielony)
  - `Go to`, `Enter` -> `#f8f8f2` (Biały/Jasny)

## 4. Interlinia i Typografia
- **CSS:** Dodaj `line-height: 120%` do stylu `step_label`.
- **Font:** Upewnij się, że `scale_font` zachowuje czytelność.

## 5. Odznaki (Badges) dla Słów Kluczowych
- **Styl:** Zamiast samego koloru tekstu dla `[WP]`, użyj:
  ```html
  <span style='background-color: #4da6ff; color: white; border-radius: 3px; padding: 0 3px;'>WP</span>
  ```

## 6. Hierarchia Informacji
- **Zmiana:** Zmniejsz `font-size` dla `target_zone_label` do 9px i zmień kolor na bardziej stonowany (np. `#888888`).

## 7. Czytelność na Tle (Text Halo/Shadow)
- **Zmiana:** Wzmocnij `QGraphicsDropShadowEffect` (zwiększ blur radius do 6 i offset do 1,1).

## 8. Separatory
- **Zmiana:** Dodaj poziomą linię (`<hr>`) lub widget separatora między informacją o lokacji a właściwą instrukcją.

## 9. Skalowanie Czcionek
- **Poprawka:** Dostosuj algorytm w `scale_font`, aby uniknąć zbyt dużych liter przy szerokich, ale niskich oknach.

## 10. Pasek Postępu
- **Zmiana:** `self.progress_bar.setFixedHeight(5)`, dodaj `border: 1px solid #FFD700`.
