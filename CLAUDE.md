# CLAUDE.md — Tuxile ActRunner

## Opis projektu

Nakładka (overlay) dla Path of Exile 2 działająca jako przezroczyste okno na wierzchu gry.
Wyświetla krok po kroku walkthrough aktów, śledzi postęp przez parsowanie `Client.txt`.

Stack: **Python 3.12 + PyQt6 + QML (QtQuick 6)**

Uruchomienie: `python main.py` (w venv z PyQt6)

---

## Struktura plików

```
main.py             — Punkt wejścia. Klasy OverlayBridge (QObject/pyqtProperty)
                      i PoEApp (init silnika QML, LogWatcher, skanowanie logów)
overlay.qml         — Cały UI: cyberpunk theme, animacje, drag/resize, przyciski
walkthrough_data.py — WALKTHROUGH (lista dict ze strefami i tekstem), TOWNS, ICON_MAPPING
log_watcher.py      — QThread monitorujący Client.txt co 500ms; emituje sygnały:
                      zone_changed, waypoint_discovered, quest_item_found,
                      quest_completed, boss_slain, trial_completed
config_manager.py   — load_config / save_config (JSON, ścieżka w ~/.config lub podobna)
styles.qss          — (nowy plik, niezintegrowany jeszcze z kodem)
venv/               — virtualenv, ignorować
```

Konfiguracja persystuje w JSON: `window_x/y`, `window_width/height`, `opacity`,
`base_font_size`, `click_through`, `current_step`, `completed_data`, `client_txt_path`.

---

## Architektura QML ↔ Python

```
QML Window (overlay.qml)
  └─ bridge.*  ←→  OverlayBridge(QObject)
                     ├─ pyqtProperty: currentStepIndex, totalSteps, substeps,
                     │                actTitle, windowX/Y/Width/Height,
                     │                opacity, baseFontSize, clickThrough, currentZone
                     └─ pyqtSlot:    onSubstepClicked, onPrevStep, onNextStep,
                                     increaseFontSize, decreaseFontSize,
                                     updateWindowPos, updateWindowSize,
                                     adjustOpacity, toggleClickThrough,
                                     resetProgress, save_config_to_disk

LogWatcher(QThread) --sygnały--> PoEApp.on_zone_changed / on_waypoint_discovered / ...
                                   --> bridge.mark_substep_completed() / bridge.currentStepIndex
```

Drag/resize: obsługiwany w QML przez `globalDragArea` (MouseArea z Ctrl+LMB).
Po zwolnieniu: `bridge.updateWindowPos()` + `bridge.updateWindowSize()` + `bridge.save_config_to_disk()`.

Debouncing zapisu: `QTimer` (1s singleShot) w `OverlayBridge.request_save()`.

---

## Znalezione problemy (sesja 2025-03-12)

### KRYTYCZNE — powodują lag/freeze całego komputera

**[QML-1] `layer.enabled: true` + MultiEffect na całym mainContainer (overlay.qml:104-112)**
- Cały interfejs renderowany do FBO offscreen co klatkę, przepuszczany przez GLSL shader
- Każda zmiana czegokolwiek w UI inwaliduje całą warstwę GPU
- Naprawa: usunąć `layer.enabled` z mainContainer; cień robić przez osobny element

**[QML-2] Resize/drag przez `root.width += dx` w `onPositionChanged` (overlay.qml:66-78)**
- `onPositionChanged` odpala się przy każdym pikselu ruchu myszy
- Każde przypisanie wymusza relayout + reinwalidację warstwy GPU z [QML-1]
- Flaga `isDragging` wyłącza efekt MultiEffect, ale `layer.enabled` pozostaje true → FBO nadal aktywne
- Naprawa: `layer.enabled: !globalDragArea.isDragging` (nie tylko `enabled` MultiEffect)

**[PY-1] Brakująca linia `replacements = {` w `update_substeps()` (main.py:106-111)**
- SyntaxError — aplikacja nie uruchomi się z tym kodem (plik ma `M` w git status)
- Linia `replacements = {` została przypadkowo usunięta

### WYSOKIE — błędy działania

**[QML-3] Konflikt MouseArea — przyciski nie działają prawidłowo (overlay.qml:48-91)**
- `globalDragArea` ma `propagateComposedEvents: true`, child MouseArea przycisków z `z: 10`
- W Qt6 propagacja eventów między overlapping MouseArea zmieniła się; kliknięcia mogą "ginąć"
- Naprawa: zastąpić globalDragArea przez `DragHandler` na title barze (nie na całym oknie)

**[PY-2] Brak `@pyqtSlot` na handlerach LogWatcher (main.py:323-329)**
- `on_zone_changed`, `on_waypoint_discovered` itp. to zwykłe metody Python bez dekoratora
- Sygnały z QThread mogą być wykonane w wątku emitującym (nie main thread) → race condition
- Naprawa: dodać `@pyqtSlot(str)` / `@pyqtSlot()` do każdego handlera w PoEApp

### ŚREDNIE — wydajność

**[QML-4] `glowOpacity` animacja infinite + layer na pasku postępu (overlay.qml:33-37, 403-408)**
- `glowOpacity` zmienia się co klatkę → inwaliduje pasek z `layer.enabled: true` + MultiEffect blur
- W połączeniu z [QML-1]: cały ekran re-renderowany co ~16ms bez powodu
- Naprawa: usunąć layer z paska; animować kolor zamiast opacity, lub zrezygnować z blur

**[QML-5] cursorVisible Timer co 500ms (overlay.qml:40-43)**
- Zmiana tekstu tytułu inwaliduje warstwę GPU z [QML-1] co 500ms
- Naprawa: po usunięciu [QML-1] niegroźne; można zostawić

**[PY-3] `update_substeps()` — ciężkie regex na głównym wątku (main.py:96-142)**
- Wielokrotne `re.sub()`, `re.findall()`, pętle po keywords × substepy
- Wywoływane synchronicznie przy każdej zmianie kroku
- Naprawa: cache'ować przetworzone HTML per idx step

### NISKIE

**[QML-6] Błąd logiczny fade animacji kroków (overlay.qml:319-334)**
- Timer (50ms) odpala przed zakończeniem animacji opacity (200ms) → treść nigdy nie znika do 0
- Naprawa: wydłużyć timer do 250ms lub użyć `onRunningChanged`

**[PY-4] `scan_log_history()` blokuje init (main.py:310-347)**
- Odczyt do 50KB pliku logów synchronicznie podczas `__init__`
- Naprawa: `QTimer.singleShot(0, self.scan_log_history)`

---

## Ważne konwencje kodu

- Substepy generowane przez split tekstu WALKTHROUGH po `.` (linia 133 main.py)
- `completed_data` w config to `{str(step_idx): [list_of_completed_substep_indices]}`
- `auto_completed_steps: set` śledzi które kroki były auto-ukończone (guard przed backtrack)
- LogWatcher robi `msleep(500)` — polling co 0.5s
- Czcionki cyberpunk: `Orbitron` (nagłówki/przyciski), `Share Tech Mono` (tekst kroków)
- Kolory: neonCyan `#00ffff`, neonPurple `#9000ff`, neonGreen `#00ff88`, dangerRed `#ff4466`
- Click-through toggle (przycisk L/U): zmienia flagi okna Qt przez `bridge.clickThrough`
- `[ICON:...]` tagi w WALKTHROUGH są stripowane w QML i podmieniane na HTML span w Pythonie

---

## Kolejne zadania (backlog)

Wszystkie zidentyfikowane błędy naprawione w sesji 2026-03-12.

Drag: `globalDragArea` (MouseArea + propagateComposedEvents) zastąpiony przez:
- `DragHandler` (id: windowMoveHandler) — Ctrl+LMB, cały Window, nie kradnie kliknięć
- `WheelHandler` — Ctrl+Wheel dla opacity
- `MouseArea` (id: resizeHandle) — 40×40 px prawy dolny róg, Ctrl+LMB

Cache substepów: `_html_cache: dict` w OverlayBridge — regex tylko przy pierwszym dostępie do kroku.
