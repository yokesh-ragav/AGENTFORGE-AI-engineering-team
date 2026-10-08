/**
 * FinTrack Personal Finance Engine
 * Fully interactive self-contained Javascript controller using LocalStorage
 */

// Application data structure and defaults
let state = {
  transactions: [],
  budgets: {
    Housing: 15000,
    Groceries: 5000,
    Utilities: 3000,
    Entertainment: 2000,
    Transport: 1500,
    "Dining Out": 2500,
    Other: 2000
  },
  theme: 'light'
};

// Seed dataset for demonstration
const demoTransactions = [
  { id: '1', description: 'Monthly Work Salary', amount: 32000.00, type: 'income', category: 'Salary', date: getRelativeDate(0), notes: 'Regular payroll deposit' },
  { id: '2', description: 'Apartment Monthly Rent', amount: 12000.00, type: 'expense', category: 'Housing', date: getRelativeDate(-1), notes: 'Electronic bank transfer payment' },
  { id: '3', description: 'Organic Grocery Stores', amount: 1640.50, type: 'expense', category: 'Groceries', date: getRelativeDate(-2), notes: 'Weekly organic wholefoods basket' },
  { id: '4', description: 'High-speed Internet Service', amount: 899.99, type: 'expense', category: 'Utilities', date: getRelativeDate(-3), notes: 'Monthly broadband billing' },
  { id: '5', description: 'Weekend Cinema Tickets', amount: 340.00, type: 'expense', category: 'Entertainment', date: getRelativeDate(-4), notes: 'Two IMAX tickets and snack box combo' },
  { id: '6', description: 'Freelance Frontend Dev Work', amount: 4500.00, type: 'income', category: 'Freelance', date: getRelativeDate(-5), notes: 'Custom React dashboard delivery' },
  { id: '7', description: 'Premium Coffee shop', amount: 67.50, type: 'expense', category: 'Dining Out', date: getRelativeDate(-5), notes: 'Matcha latte and avocado toast' },
  { id: '8', description: 'Metro Subway card recharge', amount: 500.00, type: 'expense', category: 'Transport', date: getRelativeDate(-6), notes: 'Commuter pass automatic top up' }
];

// Helper to construct dynamic date offset
function getRelativeDate(offsetDays) {
  const d = new Date();
  d.setDate(d.getDate() + offsetDays);
  return d.toISOString().split('T')[0];
}

// Map categories to standard color definitions
const CATEGORY_COLORS = {
  Housing: '#4f46e5',
  Groceries: '#10b981',
  Utilities: '#d97706',
  Entertainment: '#db2777',
  Transport: '#0891b2',
  "Dining Out": '#e11d48',
  Salary: '#16a34a',
  Freelance: '#7c3aed',
  Investments: '#0284c7',
  Other: '#4b5563'
};

// Map system category inputs to styling classes
const CATEGORY_CLASSES = {
  Housing: 'cat-housing',
  Groceries: 'cat-groceries',
  Utilities: 'cat-utilities',
  Entertainment: 'cat-entertainment',
  Transport: 'cat-transport',
  "Dining Out": 'cat-dining',
  Salary: 'cat-salary',
  Freelance: 'cat-freelance',
  Investments: 'cat-investments',
  Other: 'cat-other'
};

// Capture HTML elements
const themeToggleBtn = document.getElementById('theme-toggle-btn');
const sunIcon = themeToggleBtn.querySelector('.sun-icon');
const moonIcon = themeToggleBtn.querySelector('.moon-icon');
const demoDataBtn = document.getElementById('demo-data-btn');
const exportBtn = document.getElementById('export-btn');
const importFile = document.getElementById('import-file');

const balanceAmount = document.getElementById('balance-amount');
const balanceTrend = document.getElementById('balance-trend');
const totalIncome = document.getElementById('total-income');
const incomeCount = document.getElementById('income-count');
const totalExpenses = document.getElementById('total-expenses');
const expenseCount = document.getElementById('expense-count');
const savingsRate = document.getElementById('savings-rate');
const savingsProgress = document.getElementById('savings-progress');

const txForm = document.getElementById('transaction-form');
const txIdInput = document.getElementById('tx-id');
const txType = document.getElementById('tx-type');
const txAmount = document.getElementById('tx-amount');
const txDesc = document.getElementById('tx-description');
const txCategory = document.getElementById('tx-category');
const txDate = document.getElementById('tx-date');
const txNotes = document.getElementById('tx-notes');
const formTitle = document.getElementById('form-title');
const addTransactionBtn = document.getElementById('add-transaction-btn');
const cancelEditBtn = document.getElementById('cancel-edit-btn');

const manageBudgetsBtn = document.getElementById('manage-budgets-btn');
const budgetInputGroup = document.getElementById('budget-input-group');
const budgetCategory = document.getElementById('budget-category');
const budgetAmountInput = document.getElementById('budget-amount');
const saveBudgetBtn = document.getElementById('save-budget-btn');
const budgetContainer = document.getElementById('budget-container');

const chartLegend = document.getElementById('chart-legend');
const chartVisual = document.getElementById('chart-visual');

const filterSearch = document.getElementById('filter-search');
const filterType = document.getElementById('filter-type');
const filterCategory = document.getElementById('filter-category');
const sortBy = document.getElementById('sort-by');
const clearFiltersBtn = document.getElementById('clear-filters-btn');
const transactionRows = document.getElementById('transaction-rows');
const emptyState = document.getElementById('empty-state');
const emptyResetBtn = document.getElementById('empty-reset-btn');
const yearLabel = document.getElementById('year-label');

// Initialize local app engine
window.addEventListener('DOMContentLoaded', () => {
  yearLabel.textContent = new Date().getFullYear();
  initApp();
});

function initApp() {
  loadData();
  
  // Set default modern date to today
  txDate.value = new Date().toISOString().split('T')[0];
  
  // Setup DOM event listeners
  themeToggleBtn.addEventListener('click', toggleTheme);
  demoDataBtn.addEventListener('click', loadDemoDataset);
  exportBtn.addEventListener('click', exportData);
  importFile.addEventListener('change', importData);
  emptyResetBtn.addEventListener('click', loadDemoDataset);
  
  txForm.addEventListener('submit', handleFormSubmit);
  cancelEditBtn.addEventListener('click', resetForm);
  
  manageBudgetsBtn.addEventListener('click', () => {
    budgetInputGroup.classList.toggle('hidden');
    manageBudgetsBtn.textContent = budgetInputGroup.classList.contains('hidden') ? 'Set Budget' : 'Close Panel';
  });
  saveBudgetBtn.addEventListener('click', updateBudgetLimit);
  
  txType.addEventListener('change', () => {
    if (!txIdInput.value) {
      addTransactionBtn.textContent = txType.value === 'expense' ? 'Add Expense' : 'Add Income';
    }
  });

  filterSearch.addEventListener('input', renderApp);
  filterType.addEventListener('change', renderApp);
  filterCategory.addEventListener('change', renderApp);
  sortBy.addEventListener('change', renderApp);
  clearFiltersBtn.addEventListener('click', clearFilters);
  
  // Initial draw
  renderApp();
}

// LocalStorage Persistence functions
function loadData() {
  const rawData = localStorage.getItem('fintrack_state');
  if (rawData) {
    try {
      const parsed = JSON.parse(rawData);
      if (parsed && typeof parsed === 'object') {
        state = {
          transactions: Array.isArray(parsed.transactions) ? parsed.transactions : [],
          budgets: (parsed.budgets && typeof parsed.budgets === 'object') ? parsed.budgets : {
            Housing: 15000,
            Groceries: 5000,
            Utilities: 3000,
            Entertainment: 2000,
            Transport: 1500,
            "Dining Out": 2500,
            Other: 2000
          },
          theme: parsed.theme || 'light'
        };
      }
    } catch (e) {
      console.error('Data parsing failure. Restoring defaults.', e);
    }
  }
  
  // Double-check properties existence
  if (!state.transactions) {
    state.transactions = [];
  }
  if (!state.budgets) {
    state.budgets = {
      Housing: 15000,
      Groceries: 5000,
      Utilities: 3000,
      Entertainment: 2000,
      Transport: 1500,
      "Dining Out": 2500,
      Other: 2000
    };
  }
  
  // Theme check
  if (state.theme === 'dark') {
    document.body.classList.add('dark-theme');
    document.body.classList.remove('light-theme');
    sunIcon.style.display = 'none';
    moonIcon.style.display = 'block';
  } else {
    document.body.classList.remove('dark-theme');
    document.body.classList.add('light-theme');
    sunIcon.style.display = 'block';
    moonIcon.style.display = 'none';
  }
}

function saveData() {
  localStorage.setItem('fintrack_state', JSON.stringify(state));
}

function loadDemoDataset() {
  state.transactions = [...demoTransactions];
  saveData();
  renderApp();
}

function toggleTheme() {
  if (document.body.classList.contains('dark-theme')) {
    document.body.classList.remove('dark-theme');
    document.body.classList.add('light-theme');
    sunIcon.style.display = 'block';
    moonIcon.style.display = 'none';
    state.theme = 'light';
  } else {
    document.body.classList.add('dark-theme');
    document.body.classList.remove('light-theme');
    sunIcon.style.display = 'none';
    moonIcon.style.display = 'block';
    state.theme = 'dark';
  }
  saveData();
}

// Backup & Recovery mechanisms
function exportData() {
  const jsonString = `data:text/json;charset=utf-8,${encodeURIComponent(JSON.stringify(state, null, 2))}`;
  const downloadAnchor = document.createElement('a');
  downloadAnchor.setAttribute('href', jsonString);
  downloadAnchor.setAttribute('download', `fintrack_backup_${new Date().toISOString().split('T')[0]}.json`);
  document.body.appendChild(downloadAnchor);
  downloadAnchor.click();
  downloadAnchor.remove();
}

function importData(event) {
  const fileReader = new FileReader();
  const file = event.target.files[0];
  if (!file) return;
  
  fileReader.onload = function(e) {
    try {
      const parsed = JSON.parse(e.target.result);
      if (parsed.transactions && parsed.budgets) {
        state = parsed;
        saveData();
        renderApp();
        alert('Data backup file successfully parsed and imported!');
      } else {
        alert('Invalid data schema. Could not restore backup.');
      }
    } catch (err) {
      alert('Error parsing raw backup file. Ensure standard JSON format.');
    }
  };
  fileReader.readAsText(file);
}

// Master Render System
function renderApp() {
  // 1. Process Totals & Stats Overview
  let balance = 0;
  let incomeTotal = 0;
  let expenseTotal = 0;
  let incomeCountVal = 0;
  let expenseCountVal = 0;
  
  state.transactions.forEach(t => {
    const amt = parseFloat(t.amount) || 0;
    if (t.type === 'income') {
      incomeTotal += amt;
      incomeCountVal++;
    } else {
      expenseTotal += amt;
      expenseCountVal++;
    }
  });
  
  balance = incomeTotal - expenseTotal;
  
  balanceAmount.textContent = formatCurrency(balance);
  totalIncome.textContent = formatCurrency(incomeTotal);
  totalExpenses.textContent = formatCurrency(expenseTotal);
  
  incomeCount.textContent = `${incomeCountVal} receipt${incomeCountVal !== 1 ? 's' : ''}`;
  expenseCount.textContent = `${expenseCountVal} receipt${expenseCountVal !== 1 ? 's' : ''}`;
  
  // Trend UI logic
  if (balance > 0) {
    balanceAmount.className = "stat-amount text-success";
    balanceTrend.innerHTML = `<span class="trend-up">▲ Dynamic Net Surplus</span>`;
  } else if (balance < 0) {
    balanceAmount.className = "stat-amount text-danger";
    balanceTrend.innerHTML = `<span class="trend-down">▼ Monthly Net Deficit</span>`;
  } else {
    balanceAmount.className = "stat-amount";
    balanceTrend.innerHTML = `<span class="trend-neutral">Balanced Neutral Allocation</span>`;
  }
  
  // Savings Rate
  let savingsPercentage = 0;
  if (incomeTotal > 0) {
    savingsPercentage = Math.round(((incomeTotal - expenseTotal) / incomeTotal) * 100);
    savingsPercentage = Math.max(0, savingsPercentage); // Keep positive
  }
  savingsRate.textContent = `${savingsPercentage}%`;
  savingsProgress.style.width = `${Math.min(100, savingsPercentage)}%`;
  
  // 2. Render Budgets progress bars
  renderBudgets(expenseTotal);
  
  // 3. Render Categorical Analytics breakdown Chart
  renderAnalyticsChart();
  
  // 4. Filter, Sort and Render Table Rows
  renderTransactionsTable();
}

function formatCurrency(amount) {
  return new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', minimumFractionDigits: 2 }).format(amount);
}

// Category Budgets layout update
function renderBudgets(expenseTotal) {
  budgetContainer.innerHTML = '';
  
  // Gather actual expenditure breakdown by category
  const categorySpent = {};
  state.transactions.forEach(t => {
    if (t.type === 'expense') {
      categorySpent[t.category] = (categorySpent[t.category] || 0) + (parseFloat(t.amount) || 0);
    }
  });
  
  // Populate UI for defined categories with set budgets
  Object.keys(state.budgets).forEach(cat => {
    const limit = state.budgets[cat];
    const spent = categorySpent[cat] || 0;
    const percentage = Math.round((spent / limit) * 100);
    
    let barColorClass = 'bg-success';
    if (percentage >= 100) {
      barColorClass = 'bg-danger';
    } else if (percentage >= 80) {
      barColorClass = 'bg-warning';
    }
    
    const budgetItem = document.createElement('div');
    budgetItem.className = 'budget-item';
    budgetItem.innerHTML = `
      <div class="budget-item-info">
        <span class="budget-name">${cat}</span>
        <span class="budget-details">${formatCurrency(spent)} of ${formatCurrency(limit)} (${percentage}%)</span>
      </div>
      <div class="progress-bar-container mini">
        <div class="progress-bar-fill ${barColorClass}" style="width: ${Math.min(100, percentage)}%"></div>
      </div>
    `;
    budgetContainer.appendChild(budgetItem);
  });
}

function updateBudgetLimit(e) {
  e.preventDefault();
  const cat = budgetCategory.value;
  const limitStr = budgetAmountInput.value.replace(/[^0-9.]/g, '');
  const limit = parseFloat(limitStr);
  
  if (isNaN(limit) || limit <= 0) {
    alert('Please enter a valid positive budget amount.');
    return;
  }
  
  state.budgets[cat] = limit;
  budgetAmountInput.value = '';
  budgetInputGroup.classList.add('hidden');
  manageBudgetsBtn.textContent = 'Set Budget';
  
  saveData();
  renderApp();
}

// Custom CSS-Flex Based Responsive Bar Chart Drawing
function renderAnalyticsChart() {
  chartLegend.innerHTML = '';
  chartVisual.innerHTML = '';
  
  // 1. Gather all expenses and categorize
  const categorySpent = {};
  let totalExpenseAmt = 0;
  
  state.transactions.forEach(t => {
    if (t.type === 'expense') {
      const amt = parseFloat(t.amount) || 0;
      categorySpent[t.category] = (categorySpent[t.category] || 0) + amt;
      totalExpenseAmt += amt;
    }
  });
  
  if (totalExpenseAmt === 0) {
    chartVisual.innerHTML = `
      <div class="empty-chart-state">
        <p>No expense data logged to analyze. Add expense logs to populate.</p>
      </div>
    `;
    return;
  }
  
  // Sort categories by expenditure size
  const sortedCategories = Object.keys(categorySpent).sort((a, b) => categorySpent[b] - categorySpent[a]);
  
  // Create Visual Bars
  sortedCategories.forEach(cat => {
    const amt = categorySpent[cat];
    const pct = ((amt / totalExpenseAmt) * 100).toFixed(1);
    const color = CATEGORY_COLORS[cat] || '#6b7280';
    
    // Append Legend Item
    const legendItem = document.createElement('span');
    legendItem.className = 'legend-item';
    legendItem.innerHTML = `
      <span class="legend-dot" style="background-color: ${color}"></span>
      ${cat} (${pct}%)
    `;
    chartLegend.appendChild(legendItem);
    
    // Append Chart row
    const row = document.createElement('div');
    row.className = 'chart-bar-row';
    row.innerHTML = `
      <span class="chart-bar-label" title="${cat}">${cat}</span>
      <div class="chart-bar-track">
        <div class="chart-bar-fill" style="width: ${pct}%; background-color: ${color}"></div>
      </div>
      <span class="chart-bar-val">${formatCurrency(amt)}</span>
    `;
    chartVisual.appendChild(row);
  });
}

// Filter, Sort and render transaction log table
function renderTransactionsTable() {
  transactionRows.innerHTML = '';
  
  const query = filterSearch.value.toLowerCase().trim();
  const typeVal = filterType.value;
  const catVal = filterCategory.value;
  const sortVal = sortBy.value;
  
  // Apply filtering rules
  let filtered = state.transactions.filter(t => {
    const matchesSearch = t.description.toLowerCase().includes(query) || (t.notes && t.notes.toLowerCase().includes(query));
    const matchesType = typeVal === 'all' || t.type === typeVal;
    const matchesCategory = catVal === 'all' || t.category === catVal;
    return matchesSearch && matchesType && matchesCategory;
  });
  
  // Apply sorting options
  filtered.sort((a, b) => {
    if (sortVal === 'date-desc') {
      return new Date(b.date) - new Date(a.date);
    } else if (sortVal === 'date-asc') {
      return new Date(a.date) - new Date(b.date);
    } else if (sortVal === 'amount-desc') {
      return parseFloat(b.amount) - parseFloat(a.amount);
    } else if (sortVal === 'amount-asc') {
      return parseFloat(a.amount) - parseFloat(b.amount);
    }
    return 0;
  });
  
  if (filtered.length === 0) {
    emptyState.classList.remove('hidden');
    document.querySelector('.transactions-table').style.display = 'none';
    
    // If entire database is completely empty suggest demo data, otherwise suggest filter reset
    if (state.transactions.length === 0) {
      emptyState.querySelector('h3').textContent = 'Welcome to FinTrack!';
      emptyState.querySelector('p').textContent = 'Get started by typing your first transaction or load preset demo metrics.';
      emptyResetBtn.style.display = 'inline-flex';
    } else {
      emptyState.querySelector('h3').textContent = 'No matching search results';
      emptyState.querySelector('p').textContent = 'Refine your keywords, change category parameters or reset filters.';
      emptyResetBtn.style.display = 'none';
    }
  } else {
    emptyState.classList.add('hidden');
    document.querySelector('.transactions-table').style.display = 'table';
    
    filtered.forEach(t => {
      const tr = document.createElement('tr');
      const catClass = CATEGORY_CLASSES[t.category] || 'cat-other';
      const amountFormatted = t.type === 'income' ? `+${formatCurrency(t.amount)}` : `-${formatCurrency(t.amount)}`;
      const amountClass = t.type === 'income' ? 'text-success' : 'text-danger';
      
      // Clean display date format with robust browser compatibility
      let dateDisplay = '';
      try {
        const dateObj = new Date(t.date + 'T00:00:00');
        if (!isNaN(dateObj.getTime())) {
          dateDisplay = dateObj.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
        } else {
          dateDisplay = t.date || '';
        }
      } catch (e) {
        dateDisplay = t.date || '';
      }
      
      tr.innerHTML = `
        <td>${dateDisplay}</td>
        <td>
          <span style="font-weight: 600;">${escapeHTML(t.description)}</span>
          ${t.notes ? `<span class="notes-text">${escapeHTML(t.notes)}</span>` : ''}
        </td>
        <td>
          <span class="category-chip ${catClass}">${t.category}</span>
        </td>
        <td style="text-transform: capitalize;">${t.type}</td>
        <td class="text-right ${amountClass}">${amountFormatted}</td>
        <td class="text-center">
          <div class="row-actions">
            <button class="action-btn edit-btn" onclick="triggerEditTransaction('${t.id}')" title="Edit Transaction" aria-label="Edit transaction">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path><path d="M18.5 2.5a2.121 2.121 0 1 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path></svg>
            </button>
            <button class="action-btn delete-btn" onclick="triggerDeleteTransaction('${t.id}')" title="Delete Transaction" aria-label="Delete transaction">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path><line x1="10" y1="11" x2="10" y2="17"></line><line x1="14" y1="11" x2="14" y2="17"></line></svg>
            </button>
          </div>
        </td>
      `;
      transactionRows.appendChild(tr);
    });
  }
}

// Action Handlers
function handleFormSubmit(e) {
  e.preventDefault();
  
  if (!validateForm()) return;
  
  const id = txIdInput.value;
  const description = txDesc.value.trim();
  const amtStr = txAmount.value.replace(/[^0-9.]/g, '');
  const amount = parseFloat(amtStr);
  const type = txType.value;
  const category = txCategory.value;
  let date = txDate.value;
  if (!date) {
    date = new Date().toISOString().split('T')[0];
  }
  const notes = txNotes.value.trim();
  
  if (id) {
    // Edit existing transaction sequence
    const index = state.transactions.findIndex(t => t.id === id);
    if (index !== -1) {
      state.transactions[index] = { id, description, amount, type, category, date, notes };
    }
  } else {
    // Create new transaction block
    const newTx = {
      id: Date.now().toString(36) + Math.random().toString(36).substr(2, 5),
      description,
      amount,
      type,
      category,
      date,
      notes
    };
    state.transactions.push(newTx);
  }
  
  saveData();
  resetForm();
  renderApp();
}

function triggerDeleteTransaction(id) {
  if (confirm('Are you sure you want to delete this transaction record?')) {
    state.transactions = state.transactions.filter(t => t.id !== id);
    saveData();
    renderApp();
    
    // Reset editing state if the deleted transaction was being edited
    if (txIdInput.value === id) {
      resetForm();
    }
  }
}

function triggerEditTransaction(id) {
  const t = state.transactions.find(tx => tx.id === id);
  if (!t) return;
  
  txIdInput.value = t.id;
  txDesc.value = t.description;
  txAmount.value = t.amount;
  txType.value = t.type;
  txCategory.value = t.category;
  txDate.value = t.date;
  txNotes.value = t.notes || '';
  
  formTitle.textContent = 'Edit Transaction';
  addTransactionBtn.textContent = 'Update Log';
  cancelEditBtn.style.display = 'inline-flex';
  
  // Scroll form into view nicely on small mobile screens
  txForm.scrollIntoView({ behavior: 'smooth', block: 'center' });
}

// Local form field validation logic
function validateForm() {
  let isValid = true;
  
  // Description Validation
  if (txDesc.value.trim() === '') {
    txDesc.classList.add('input-invalid');
    document.getElementById('desc-error').style.display = 'block';
    isValid = false;
  } else {
    txDesc.classList.remove('input-invalid');
    document.getElementById('desc-error').style.display = 'none';
  }
  
  // Amount Validation - Stripping non-numeric values first
  let amtStr = txAmount.value.replace(/[^0-9.]/g, '');
  const amt = parseFloat(amtStr);
  if (isNaN(amt) || amt <= 0) {
    txAmount.classList.add('input-invalid');
    document.getElementById('amount-error').style.display = 'block';
    isValid = false;
  } else {
    txAmount.classList.remove('input-invalid');
    document.getElementById('amount-error').style.display = 'none';
  }
  
  // Category Validation
  if (!txCategory.value) {
    txCategory.classList.add('input-invalid');
    document.getElementById('category-error').style.display = 'block';
    isValid = false;
  } else {
    txCategory.classList.remove('input-invalid');
    document.getElementById('category-error').style.display = 'none';
  }
  
  // Date Validation
  if (!txDate.value) {
    txDate.classList.add('input-invalid');
    document.getElementById('date-error').style.display = 'block';
    isValid = false;
  } else {
    txDate.classList.remove('input-invalid');
    document.getElementById('date-error').style.display = 'none';
  }
  
  return isValid;
}

function resetForm() {
  txIdInput.value = '';
  txForm.reset();
  txDate.value = new Date().toISOString().split('T')[0];
  txCategory.value = 'Other';
  
  formTitle.textContent = 'Add Transaction';
  addTransactionBtn.textContent = txType.value === 'expense' ? 'Add Expense' : 'Add Income';
  cancelEditBtn.style.display = 'none';
  
  // Clear any active invalid classes
  txDesc.classList.remove('input-invalid');
  txAmount.classList.remove('input-invalid');
  txCategory.classList.remove('input-invalid');
  txDate.classList.remove('input-invalid');
  
  document.getElementById('desc-error').style.display = 'none';
  document.getElementById('amount-error').style.display = 'none';
  document.getElementById('category-error').style.display = 'none';
  document.getElementById('date-error').style.display = 'none';
}

function clearFilters() {
  filterSearch.value = '';
  filterType.value = 'all';
  filterCategory.value = 'all';
  sortBy.value = 'date-desc';
  renderApp();
}

// Utility to escape dangerous user markup injection strings
function escapeHTML(str) {
  if (!str) return '';
  return str.replace(/[&<>'"]/g, 
    tag => ({
      '&': '&amp;',
      '<': '&lt;',
      '>': '&gt;',
      "'": '&#39;',
      '"': '&quot;'
    }[tag] || tag)
  );
}

// Expose trigger handlers on window for simple layout onclick invocation
window.triggerEditTransaction = triggerEditTransaction;
window.triggerDeleteTransaction = triggerDeleteTransaction;