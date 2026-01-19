#!/usr/bin/env python3
"""
Скрипт для проверки работы андервольта DeckTune.
Проверяет:
1. Доступность ryzenadj binary
2. Права sudo
3. Применение тестовых значений
4. Wizard mode конфигурацию
"""

import os
import sys
import subprocess
import json

# Добавляем путь к плагину
PLUGIN_DIR = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, PLUGIN_DIR)

from backend.core.ryzenadj import RyzenadjWrapper
from backend.platform.detect import detect_platform

# Цвета для вывода
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_header(text):
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}{text:^60}{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")

def print_success(text):
    print(f"{GREEN}✓ {text}{RESET}")

def print_error(text):
    print(f"{RED}✗ {text}{RESET}")

def print_warning(text):
    print(f"{YELLOW}⚠ {text}{RESET}")

def print_info(text):
    print(f"  {text}")

def check_ryzenadj_binary():
    """Проверка наличия ryzenadj binary."""
    print_header("Проверка 1: Наличие ryzenadj binary")
    
    ryzenadj_path = os.path.join(PLUGIN_DIR, "bin", "ryzenadj")
    
    if not os.path.exists(ryzenadj_path):
        print_error(f"ryzenadj не найден: {ryzenadj_path}")
        return False
    
    print_success(f"ryzenadj найден: {ryzenadj_path}")
    
    if not os.access(ryzenadj_path, os.X_OK):
        print_error("ryzenadj не имеет прав на выполнение")
        return False
    
    print_success("ryzenadj имеет права на выполнение")
    return True

def check_sudo():
    """Проверка доступности sudo."""
    print_header("Проверка 2: Доступность sudo")
    
    try:
        result = subprocess.run(
            ["sudo", "-n", "true"],
            capture_output=True,
            timeout=5
        )
        
        if result.returncode == 0:
            print_success("sudo доступен без пароля (NOPASSWD настроен)")
            return True
        else:
            print_warning("sudo требует пароль")
            print_info("Для работы плагина нужно настроить NOPASSWD для ryzenadj")
            return False
    except subprocess.TimeoutExpired:
        print_error("Таймаут при проверке sudo")
        return False
    except FileNotFoundError:
        print_error("sudo не найден в системе")
        return False

def test_ryzenadj_info():
    """Тест команды ryzenadj --info."""
    print_header("Проверка 3: Тест ryzenadj --info")
    
    ryzenadj_path = os.path.join(PLUGIN_DIR, "bin", "ryzenadj")
    
    try:
        result = subprocess.run(
            ["sudo", ryzenadj_path, "--info"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            print_success("ryzenadj --info выполнен успешно")
            print_info("Вывод (первые 5 строк):")
            lines = result.stdout.strip().split('\n')[:5]
            for line in lines:
                print_info(f"  {line}")
            return True
        else:
            print_error(f"ryzenadj --info завершился с ошибкой (код {result.returncode})")
            if result.stderr:
                print_info(f"Ошибка: {result.stderr.strip()}")
            return False
    except subprocess.TimeoutExpired:
        print_error("Таймаут при выполнении ryzenadj --info")
        return False
    except Exception as e:
        print_error(f"Ошибка при выполнении ryzenadj --info: {e}")
        return False

def test_platform_detection():
    """Тест определения платформы."""
    print_header("Проверка 4: Определение платформы")
    
    try:
        platform = detect_platform()
        print_success(f"Платформа определена: {platform.model}")
        print_info(f"Вариант: {platform.variant}")
        print_info(f"Безопасный лимит: {platform.safe_limit}mV")
        print_info(f"Экспертный лимит: {platform.expert_limit}mV")
        return True
    except Exception as e:
        print_error(f"Ошибка при определении платформы: {e}")
        return False

def test_hex_calculation():
    """Тест расчета hex значений."""
    print_header("Проверка 5: Расчет hex значений")
    
    test_cases = [
        (0, -30, "0XFFFE2"),
        (1, -30, "0X1FFFE2"),
        (2, -25, "0X2FFFE7"),
        (3, -20, "0X3FFFEC"),
    ]
    
    all_passed = True
    for core, value, expected in test_cases:
        result = RyzenadjWrapper.calculate_hex(core, value)
        if result == expected:
            print_success(f"Core {core}, {value}mV → {result}")
        else:
            print_error(f"Core {core}, {value}mV → {result} (ожидалось {expected})")
            all_passed = False
    
    return all_passed

def test_apply_safe_values():
    """Тест применения безопасных значений."""
    print_header("Проверка 6: Применение безопасных значений")
    
    ryzenadj_path = os.path.join(PLUGIN_DIR, "bin", "ryzenadj")
    wrapper = RyzenadjWrapper(ryzenadj_path, PLUGIN_DIR)
    
    # Применяем очень консервативные значения
    test_values = [-10, -10, -10, -10]
    
    print_info(f"Применяем тестовые значения: {test_values}")
    print_warning("Это безопасные значения, но если система зависнет - перезагрузитесь")
    
    response = input(f"\n{YELLOW}Продолжить? (y/n): {RESET}").strip().lower()
    if response != 'y':
        print_warning("Тест пропущен пользователем")
        return None
    
    success, error = wrapper.apply_values(test_values)
    
    if success:
        print_success("Значения применены успешно!")
        print_info("Команды, которые были выполнены:")
        for cmd in wrapper.get_last_commands():
            print_info(f"  {cmd}")
        
        # Сбрасываем значения обратно в 0
        print_info("\nСбрасываем значения обратно в 0...")
        success_reset, error_reset = wrapper.disable()
        if success_reset:
            print_success("Значения сброшены в 0")
        else:
            print_error(f"Ошибка при сбросе: {error_reset}")
        
        return True
    else:
        print_error(f"Ошибка при применении значений: {error}")
        return False

def check_wizard_mode_config():
    """Проверка конфигурации Wizard Mode."""
    print_header("Проверка 7: Конфигурация Wizard Mode")
    
    # Проверяем наличие gymdeck3
    gymdeck3_path = os.path.join(PLUGIN_DIR, "bin", "gymdeck3")
    
    if os.path.exists(gymdeck3_path):
        print_success(f"gymdeck3 найден: {gymdeck3_path}")
        
        if os.access(gymdeck3_path, os.X_OK):
            print_success("gymdeck3 имеет права на выполнение")
        else:
            print_error("gymdeck3 не имеет прав на выполнение")
            return False
    else:
        print_error(f"gymdeck3 не найден: {gymdeck3_path}")
        return False
    
    # Проверяем наличие frontend файлов
    src_path = os.path.join(PLUGIN_DIR, "src")
    if os.path.exists(src_path):
        print_success(f"Frontend директория найдена: {src_path}")
    else:
        print_warning(f"Frontend директория не найдена: {src_path}")
    
    return True

def main():
    """Основная функция."""
    print(f"\n{BLUE}{'='*60}")
    print(f"  DeckTune - Диагностика работы андервольта")
    print(f"{'='*60}{RESET}\n")
    
    results = {
        "ryzenadj_binary": check_ryzenadj_binary(),
        "sudo": check_sudo(),
        "ryzenadj_info": test_ryzenadj_info(),
        "platform": test_platform_detection(),
        "hex_calc": test_hex_calculation(),
        "wizard_config": check_wizard_mode_config(),
    }
    
    # Тест применения значений (опциональный)
    apply_result = test_apply_safe_values()
    if apply_result is not None:
        results["apply_values"] = apply_result
    
    # Итоговый отчет
    print_header("ИТОГОВЫЙ ОТЧЕТ")
    
    passed = sum(1 for v in results.values() if v is True)
    failed = sum(1 for v in results.values() if v is False)
    total = len(results)
    
    for test_name, result in results.items():
        if result is True:
            print_success(f"{test_name}: PASSED")
        elif result is False:
            print_error(f"{test_name}: FAILED")
        else:
            print_warning(f"{test_name}: SKIPPED")
    
    print(f"\n{BLUE}Результат: {passed}/{total} тестов пройдено{RESET}")
    
    if failed > 0:
        print(f"\n{RED}Обнаружены проблемы. Проверьте вывод выше.{RESET}")
        return 1
    else:
        print(f"\n{GREEN}Все проверки пройдены успешно!{RESET}")
        return 0

if __name__ == "__main__":
    sys.exit(main())
