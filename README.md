<div align="center">

<img width="128" height="128" alt="Nucleus" src="https://github.com/user-attachments/assets/f9798e24-1ac1-49a0-8831-eb7bd8ad9dc2" />

# Nucleus

**Минималистичный командный центр для Windows**

Одно окно. Один хоткей. Всё под рукой.

`Ctrl + Space` — и вы дома.

[![Windows](https://img.shields.io/badge/Windows-10%20%7C%2011-0078D6?logo=windows&logoColor=white)](#)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)](#)
[![PyQt6](https://img.shields.io/badge/PyQt6-6.11-41CD52?logo=qt&logoColor=white)](#)
[![License](https://img.shields.io/badge/License-GPLv3-C6FF4A)](https://www.gnu.org/licenses/gpl-3.0.html)

</div>

---

## <img src="https://api.iconify.design/lucide:sparkles.svg?color=%23C6FF4A" width="22"/> Что это

Nucleus — это лёгкий командный центр, который живёт в трее и вызывается одной
комбинацией клавиш. Внутри — заметки с Markdown, калькулятор с графиками и
уравнениями, эмодзи-пикер, системный монитор, таймер, поиск в Google и YouTube,
а также система плагинов и тем.

Никаких облаков, аккаунтов и телеметрии. Всё локально, всё в `nucleus.db`
рядом с приложением.

---
## Скриншоты
<img width="1005" height="657" alt="image" src="https://github.com/user-attachments/assets/decb91ba-58aa-4ad8-ad5b-c832d1929485" />
<img width="1007" height="251" alt="image" src="https://github.com/user-attachments/assets/da13dbe8-1ff1-48ac-9f75-b183f0244337" />
<img width="1019" height="865" alt="image" src="https://github.com/user-attachments/assets/32be884b-58dc-47ce-a1fa-cf3c6e95c953" />
<img width="1013" height="868" alt="image" src="https://github.com/user-attachments/assets/1f4269ca-41b2-40a8-a31a-0306dd803f83" />
<img width="1016" height="864" alt="image" src="https://github.com/user-attachments/assets/6f8990c4-fa13-4dfa-a749-022429a970dc" />
<img width="998" height="854" alt="image" src="https://github.com/user-attachments/assets/a3364c9f-4b9d-49ca-a5dd-667976ef3231" />
<img width="1021" height="862" alt="image" src="https://github.com/user-attachments/assets/f5408229-5df7-4208-92d6-c215e4dc56a4" />
<img width="1015" height="862" alt="image" src="https://github.com/user-attachments/assets/8f3c9ebf-8ace-4703-a929-46b3355b1895" />
<img width="1028" height="880" alt="image" src="https://github.com/user-attachments/assets/1a475fa6-41f2-499e-864c-0e3cf23e3180" />
<img width="1041" height="265" alt="image" src="https://github.com/user-attachments/assets/6d9d2387-aa93-48a2-9b78-bf55733ed3a2" />
<img width="1007" height="256" alt="image" src="https://github.com/user-attachments/assets/dc729135-f77a-4a0b-982e-b98bb11b5477" />
<img width="909" height="342" alt="image" src="https://github.com/user-attachments/assets/ce2dfc5c-6516-4b0c-8519-4f2998a71d67" />


## <img src="https://api.iconify.design/lucide:rocket.svg?color=%23C6FF4A" width="22"/> Установка

### Вариант 1: готовый `.exe`

1. Скачайте `Nucleus.exe` из релизов
2. Положите в удобную папку, например `C:\Nucleus\`
3. Запустите — приложение свернётся в трей
4. Нажмите `Ctrl + Space` — окно появится

Первый запуск — 5–10 секунд (распаковка). Дальше — мгновенно.

### Вариант 2: из исходников

```bash
git clone https://github.com/ваш-логин/nucleus.git
cd nucleus
pip install -r requirements.txt
python main.py
```

---

## <img src="https://api.iconify.design/lucide:zap.svg?color=%23C6FF4A" width="22"/> Быстрый старт

| Клавиша | Действие |
|---|---|
| `Ctrl + Space` | Показать / скрыть окно |
| `↑` / `↓` | Навигация по списку |
| `Enter` | Выполнить выбранное |
| `Esc` | Назад / скрыть окно |
| `Ctrl + K` | Очистить поле ввода |

Начните печатать — список фильтруется. Префиксы открывают модули:

---

## <img src="https://api.iconify.design/lucide:puzzle.svg?color=%23C6FF4A" width="22"/> Модули

| Префикс | Модуль | Что делает |
|---|---|---|
| `>` | **Shell** | Выполнить команду через PowerShell |
| `=` | **Калькулятор** | Выражения, **дроби**, **уравнения**, **графики**, **таблицы** |
| `@` | **Открыть** | Папка или файл в проводнике |
| `g` | **Google** | Поиск в браузере |
| `yt` | **YouTube** | Поиск видео |
| `#` | **Заметки** | Markdown-редактор с живым превью и автосейвом |
| `:` | **Эмодзи** | Сетка с категориями и поиском |
| `%` | **Система** | CPU, RAM, диск, график 60 сек, топ процессов |
| `~` | **Таймер** | `~ 5m`, `~ 1h30m`, `~ 90s` или просто `~` |
| `?` | **Помощь** | Шпаргалка + туториал + настройки |

---

## <img src="https://api.iconify.design/lucide:calculator.svg?color=%23C6FF4A" width="22"/> Калькулятор

Пять вкладок:

- **Выражение** — `2+2*sin(pi/3)`, `sqrt(144)`, `ans*2`
- **Дроби** — `1/2 + 3/4` → `5/4`, десятичное и смешанное `1 1/4`
- **Уравнения** — `x^2 - 4 = 0` → `x₁ = -2, x₂ = 2`
- **График** — `sin(x); cos(x)` — несколько кривых сразу
- **Таблица** — f(x) для x от…до…шаг + экспорт в CSV

---

## <img src="https://api.iconify.design/lucide:file-text.svg?color=%23C6FF4A" width="22"/> Заметки

- Markdown с живым превью
- Тулбар: **B** *I* `</>` H1 • список • цитата • ссылка • таблица
- Автосохранение каждые 600 мс
- Поиск по заметкам
- Всё в `nucleus.db`

---

## <img src="https://api.iconify.design/lucide:plug.svg?color=%23C6FF4A" width="22"/> Плагины

Папка `plugins/` — вы кладёте `.py`, появляется новый экшен.

Пример `plugins/hello.py`:

```python
import webbrowser

def register(api):
    @api.action("hh", "Hello от плагина", "fa5s.hand-peace", "демо")
    def hello(_):
        return "плагины работают!"

    @api.action("yt", "YouTube", "fa5b.youtube", "поиск видео")
    def yt(q):
        url = f"https://youtube.com/results?search_query={q.lstrip('yt').strip()}"
        webbrowser.open(url)
        return "открыл YouTube"
```

Перезапустите Nucleus — новый экшен появится в списке.

### API

| Метод | Что делает |
|---|---|
| `api.action(prefix, title, icon, subtitle)` | Регистрирует новое действие (декоратор) |
| `api.notify(title, text)` | Показывает уведомление в трее |

Иконки — FontAwesome 5: `fa5s.*` (solid), `fa5b.*` (brands).

---

## <img src="https://api.iconify.design/lucide:palette.svg?color=%23C6FF4A" width="22"/> Темы

Папка `themes/` — `.json` файлы. Вы кладёте новый — он появляется в меню трея.

Структура темы:

```json
{
  "name": "Nord",
  "ACCENT": "#88C0D0",
  "CARD":   "#2E3440",
  "BG":     "#242933",
  "PANEL":  "#3B4252",
  "DIM":    "#616E88",
  "TEXT":   "#ECEFF4",
  "SUB":    "#D8DEE9",
  "LINE":   "#434C5E"
}
```

Готовые темы:

| Тема | Цвет | Описание |
|---|---|---|
| ![Acid](https://img.shields.io/badge/Acid-C6FF4A?style=flat-square&color=C6FF4A&labelColor=C6FF4A) | `#C6FF4A` | Кислотный лайм (по умолчанию) |
| ![Nord](https://img.shields.io/badge/Nord-88C0D0?style=flat-square&color=88C0D0&labelColor=88C0D0) | `#88C0D0` | Холодный синий |
| ![Matrix](https://img.shields.io/badge/Matrix-00FF88?style=flat-square&color=00FF88&labelColor=00FF88) | `#00FF88` | Зелёный терминал |
| ![Plasma](https://img.shields.io/badge/Plasma-E0AAFF?style=flat-square&color=E0AAFF&labelColor=E0AAFF) | `#E0AAFF` | Фиолетовый |

Смена темы: правый клик по иконке в трее → **Тема** → выбрать.
Приложение перезапустится с новой темой.

---

## <img src="https://api.iconify.design/lucide:hammer.svg?color=%23C6FF4A" width="22"/> Сборка `.exe`

### Требования

- Python 3.11+
- PyInstaller 6+
- Иконка `assets/nucleus.ico` (256×256)

### Сборка

```bash
cd C:\nucleus
build.bat
```

Готовый файл — `dist\Nucleus.exe`. Размер ~80–350 МБ в зависимости от
исключённых модулей.

### Что внутри

- `--onefile` — один `.exe`
- `--windowed` — без консоли
- `--icon=assets/nucleus.ico` — своя иконка
- `--add-data` — вшиты `themes/` и `plugins/`

---

## <img src="https://api.iconify.design/lucide:folder-tree.svg?color=%23C6FF4A" width="22"/> Структура

```
nucleus/
├── main.py                 # каркас, окно, трей, хоткей
├── theme.py                # читает config.json + themes/*.json
├── registry.py             # @action, поиск, REGISTRY
├── requirements.txt
├── build.bat
├── nucleus.spec
├── config.json             # {"theme": "acid"}
├── assets/
│   └── nucleus.ico
├── core/
│   ├── __init__.py
│   ├── plugins.py          # загрузчик плагинов
│   └── themes.py           # список и переключение тем
├── screens/
│   ├── __init__.py
│   ├── notes.py            # Markdown-редактор
│   ├── calc.py             # 5 вкладок калькулятора
│   ├── emoji.py            # сетка эмодзи
│   ├── system.py           # CPU/RAM/графики
│   ├── timer.py            # таймер
│   ├── help.py             # шпаргалка
│   └── tutorial.py         # туториал при первом запуске
├── themes/
│   ├── acid.json
│   ├── nord.json
│   ├── matrix.json
│   └── plasma.json
└── plugins/
    └── hello.py
```

---

## <img src="https://api.iconify.design/lucide:package.svg?color=%23C6FF4A" width="22"/> Зависимости

| Пакет | Назначение |
|---|---|
| `PyQt6` | UI, окна, анимации |
| `QtAwesome` | Иконки FontAwesome |
| `pyqtgraph` | Графики |
| `numpy` | Вычисления для графиков |
| `sympy` | Решение уравнений |
| `Markdown` | Рендер заметок |
| `psutil` | Системные метрики |
| `pynput` | Глобальный хоткей `Ctrl+Space` |
| `emoji` | База эмодзи с тегами |

Установка:

```bash
pip install -r requirements.txt
```

---

## <img src="https://api.iconify.design/lucide:shield-check.svg?color=%23C6FF4A" width="22"/> Приватность

- **Всё локально** — никаких сетевых запросов, кроме Google/YouTube
  (когда вы сами их вызываете)
- **Никаких аккаунтов** — просто `.exe` и `nucleus.db`
- **Никакой телеметрии**
- Данные: `nucleus.db` рядом с приложением (заметки, история, мета)

Чтобы начать с чистого листа — очистите `nucleus.db`, приложение создаст
новый файл при следующем запуске.

---

## <img src="https://api.iconify.design/lucide:help-circle.svg?color=%23C6FF4A" width="22"/> FAQ

**Ctrl+Space не работает**

Скорее всего `pynput` блокируется. Запустите `.exe` от имени администратора
один раз. Или проверьте, что хоткей не занят другим приложением
(например, Spotlight / PowerToys / Alfred).

**Антивирус ругается на `.exe`**

Норма для PyInstaller onefile. Добавьте в исключения. Или пересоберите
с `--onedir` — антивирусы лояльнее.

**Иконка в проводнике не обновилась**

Кэш Windows. Переименуйте `.exe` или перезапустите `explorer.exe`.

**Первый запуск долгий**

PyInstaller распаковывает содержимое `.exe` во временную папку. Дальше —
мгновенно. Если хочется быстрее — используйте `--onedir`.

**Где хранится база?**

Рядом с `Nucleus.exe`: `nucleus.db`. Чтобы начать с чистого листа —
очистите файл, приложение создаст новый при следующем запуске.

---
## <img src="https://api.iconify.design/lucide:scroll-text.svg?color=%23C6FF4A" width="22"/> Лицензия

Этот проект распространяется под лицензией **GNU General Public License v3.0**.

Вы можете свободно использовать, изучать, изменять и распространять Nucleus
при условии, что производные работы также будут открыты под GPL-3.0.

Полный текст лицензии: [gnu.org/licenses/gpl-3.0](https://www.gnu.org/licenses/gpl-3.0.html)

---

<div align="center">

**Nucleus** — потому что всё должно быть в одном месте.


</div>
