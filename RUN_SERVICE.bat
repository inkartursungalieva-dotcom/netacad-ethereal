@echo off
setlocal enabledelayedexpansion

title [NetAcad Ethereal] - Запуск сервиса
echo ======================================================
echo          NetAcad Ethereal - Сервис Запуска
echo ======================================================
echo.

:: Проверка наличия Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python не найден! Пожалуйста, установите Python 3.x
    echo Скачать: https://www.python.org/downloads/
    pause
    exit /b 1
)

:: Настройка виртуального окружения
if not exist ".venv" (
    echo [INFO] Создание виртуального окружения (в первый раз)...
    python -m venv .venv
    if %errorlevel% neq 0 (
        echo [ERROR] Не удалось создать .venv!
        pause
        exit /b 1
    )
)

:: Активация окружения и установка библиотек
echo [INFO] Активация виртуального окружения...
call .venv\Scripts\activate

:: Проверка, установлены ли уже библиотеки
pip show django >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] Установка библиотек (это может занять время)...
    python -m pip install --upgrade pip >nul 2>&1
    pip install -r requirements.txt --quiet
    if %errorlevel% neq 0 (
        echo [ERROR] Ошибка при установке библиотек! Проверьте интернет-соединение.
        pause
        exit /b 1
    )
) else (
    echo [INFO] Библиотеки уже установлены. Пропускаем установку.
)

echo [INFO] Подготовка к запуску...
echo.

:: Запуск основного скрипта
python start_app.py

:: Остановка сервера
echo.
echo [INFO] Сервер остановлен.
pause
