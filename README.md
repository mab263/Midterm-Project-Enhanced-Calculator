# Enhanced Calculator

A command-line calculator written in Python. It has a REPL interface, ten arithmetic operations, undo/redo, automatic logging and history saving, dynamic help menu, color coded outputs, and a configuration system based on environment variables. It is built around several design patterns and has a full pytest suite with enforced coverage.

## 🔢 Features

- **Ten operations:** add, subtract, multiply, divide, power, root, modulus, int_divide, percent, abs_diff
- **REPL interface** with commands: history, clear, undo, redo, save, load, help, exit
- **Undo and redo** of calculations
- **History saved to CSV** with pandas, loaded automatically at startup
- **Logging** of every calculation, warning, and error to a log file
- **Configuration** through a `.env` file, with defaults for every setting
- **Input validation and error handling** with custom exceptions
- **Dynamic help menu** built automatically from the registered operations and commands
- **Color-coded output** (results green, errors red, hints yellow, headings cyan)

## 🎨 Design Patterns

| Pattern | Where it is used |
|---|---|
| Factory | `OperationFactory` creates an operation from its command name |
| Strategy | Each operation is an interchangeable `Operation` class |
| Observer | `LoggingObserver` and `AutoSaveObserver` react to each new calculation |
| Memento | `CalculatorMemento` and `UndoRedoManager` provide undo and redo |
| Facade | `Calculator` puts config, logging, validation, operations, history, and undo/redo behind one interface |
| Decorator | `@OperationFactory.register` and `@command` register operations and commands, and the help menu is built from them |

## 🗂️ Project Structure

```
app/
├── calculator_repl.py     # REPL and commands
├── calculator.py          # Calculator facade
├── calculation.py         # Calculation record
├── calculator_config.py   # Settings from .env
├── calculator_memento.py  # Undo/redo snapshots
├── exceptions.py          # Custom exceptions
├── history.py             # CSV save/load and observers
├── input_validators.py    # Input validation
├── logger.py              # Logging
├── operations.py          # Operations and factory
└── output.py              # Color-coded output
tests/                     # pytest test suite
main.py                    # Entry point
```

## 🖥️ Installation

Requires Python 3.10 or newer.

```bash
git clone git@github.com:mab263/Midterm-Project-Enhanced-Calculator.git
cd Midterm-Project-Enhanced-Calculator
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate.bat
python -m pip install -r requirements.txt
```

## 🛠️ Configuration

Copy the template and edit it if you want different settings:

```bash
cp .env.example .env
```

Every setting has a default, so the calculator also runs without a `.env` file.

| Variable | Default | Meaning |
|---|---|---|
| `CALCULATOR_LOG_DIR` | `logs` in the project folder | Directory for log files |
| `CALCULATOR_HISTORY_DIR` | `history` in the project folder | Directory for history files |
| `CALCULATOR_LOG_FILE` | `calculator.log` | Log file name inside the log directory |
| `CALCULATOR_HISTORY_FILE` | `calculator_history.csv` | History file name inside the history directory |
| `CALCULATOR_MAX_HISTORY_SIZE` | `100` | Maximum number of history entries |
| `CALCULATOR_AUTO_SAVE` | `true` | Save history automatically after each calculation |
| `CALCULATOR_PRECISION` | `10` | Decimal places kept in results |
| `CALCULATOR_MAX_INPUT_VALUE` | `1000000` | Largest number accepted as input |
| `CALCULATOR_DEFAULT_ENCODING` | `utf-8` | Encoding for the log and history files |

Invalid values (such as `CALCULATOR_PRECISION=abc` or a history size of 0) stop the program at startup with a clear message.

## 📁 Logging

Calculations are logged at INFO level, recoverable problems (such as a history file that could not be loaded) at WARNING, and failed operations at ERROR. Lines look like this:

```
2026-10-25 12:00:00,000 - INFO - Calculation performed: operation=Addition, operand1=2, operand2=3, result=5
```

The log file is `logs/calculator.log` unless you change `CALCULATOR_LOG_DIR` or `CALCULATOR_LOG_FILE`.

## 👨🏻‍💻 Usage

```bash
python main.py
```

Give an operation and two numbers on one line, or type just the operation and you will be prompted for the numbers:

```
Enter command: add 2 3
Result: 5

Enter command: divide
Enter two numbers (or 'cancel' to abort):
First number: 10
Second number: 4
Result: 2.5

Enter command: undo
Operation undone
```

### ⚙️ Operations

| Command | Description |
|---|---|
| `add` | Add two numbers |
| `subtract` | Subtract the second number from the first |
| `multiply` | Multiply two numbers |
| `divide` | Divide the first number by the second |
| `power` | Raise the first number to the power of the second |
| `root` | Take the nth root of the first number (n is the second) |
| `modulus` | Remainder of dividing the first number by the second |
| `int_divide` | Divide and discard the fractional part |
| `percent` | First number as a percentage of the second |
| `abs_diff` | Absolute difference between the two numbers |

### 🤖 Other commands

| Command | Description |
|---|---|
| `history` | Show calculation history |
| `clear` | Clear calculation history |
| `undo` | Undo the last calculation |
| `redo` | Redo the last undone calculation |
| `save` | Save history to the CSV file |
| `load` | Load history from the CSV file |
| `help` | Show the help menu |
| `exit` | Exit the calculator |

Invalid input, division by zero, and other errors print a message and the calculator keeps running. Set `NO_COLOR=1` to turn colors off.

## 📝 Testing

```bash
pytest
```

This runs the whole suite and prints a coverage report. The run fails if coverage drops below 90%. An HTML report is written to `htmlcov/`.

## 🔎 Continuous Integration

A GitHub Actions workflow (`.github/workflows/python-app.yml`) runs on every push and pull request to `main`. It installs the dependencies from `requirements.txt`, runs the tests with coverage, and fails the build if coverage is below 90%.
