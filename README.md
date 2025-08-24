# 📱 Telegram Groups Inspector

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Platform](https://img.shields.io/badge/Platform-Cross--Platform-orange.svg)
![Status](https://img.shields.io/badge/Status-Active-brightgreen.svg)

*Advanced Telegram Groups Analysis and Management Tool*

[🇺🇸 English](#english) | [🇵🇱 Polski](#polski)

</div>

---

## 🇺🇸 English {#english}

### 📋 Overview

**Telegram Groups Inspector** is an advanced tool for comprehensive analysis and management of Telegram groups. Built with modern Python technologies, it provides powerful features for monitoring group activities, analyzing messages, downloading media, and managing user data with multi-threading capabilities.

### ✨ Key Features

- 🔍 **Group Scanning**: Deep analysis of group structure and metadata
- 👥 **User Analysis**: Comprehensive user activity monitoring and statistics
- 💬 **Message Analytics**: Advanced message pattern analysis and filtering
- 📁 **Media Downloader**: Bulk download of photos, videos, and documents
- ⚡ **Multi-threading**: Optimized concurrent processing for faster operations
- 🎨 **Rich UI**: Beautiful console interface with emoji support
- 📊 **Export Options**: Multiple output formats (JSON, CSV, TXT)
- 🔒 **Secure Configuration**: Protected API credentials management
- 📝 **Detailed Logging**: Comprehensive operation logging

### 🏗️ Project Structure

```
TelegramGroupsInspector/
├── 📁 src/                     # Source code directory
│   ├── 🐍 main.py              # Main application entry point
│   ├── 📁 config/              # Configuration management
│   │   ├── config.py           # Main configuration settings
│   │   ├── connection_config.py # Telegram API configuration
│   │   └── connection.json     # Connection parameters
│   ├── 📁 modules/             # Core functionality modules
│   │   ├── group_scanner.py    # Group analysis engine
│   │   ├── user_scanner.py     # User monitoring system
│   │   ├── message_analyzer.py # Message processing engine
│   │   └── media_downloader.py # Media download manager
│   ├── 📁 units/               # Utility components
│   │   ├── menu.py             # Interactive menu system
│   │   └── file_manager.py     # File operations manager
│   ├── 📁 utils/               # Advanced utilities
│   │   ├── async_processor.py  # Multi-threading manager
│   │   └── console_manager.py  # Console UI controller
│   ├── 📁 logs/                # Application logs
│   ├── 📁 outputs/             # Generated reports and data
│   └── 📁 sessions/            # Telegram session files
├── 📄 requirements.txt         # Python dependencies
├── 🐍 telegram_inspector.py    # Quick launch script
└── 📖 README.md               # This documentation
```

### 🛠️ Installation & Setup

#### Prerequisites
- Python 3.8 or higher
- Telegram API credentials (api_id, api_hash)
- Active Telegram account

#### Step 1: Clone Repository
```bash
git clone https://github.com/yourusername/TelegramGroupsInspector.git
cd TelegramGroupsInspector
```

#### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

#### Step 3: Configure API Credentials
1. Get your API credentials from [my.telegram.org](https://my.telegram.org)
2. Edit `src/config/config.py`:
```python
API_ID = "YOUR_API_ID_HERE"
API_HASH = "YOUR_API_HASH_HERE"
PHONE_NUMBER = "+1234567890"  # Your phone number
```

#### Step 4: Run Application
```bash
python telegram_inspector.py
```
or
```bash
python src/main.py
```

### 🎮 Usage Guide

#### Main Menu Navigation
The application features an intuitive emoji-enhanced menu system:

```
┌─ 🎯 TELEGRAM GROUPS INSPECTOR ─┐
│                                │
│  1️⃣  Group Scanner             │
│  2️⃣  User Analysis             │
│  3️⃣  Message Analyzer          │
│  4️⃣  Media Downloader          │
│  5️⃣  File Manager              │
│  6️⃣  Settings                  │
│  7️⃣  Exit                      │
│                                │
└────────────────────────────────┘
```

#### Core Functions

**1. Group Scanner** 🔍
- Scan group structure and metadata
- Extract member lists and permissions
- Analyze group statistics
- Export group information

**2. User Analysis** 👥
- Monitor user activity patterns
- Track message frequency
- Analyze user engagement
- Generate user reports

**3. Message Analyzer** 💬
- Filter messages by date, user, or content
- Analyze message patterns
- Extract specific message types
- Search and categorize content

**4. Media Downloader** 📁
- Bulk download photos and videos
- Organize media by date/user
- Custom download filters
- Progress tracking

### ⚙️ Configuration Options

#### Threading Configuration
```python
# In config.py
MAX_WORKERS = 4              # Maximum thread workers
BATCH_SIZE = 100             # Processing batch size
RATE_LIMIT_DELAY = 1.0       # API rate limiting
```

#### Output Settings
```python
OUTPUT_FORMATS = ['json', 'csv', 'txt']
AUTO_SAVE = True
TIMESTAMP_FILES = True
```

### 🔧 Advanced Features

#### Multi-threading Support
The application uses advanced async processing for optimal performance:
- **ThreadPoolManager**: CPU-intensive task management
- **AsyncTaskManager**: I/O operations optimization
- **Rate Limiting**: Automatic API throttling
- **Batch Processing**: Efficient data handling

#### Security Features
- Encrypted session storage
- Secure API credential management
- Local data processing (no external servers)
- Privacy-focused design

### 📊 Output Formats

#### JSON Export
```json
{
  "group_info": {
    "title": "Group Name",
    "members_count": 1500,
    "creation_date": "2024-01-01"
  },
  "users": [...],
  "messages": [...]
}
```

#### CSV Export
Structured data tables for analysis in spreadsheet applications.

#### TXT Reports
Human-readable reports with detailed analysis.

### 🐛 Troubleshooting

#### Common Issues

**1. API Errors**
```
Error: API_ID or API_HASH invalid
Solution: Verify credentials in config.py
```

**2. Session Issues**
```
Error: Session file corrupted
Solution: Delete session files and re-authenticate
```

**3. Permission Errors**
```
Error: Access denied to group
Solution: Ensure account is group member
```

### 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

### 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

### ⚠️ Disclaimer

This tool is for educational and legitimate use only. Users are responsible for complying with Telegram's Terms of Service and applicable laws. The developers are not responsible for misuse of this software.

---

## 🇵🇱 Polski {#polski}

### 📋 Przegląd

**Telegram Groups Inspector** to zaawansowane narzędzie do kompleksowej analizy i zarządzania grupami Telegram. Zbudowane z wykorzystaniem nowoczesnych technologii Python, zapewnia potężne funkcje do monitorowania aktywności grup, analizowania wiadomości, pobierania mediów i zarządzania danymi użytkowników z obsługą wielowątkowości.

### ✨ Kluczowe Funkcje

- 🔍 **Skanowanie Grup**: Głęboka analiza struktury grup i metadanych
- 👥 **Analiza Użytkowników**: Kompleksowe monitorowanie aktywności i statystyk użytkowników
- 💬 **Analityka Wiadomości**: Zaawansowana analiza wzorców wiadomości i filtrowanie
- 📁 **Pobieracz Mediów**: Masowe pobieranie zdjęć, filmów i dokumentów
- ⚡ **Wielowątkowość**: Zoptymalizowane przetwarzanie współbieżne dla szybszych operacji
- 🎨 **Bogaty Interfejs**: Piękny interfejs konsolowy z obsługą emoji
- 📊 **Opcje Eksportu**: Wiele formatów wyjściowych (JSON, CSV, TXT)
- 🔒 **Bezpieczna Konfiguracja**: Chronione zarządzanie danymi API
- 📝 **Szczegółowe Logowanie**: Kompleksowe logowanie operacji

### 🏗️ Struktura Projektu

```
TelegramGroupsInspector/
├── 📁 src/                     # Katalog kodu źródłowego
│   ├── 🐍 main.py              # Główny punkt wejścia aplikacji
│   ├── 📁 config/              # Zarządzanie konfiguracją
│   │   ├── config.py           # Główne ustawienia konfiguracji
│   │   ├── connection_config.py # Konfiguracja API Telegram
│   │   └── connection.json     # Parametry połączenia
│   ├── 📁 modules/             # Główne moduły funkcjonalności
│   │   ├── group_scanner.py    # Silnik analizy grup
│   │   ├── user_scanner.py     # System monitorowania użytkowników
│   │   ├── message_analyzer.py # Silnik przetwarzania wiadomości
│   │   └── media_downloader.py # Menedżer pobierania mediów
│   ├── 📁 units/               # Komponenty narzędziowe
│   │   ├── menu.py             # Interaktywny system menu
│   │   └── file_manager.py     # Menedżer operacji na plikach
│   ├── 📁 utils/               # Zaawansowane narzędzia
│   │   ├── async_processor.py  # Menedżer wielowątkowości
│   │   └── console_manager.py  # Kontroler interfejsu konsoli
│   ├── 📁 logs/                # Logi aplikacji
│   ├── 📁 outputs/             # Wygenerowane raporty i dane
│   └── 📁 sessions/            # Pliki sesji Telegram
├── 📄 requirements.txt         # Zależności Python
├── 🐍 telegram_inspector.py    # Skrypt szybkiego uruchomienia
└── 📖 README.md               # Ta dokumentacja
```

### 🛠️ Instalacja i Konfiguracja

#### Wymagania
- Python 3.8 lub nowszy
- Dane uwierzytelniające API Telegram (api_id, api_hash)
- Aktywne konto Telegram

#### Krok 1: Klonowanie Repozytorium
```bash
git clone https://github.com/twojeuzytkownik/TelegramGroupsInspector.git
cd TelegramGroupsInspector
```

#### Krok 2: Instalacja Zależności
```bash
pip install -r requirements.txt
```

#### Krok 3: Konfiguracja Danych API
1. Pobierz dane uwierzytelniające API z [my.telegram.org](https://my.telegram.org)
2. Edytuj `src/config/config.py`:
```python
API_ID = "TWOJE_API_ID_TUTAJ"
API_HASH = "TWÓJ_API_HASH_TUTAJ"
PHONE_NUMBER = "+48123456789"  # Twój numer telefonu
```

#### Krok 4: Uruchomienie Aplikacji
```bash
python telegram_inspector.py
```
lub
```bash
python src/main.py
```

### 🎮 Przewodnik Użytkowania

#### Nawigacja w Menu Głównym
Aplikacja oferuje intuicyjny system menu wzbogacony o emoji:

```
┌─ 🎯 TELEGRAM GROUPS INSPECTOR ─┐
│                                │
│  1️⃣  Skaner Grup               │
│  2️⃣  Analiza Użytkowników      │
│  3️⃣  Analizator Wiadomości     │
│  4️⃣  Pobieracz Mediów          │
│  5️⃣  Menedżer Plików           │
│  6️⃣  Ustawienia               │
│  7️⃣  Wyjście                   │
│                                │
└────────────────────────────────┘
```

#### Główne Funkcje

**1. Skaner Grup** 🔍
- Skanowanie struktury grup i metadanych
- Ekstraktowanie list członków i uprawnień
- Analiza statystyk grup
- Eksport informacji o grupach

**2. Analiza Użytkowników** 👥
- Monitorowanie wzorców aktywności użytkowników
- Śledzenie częstotliwości wiadomości
- Analiza zaangażowania użytkowników
- Generowanie raportów użytkowników

**3. Analizator Wiadomości** 💬
- Filtrowanie wiadomości według daty, użytkownika lub treści
- Analiza wzorców wiadomości
- Ekstraktowanie określonych typów wiadomości
- Wyszukiwanie i kategoryzowanie treści

**4. Pobieracz Mediów** 📁
- Masowe pobieranie zdjęć i filmów
- Organizowanie mediów według daty/użytkownika
- Niestandardowe filtry pobierania
- Śledzenie postępu

### ⚙️ Opcje Konfiguracji

#### Konfiguracja Wielowątkowości
```python
# W config.py
MAX_WORKERS = 4              # Maksymalna liczba wątków roboczych
BATCH_SIZE = 100             # Rozmiar partii przetwarzania
RATE_LIMIT_DELAY = 1.0       # Ograniczenie szybkości API
```

#### Ustawienia Wyjścia
```python
OUTPUT_FORMATS = ['json', 'csv', 'txt']
AUTO_SAVE = True
TIMESTAMP_FILES = True
```

### 🔧 Zaawansowane Funkcje

#### Obsługa Wielowątkowości
Aplikacja wykorzystuje zaawansowane przetwarzanie asynchroniczne dla optymalnej wydajności:
- **ThreadPoolManager**: Zarządzanie zadaniami intensywnymi CPU
- **AsyncTaskManager**: Optymalizacja operacji I/O
- **Ograniczanie Szybkości**: Automatyczne ograniczanie API
- **Przetwarzanie Wsadowe**: Efektywne przetwarzanie danych

#### Funkcje Bezpieczeństwa
- Szyfrowane przechowywanie sesji
- Bezpieczne zarządzanie danymi uwierzytelniającymi API
- Lokalne przetwarzanie danych (brak zewnętrznych serwerów)
- Projektowanie zorientowane na prywatność

### 📊 Formaty Wyjściowe

#### Eksport JSON
```json
{
  "group_info": {
    "title": "Nazwa Grupy",
    "members_count": 1500,
    "creation_date": "2024-01-01"
  },
  "users": [...],
  "messages": [...]
}
```

#### Eksport CSV
Strukturalne tabele danych do analizy w aplikacjach arkuszy kalkulacyjnych.

#### Raporty TXT
Czytelne dla człowieka raporty ze szczegółową analizą.

### 🐛 Rozwiązywanie Problemów

#### Częste Problemy

**1. Błędy API**
```
Błąd: API_ID lub API_HASH nieprawidłowe
Rozwiązanie: Sprawdź dane uwierzytelniające w config.py
```

**2. Problemy z Sesją**
```
Błąd: Plik sesji uszkodzony
Rozwiązanie: Usuń pliki sesji i uwierzytelnij ponownie
```

**3. Błędy Uprawnień**
```
Błąd: Odmowa dostępu do grupy
Rozwiązanie: Upewnij się, że konto jest członkiem grupy
```

### 🤝 Współpraca

1. Forkuj repozytorium
2. Utwórz gałąź funkcji (`git checkout -b feature/NiezwyklaFunkcja`)
3. Zatwierdź zmiany (`git commit -m 'Dodaj NiezwyklaFunkcja'`)
4. Wypchnij do gałęzi (`git push origin feature/NiezwyklaFunkcja`)
5. Otwórz Pull Request

### 📄 Licencja

Ten projekt jest licencjonowany na licencji MIT - szczegóły w pliku LICENSE.

### ⚠️ Zastrzeżenie

To narzędzie jest przeznaczone wyłącznie do celów edukacyjnych i legalnego użytku. Użytkownicy są odpowiedzialni za przestrzeganie Warunków Korzystania z Telegram i obowiązującego prawa. Deweloperzy nie ponoszą odpowiedzialności za nadużycie tego oprogramowania.

---

<div align="center">

**🚀 Made with ❤️ by MXC-Projects**

[![GitHub](https://img.shields.io/badge/GitHub-Repository-black.svg)](https://github.com/yourusername/TelegramGroupsInspector)
[![Issues](https://img.shields.io/badge/Issues-Welcome-brightgreen.svg)](https://github.com/yourusername/TelegramGroupsInspector/issues)
[![Pull Requests](https://img.shields.io/badge/Pull%20Requests-Welcome-brightgreen.svg)](https://github.com/yourusername/TelegramGroupsInspector/pulls)

</div>
