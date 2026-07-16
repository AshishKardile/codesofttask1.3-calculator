// Calculator State
let currentValue = '0';
let previousValue = null;
let activeOperation = null;
let memoryRegister = 0;
let resetOnNextInput = false;

// DOM Elements
const displayEl = document.getElementById('display-value');
const memoryIndicatorEl = document.getElementById('memory-indicator');
const lcdScreenEl = document.getElementById('lcd-screen');

// Number of digits limits to avoid LCD overflow
const MAX_DIGITS = 10;

// Initialize Display
updateDisplay();

// Register Click Event Listeners for Keyboard Buttons
document.querySelectorAll('.btn').forEach(button => {
  button.addEventListener('click', () => {
    const key = button.getAttribute('data-key');
    handleInput(key);
    triggerButtonVisualFeedback(button);
  });
});

// Register Keyboard Event Listeners for Physical Keyboards
window.addEventListener('keydown', (e) => {
  let key = e.key;

  // Normalize keyboard keys to data-key values
  if (key === 'Enter') key = '=';
  if (key === 'Escape') key = 'CE/C';
  if (key === 'c' || key === 'C') key = 'CE/C';
  if (key === 'Backspace') key = 'Backspace';
  if (key === 'r' || key === 'R') key = 'sqrt';
  if (key === 'm' || key === 'M') key = 'MU';

  // Check if it's a valid key
  const button = document.querySelector(`.btn[data-key="${key}"]`);
  if (button) {
    e.preventDefault();
    button.classList.add('active');
    handleInput(key);
  } else if (key === 'Backspace') {
    e.preventDefault();
    handleBackspace();
  }
});

window.addEventListener('keyup', (e) => {
  let key = e.key;
  if (key === 'Enter') key = '=';
  if (key === 'Escape' || key === 'c' || key === 'C') key = 'CE/C';
  if (key === 'r' || key === 'R') key = 'sqrt';
  if (key === 'm' || key === 'M') key = 'MU';

  const button = document.querySelector(`.btn[data-key="${key}"]`);
  if (button) {
    button.classList.remove('active');
  }
});

// Main Input Handler
function handleInput(key) {
  if (isNumber(key)) {
    handleNumber(key);
  } else if (key === '00') {
    handleDoubleZero();
  } else if (key === '.') {
    handleDecimal();
  } else if (isOperator(key)) {
    handleOperator(key);
  } else if (key === '=') {
    handleEquals();
  } else if (key === 'CE/C') {
    handleClearEntry();
  } else if (key === 'ON/AC') {
    handleAllClear();
  } else if (key === '+/-') {
    handleSignToggle();
  } else if (key === 'sqrt') {
    handleSquareRoot();
  } else if (key === 'MU') {
    handleMarkup();
  } else if (key === '%') {
    handlePercent();
  } else if (key === '00-0') {
    handleTaxDemo(); // Placeholder demo action
  } else if (isMemoryKey(key)) {
    handleMemory(key);
  }
  updateDisplay();
}

// Check Input Types
function isNumber(val) {
  return /^[0-9]$/.test(val);
}

function isOperator(val) {
  return ['+', '-', '*', '/'].includes(val);
}

function isMemoryKey(val) {
  return ['MC', 'MR', 'M-', 'M+'].includes(val);
}

// Handling Number Inputs
function handleNumber(num) {
  if (currentValue === '0' || resetOnNextInput) {
    currentValue = num;
    resetOnNextInput = false;
  } else {
    const cleanNum = currentValue.replace(/[^0-9]/g, '');
    if (cleanNum.length < MAX_DIGITS) {
      currentValue += num;
    }
  }
}

// Handling Double Zero (00)
function handleDoubleZero() {
  if (currentValue === '0' || resetOnNextInput) {
    currentValue = '0';
    resetOnNextInput = false;
    return;
  }
  const cleanNum = currentValue.replace(/[^0-9]/g, '');
  if (cleanNum.length < MAX_DIGITS - 1) {
    currentValue += '00';
  } else if (cleanNum.length < MAX_DIGITS) {
    currentValue += '0';
  }
}

// Handling Decimal Point
function handleDecimal() {
  if (resetOnNextInput) {
    currentValue = '0.';
    resetOnNextInput = false;
    return;
  }
  if (!currentValue.includes('.')) {
    currentValue += '.';
  }
}

// Handling Sign Toggle (+/-)
function handleSignToggle() {
  if (currentValue === '0' || currentValue === 'Error') return;
  if (currentValue.startsWith('-')) {
    currentValue = currentValue.substring(1);
  } else {
    currentValue = '-' + currentValue;
  }
}

// Handling Square Root (√)
function handleSquareRoot() {
  const num = parseFloat(currentValue);
  if (num < 0) {
    currentValue = 'Error';
  } else {
    currentValue = formatResult(Math.sqrt(num));
  }
  resetOnNextInput = true;
}

// Handling Markup (MU)
// A + B MU calculates A / (1 - B/100) -> Standard commercial mark-up
function handleMarkup() {
  if (!activeOperation || previousValue === null) return;
  
  const a = parseFloat(previousValue);
  const b = parseFloat(currentValue);
  let result = 0;

  if (activeOperation === '+') {
    // Selling price: Cost / (1 - Margin%)
    if (b >= 100) {
      currentValue = 'Error';
      activeOperation = null;
      previousValue = null;
      resetOnNextInput = true;
      return;
    }
    result = a / (1 - (b / 100));
  } else if (activeOperation === '-') {
    // Selling price with discount: Cost * (1 - Margin%)
    result = a * (1 - (b / 100));
  } else if (activeOperation === '*') {
    // Selling price: Cost * (1 + Margin%)
    result = a * (1 + (b / 100));
  } else if (activeOperation === '/') {
    // Ratio
    result = a / (b / 100);
  }

  currentValue = formatResult(result);
  activeOperation = null;
  previousValue = null;
  resetOnNextInput = true;
}

// Handling Percent (%)
function handlePercent() {
  if (!activeOperation || previousValue === null) {
    // Single number percentage (e.g. 50% = 0.5)
    currentValue = formatResult(parseFloat(currentValue) / 100);
    resetOnNextInput = true;
    return;
  }

  const a = parseFloat(previousValue);
  const b = parseFloat(currentValue);
  let result = 0;

  switch (activeOperation) {
    case '+':
      result = a + (a * b / 100);
      break;
    case '-':
      result = a - (a * b / 100);
      break;
    case '*':
      result = a * (b / 100);
      break;
    case '/':
      result = a / (b / 100);
      break;
  }

  currentValue = formatResult(result);
  activeOperation = null;
  previousValue = null;
  resetOnNextInput = true;
}

// Handling Tax Demo (00-0)
// Just flips between normal display and a demo tax offset, showing tax labels
function handleTaxDemo() {
  // Simple fun functionality for tax demonstration:
  // Adds 10% tax to the current number
  const num = parseFloat(currentValue);
  if (!isNaN(num) && currentValue !== 'Error') {
    currentValue = formatResult(num * 1.10); // +10% tax rate demo
  }
}

// Handling Operators
function handleOperator(op) {
  const currentNum = parseFloat(currentValue);

  if (activeOperation && !resetOnNextInput) {
    const result = calculate(parseFloat(previousValue), currentNum, activeOperation);
    currentValue = formatResult(result);
    previousValue = currentValue;
  } else {
    previousValue = currentValue;
  }

  activeOperation = op;
  resetOnNextInput = true;
}

// Handling Equals
function handleEquals() {
  if (!activeOperation || previousValue === null) return;

  const currentNum = parseFloat(currentValue);
  const prevNum = parseFloat(previousValue);
  const result = calculate(prevNum, currentNum, activeOperation);

  currentValue = formatResult(result);
  previousValue = null;
  activeOperation = null;
  resetOnNextInput = true;
}

// Handling Clear Entry (CE/C)
function handleClearEntry() {
  lcdScreenEl.classList.add('blink');
  setTimeout(() => lcdScreenEl.classList.remove('blink'), 250);

  currentValue = '0';
  resetOnNextInput = false;
}

// Handling All Clear (ON/AC)
function handleAllClear() {
  lcdScreenEl.classList.add('blink');
  setTimeout(() => lcdScreenEl.classList.remove('blink'), 250);

  currentValue = '0';
  previousValue = null;
  activeOperation = null;
  resetOnNextInput = false;
}

// Handling Backspace (for keyboard users)
function handleBackspace() {
  if (resetOnNextInput) return;
  if (currentValue.length > 1) {
    currentValue = currentValue.slice(0, -1);
    if (currentValue === '-' || currentValue === '') {
      currentValue = '0';
    }
  } else {
    currentValue = '0';
  }
  updateDisplay();
}

// Memory Operations
function handleMemory(memKey) {
  const currentNum = parseFloat(currentValue);

  switch (memKey) {
    case 'MC':
      memoryRegister = 0;
      break;
    case 'MR':
      currentValue = formatResult(memoryRegister);
      resetOnNextInput = true;
      break;
    case 'M+':
      memoryRegister += currentNum;
      resetOnNextInput = true;
      break;
    case 'M-':
      memoryRegister -= currentNum;
      resetOnNextInput = true;
      break;
  }
}

// Calculation Engine
function calculate(a, b, op) {
  switch (op) {
    case '+': return a + b;
    case '-': return a - b;
    case '*': return a * b;
    case '/':
      if (b === 0) return 'Error';
      return a / b;
    default: return b;
  }
}

// Formatting Output to Fit Screen
function formatResult(num) {
  if (num === 'Error') return 'Error';
  if (isNaN(num)) return 'Error';
  if (!isFinite(num)) return 'Error';

  let str = num.toString();

  if (str.includes('e')) {
    const tempNum = Number(num).toPrecision(MAX_DIGITS - 4);
    return tempNum.toString();
  }

  if (str.includes('.')) {
    const parts = str.split('.');
    const integerPartLength = parts[0].replace('-', '').length;
    const decimalPlaces = MAX_DIGITS - integerPartLength - (str.startsWith('-') ? 1 : 0);

    if (decimalPlaces > 0) {
      let fixed = Number(num).toFixed(Math.min(decimalPlaces, 8));
      while (fixed.endsWith('0') && fixed.includes('.')) {
        fixed = fixed.slice(0, -1);
      }
      if (fixed.endsWith('.')) {
        fixed = fixed.slice(0, -1);
      }
      return fixed;
    } else {
      return Math.round(num).toString();
    }
  }

  const cleanStr = str.replace('-', '');
  if (cleanStr.length > MAX_DIGITS) {
    return 'Error'; // Screen Overflow
  }

  return str;
}

// Update LCD Screen UI
function updateDisplay() {
  let displayStr = currentValue;

  if (displayStr !== 'Error') {
    if (!displayStr.includes('.')) {
      displayStr += '.';
    }
  }

  displayEl.textContent = displayStr;

  // Update memory indicator
  if (memoryRegister !== 0) {
    memoryIndicatorEl.classList.add('active');
  } else {
    memoryIndicatorEl.classList.remove('active');
  }
}

// Button Click Press Visual Feedback Helper
function triggerButtonVisualFeedback(button) {
  button.classList.add('active');
  setTimeout(() => button.classList.remove('active'), 80);
}
