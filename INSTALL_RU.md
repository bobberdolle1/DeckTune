# Установка DeckTune

## Быстрая установка

```bash
curl -L https://github.com/bobberdolle1/DeckTune/releases/latest/download/install.sh | sh
```

## Ручная установка

1. Скачайте `DeckTune-v3.3.4.zip` из [Releases](https://github.com/bobberdolle1/DeckTune/releases)
2. Перенесите на Steam Deck
3. В Decky Loader: Settings → Developer → Enable "Developer Mode"
4. Decky Loader → Install from zip → Выберите скачанный файл
5. Готово! Плагин появится в Quick Access Menu

## Требования

- Steam Deck (LCD или OLED)
- [Decky Loader](https://decky.xyz/)
- SteamOS

## Первый запуск

1. Откройте DeckTune в Quick Access Menu (кнопка ...)
2. Выберите режим:
   - **Wizard Mode** — автоматический поиск оптимальных значений
   - **Expert Mode** — ручная настройка для опытных пользователей
3. Следуйте инструкциям на экране

## Основные функции

### Apply on Startup
Автоматическое применение последнего профиля при загрузке Steam Deck.

**Как включить:**
1. Settings (⚙️) → Apply on Startup → ON
2. Ваш профиль будет применяться автоматически при каждой загрузке

### Game Only Mode
Андервольт только во время игр, сброс в меню Steam.

**Как включить:**
1. Settings (⚙️) → Game Only Mode → ON
2. Андервольт применяется при запуске игры
3. Автоматический сброс при выходе в меню

### Expert Mode
Расширенные настройки с подтверждением безопасности.

**Как включить:**
1. Settings (⚙️) → Expert Mode → ON
2. Подтвердите предупреждение о рисках
3. Получите доступ к ручной настройке по ядрам

## Безопасность

- **Panic Disable** — красная кнопка мгновенно сбрасывает все значения в 0
- **Watchdog** — автоматический откат при зависании (30s таймаут)
- **Boot Recovery** — восстановление после сбоя при загрузке
- **LKG** — сохранение последних стабильных значений

## Поддержка

**Проблемы при установке:**
1. Проверьте логи: `journalctl -u plugin.loader -f`
2. Откройте issue: https://github.com/bobberdolle1/DeckTune/issues
3. Приложите логи и описание проблемы

**Частые вопросы:**
- Плагин не загружается → Проверьте версию Decky Loader (требуется последняя)
- Значения не применяются → Проверьте права доступа к ryzenadj
- Система зависает → Используйте Panic Disable, уменьшите значения

## Лицензия

GPL-3.0 — см. [LICENSE](LICENSE)
