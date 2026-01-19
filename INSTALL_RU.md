# Инструкция по установке DeckTune v3.1.26

## Быстрая установка

### Вариант 1: Автоматическая установка (рекомендуется)

```bash
curl -L https://github.com/bobberdolle1/DeckTune/releases/latest/download/install.sh | sh
```

### Вариант 2: Ручная установка из ZIP

1. **Скачайте релиз**
   - Перейдите на https://github.com/bobberdolle1/DeckTune/releases
   - Скачайте `DeckTune-v3.1.26.zip`

2. **Перенесите на Steam Deck**
   - Скопируйте zip файл на Steam Deck любым удобным способом

3. **Включите Developer Mode в Decky Loader**
   - Откройте Decky Loader (кнопка ... в Quick Access Menu)
   - Перейдите в Settings → Developer
   - Включите "Developer Mode"

4. **Установите плагин**
   - В Decky Loader нажмите на иконку магазина
   - Выберите "Install from zip"
   - Выберите скачанный `DeckTune-v3.1.26.zip`
   - Дождитесь завершения установки

5. **Готово!**
   - Плагин появится в Quick Access Menu
   - Откройте DeckTune и начните использовать

## Что нового в v3.1.26

### Система управления настройками

- **Header Bar** — компактная навигация с иконками (Fan Control, Settings)
- **Settings Menu** — централизованное меню настроек с подтверждением Expert Mode
- **Apply on Startup** — автоматическое применение последнего профиля при загрузке
- **Game Only Mode** — андервольт только во время игр, сброс в меню Steam
- **Persistent Settings** — все настройки сохраняются между перезагрузками

### Как использовать новые функции

#### Apply on Startup (Применение при запуске)
1. Откройте Expert Mode → Manual tab
2. Включите "Apply on Startup"
3. Ваш последний профиль будет автоматически применяться при каждой загрузке Steam Deck

#### Game Only Mode (Только в играх)
1. Откройте Expert Mode → Manual tab
2. Включите "Game Only Mode"
3. Андервольт будет применяться только когда вы запускаете игру
4. При выходе в меню Steam андервольт автоматически сбрасывается в 0

#### Settings Menu (Меню настроек)
1. Нажмите на иконку ⚙️ в верхней части интерфейса
2. Включите/выключите Expert Mode (требуется подтверждение)
3. Все изменения сохраняются автоматически

## Требования

- Steam Deck (LCD или OLED)
- [Decky Loader](https://decky.xyz/) установлен
- SteamOS

## Поддержка

Если возникли проблемы:
1. Проверьте логи: `journalctl -u plugin.loader -f`
2. Откройте issue на GitHub: https://github.com/bobberdolle1/DeckTune/issues
3. Приложите логи и описание проблемы

## Безопасность

DeckTune включает многоуровневую систему защиты:
- Автоматические лимиты для каждой модели
- Watchdog с автоматическим откатом при зависании
- Boot Recovery для восстановления после сбоев
- Кнопка Panic Disable для мгновенного сброса

## Лицензия

GPL-3.0 License — см. [LICENSE](LICENSE)
