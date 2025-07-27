# Plume Testnet

## EN:

An automated tool for interacting with the Plume Testnet, designed to bridge assets from supported networks (Base, Arbitrum, Optimism) to Plume, perform swaps to achieve a target transaction count, and withdraw assets from Plume.

### Main Features

The software automates the following tasks on the Plume Testnet:

- Bridging assets from Base, Arbitrum, or Optimism to Plume
- Performing swaps on Plume to reach a target of 400 transactions
- Withdrawing assets from Plume to a specified address or the same wallet
- Support for multiple wallets
- Asynchronous processing for efficient handling of multiple accounts
- Proxy management with automatic replacement on errors
- Configurable delays between actions
- Detailed logging and error handling
- Database integration for wallet management
- Random selection of source network for bridging based on balance

### Installation

#### Windows
```bash
py -3.11 -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

#### Linux/MacOS
```bash
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

### How to Use

#### First Run
Run `main.py` to create the `files/` directory and initialize necessary files:
```bash
python main.py
```

#### Pre-Run Setup
- Add private keys to `files/private.txt` (one key per line).
- Add proxies to `files/proxy.txt` in the format: `http://log:pass@ip:port` or `log:pass@ip:port`.
- For withdrawals to a different address, add withdrawal addresses to `files/withdraw_address.txt` (one address per line, corresponding to the private keys).
- Configure settings in `files/settings.json`.

### Settings.json
Settings support randomization. Use min/max ranges for random values:

#### General Settings
- `wallet_startup_delay` - Delay range between wallet startups (seconds, e.g., `{"min": 5, "max": 10}`).
- `wallet_range` - Range of wallets to process (e.g., `{"start": 0, "end": 0}`; `end: 0` processes all wallets).
- `resource_settings.auto_replace` - Enable/disable automatic proxy replacement on errors (true/false).
- `resource_settings.max_failures` - Maximum allowed proxy failures before replacement.
- `bridge_settings` - Enable/disable specific networks for bridging (e.g., `{"use_base": true, "use_arbitrum": true, "use_optimism": false}`).
- `wallet_transactins_delay` - Delay range between swap transactions (seconds, e.g., `{"min": 10, "max": 30}`).
- `use_withdraw_address` - Use addresses from `withdraw_address.txt` for withdrawals (true) or withdraw to the same wallet (false).

### Available Options
1. **Import Wallets to Database**  
   Imports wallets from `private.txt` to the database. Required before starting operations.

2. **Run All Tasks (Main Process)**  
   Executes bridging and swap tasks for all wallets, targeting 400 transactions per wallet.

3. **Bridge Assets to Plume**  
   Bridges assets from a supported network (Base, Arbitrum, or Optimism) to Plume for selected wallets.

4. **Perform Swaps on Plume**  
   Executes swaps on Plume until the wallet reaches 400 transactions.

5. **Withdraw Assets from Plume**  
   Unwraps assets and bridges them from Plume to the address specified in `withdraw_address.txt` (if `use_withdraw_address` is true) or to the same wallet (if false).

6. **Exit**  
   Terminates the program.

### Software Workflow
1. Loads wallets, proxies, and withdrawal addresses from files.
2. Initializes clients with random user agents and proxies.
3. Checks Plume balance; skips bridging if balance exceeds 5 ETH.
4. Selects a random source network (Base, Arbitrum, or Optimism) with a minimum balance of 0.0008 ETH for bridging.
5. Bridges 95% of the available balance to Plume and waits for confirmation.
6. Performs swaps on Plume until 400 transactions are reached.
7. For withdrawal, unwraps assets and bridges 99% of the Plume balance to the specified address (or same wallet if `use_withdraw_address` is false), waiting 120-180 seconds for confirmation.
8. Handles proxy errors with automatic replacement (if enabled).
9. Logs results and errors to the console and database.

### Onchain Module Functions
- **Bridge**: Bridges assets from Base, Arbitrum, or Optimism to Plume if the source network has at least 0.0008 ETH.
- **Swap**: Performs swaps on Plume until the wallet reaches 400 transactions.
- **Withdraw**: Unwraps assets and bridges them from Plume to the specified address or same wallet.

### Requirements
- Python 3.11+
- Active ETH wallets (private keys)
- Proxies (optional but recommended)
- Installed dependencies from `requirements.txt`
- Minimum balance of 0.0008 ETH in at least one supported network (Base, Arbitrum, or Optimism) for bridging
- Withdrawal addresses in `files/withdraw_address.txt` for withdrawal operations if `use_withdraw_address` is true

### Notes
- The software operates on the Plume Testnet and supports bridging from Base, Arbitrum, and Optimism.
- Ensure proxies are reliable to avoid frequent errors.
- The database stores wallet and proxy information for efficient management.
- Random delays are applied to avoid detection and rate-limiting.
- Swaps continue until 400 transactions are achieved per wallet.
- Withdrawal requires a Plume balance greater than 5 ETH and, if `use_withdraw_address` is true, a valid address in `withdraw_address.txt`.

## RU:

# Plume Testnet

Автоматизированный инструмент для взаимодействия с тестовой сетью Plume, предназначенный для переброски активов из поддерживаемых сетей (Base, Arbitrum, Optimism) в Plume, выполнения свопов для достижения целевого количества транзакций и вывода активов из Plume.

### Основные функции

Программа автоматизирует следующие задачи в тестовой сети Plume:

- Переброска активов из Base, Arbitrum или Optimism в Plume
- Выполнение свопов в Plume для достижения 400 транзакций
- Вывод активов из Plume на указанный адрес или тот же кошелек
- Поддержка нескольких кошельков
- Асинхронная обработка для эффективной работы с множеством аккаунтов
- Управление прокси с автоматической заменой при ошибках
- Настраиваемые задержки между действиями
- Подробное логирование и обработка ошибок
- Интеграция с базой данных для управления кошельками
- Случайный выбор исходной сети для переброски на основе баланса

### Установка

#### Windows
```bash
py -3.11 -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

#### Linux/MacOS
```bash
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

### Как использовать

#### Первый запуск
Запустите `main.py`, чтобы создать директорию `files/` и инициализировать необходимые файлы:
```bash
python main.py
```

#### Настройка перед запуском
- Добавьте приватные ключи в `files/private.txt` (по одному ключу на строку).
- Добавьте прокси в `files/proxy.txt` в формате: `http://log:pass@ip:port` или `log:pass@ip:port`.
- Для вывода на другой адрес добавьте адреса для вывода в `files/withdraw_address.txt` (по одному адресу на строку, соответствующему приватным ключам).
- Настройте параметры в `files/settings.json`.

### Settings.json
Настройки поддерживают рандомизацию. Используйте диапазоны min/max для случайных значений:

#### Общие настройки
- `wallet_startup_delay` - Диапазон задержек между запусками кошельков (в секундах, например, `{"min": 5, "max": 10}`).
- `wallet_range` - Диапазон кошельков для обработки (например, `{"start": 0, "end": 0}`; `end: 0` обрабатывает все кошельки).
- `resource_settings.auto_replace` - Включение/отключение автоматической замены прокси при ошибках (true/false).
- `resource_settings.max_failures` - Максимальное количество ошибок прокси перед заменой.
- `bridge_settings` - Включение/отключение определенных сетей для переброски (например, `{"use_base": true, "use_arbitrum": true, "use_optimism": false}`).
- `wallet_transactins_delay` - Диапазон задержек между транзакциями свопов (в секундах, например, `{"min": 10, "max": 30}`).
- `use_withdraw_address` - Использовать адреса из `withdraw_address.txt` для вывода (true) или выводить на тот же кошелек (false).

### Доступные опции
1. **Импорт кошельков в базу данных**  
   Импортирует кошельки из `private.txt` в базу данных. Необходимо выполнить перед началом работы.

2. **Выполнение всех задач (основной процесс)**  
   Выполняет задачи переброски и свопов для всех кошельков, нацеленных на 400 транзакций на кошелек.

3. **Переброска активов в Plume**  
   Перебрасывает активы из поддерживаемой сети (Base, Arbitrum или Optimism) в Plume для выбранных кошельков.

4. **Выполнение свопов в Plume**  
   Выполняет свопы в Plume, пока кошелек не достигнет 400 транзакций.

5. **Вывод активов из Plume**  
   Разворачивает активы и перебрасывает их из Plume на адрес, указанный в `withdraw_address.txt` (если `use_withdraw_address` равно true) или на тот же кошелек (если false).

6. **Выход**  
   Завершает работу программы.

### Рабочий процесс программы
1. Загружает кошельки, прокси и адреса для вывода из файлов.
2. Инициализирует клиенты с случайными пользовательскими агентами и прокси.
3. Проверяет баланс в Plume; пропускает переброску, если баланс превышает 5 ETH.
4. Выбирает случайную исходную сеть (Base, Arbitrum или Optimism) с минимальным балансом 0.0008 ETH для переброски.
5. Перебрасывает 95% доступного баланса в Plume и ожидает подтверждения.
6. Выполняет свопы в Plume до достижения 400 транзакций.
7. Для вывода разворачивает активы и перебрасывает 99% баланса Plume на указанный адрес (или тот же кошелек, если `use_withdraw_address` равно false), ожидая 120-180 секунд для подтверждения.
8. Обрабатывает ошибки прокси с автоматической заменой (если включено).
9. Логирует результаты и ошибки в консоль и базу данных.

### Функции ончейн-модуля
- **Переброска**: Перебрасывает активы из Base, Arbitrum или Optimism в Plume, если в исходной сети есть минимум 0.0008 ETH.
- **Свопы**: Выполняет свапы в Plume, пока кошелек не достигнет 400 транзакций.
- **Вывод**: Разворачивает активы и перебрасывает их из Plume на указанный адрес или тот же кошелек.

### Требования
- Python 3.11+
- Активные кошельки ETH (приватные ключи)
- Прокси (опционально, но рекомендуется)
- Установленные зависимости из `requirements.txt`
- Минимальный баланс 0.0008 ETH в одной из поддерживаемых сетей (Base, Arbitrum или Optimism) для переброски
- Адреса для вывода в `files/withdraw_address.txt`, если `use_withdraw_address` равно true

### Примечания
- Программа работает в тестовой сети Plume и поддерживает переброску из Base, Arbitrum и Optimism.
- Убедитесь, что прокси надежны, чтобы избежать частых ошибок.
- База данных хранит информацию о кошельках и прокси для эффективного управления.
- Случайные задержки применяются для избежания обнаружения и ограничений по скорости.
- Свопы продолжаются до достижения 400 транзакций на кошелек.
- Для вывода требуется баланс Plume более 5 ETH и, если `use_withdraw_address` равно true, действительный адрес в `withdraw_address.txt`.
