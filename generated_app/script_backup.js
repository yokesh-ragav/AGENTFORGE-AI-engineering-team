(function () {
  // Key for local storage persistence
  const STORAGE_KEY = 'pockettrack_expenses';

  // Seed data for clean initial demo if empty
  const initialExpenses = [
    { id: '1', name: 'Reference Book', amount: 450, category: 'Education', date: '2023-10-25' },
    { id: '2', name: 'Bus Monthly Pass', amount: 350, category: 'Transport', date: '2023-10-25' },
    { id: '3', name: 'Lunch at Canteen', amount: 120, category: 'Food', date: '2023-10-24' },
    { id: '4', name: 'Movie Ticket', amount: 250, category: 'Entertainment', date: '2023-10-23' }
  ];

  // Load state from LocalStorage or seed with sample data
  let expenses = [];
  try {
    const rawData = localStorage.getItem(STORAGE_KEY);
    if (rawData) {
      expenses = JSON.parse(rawData);
    } else {
      expenses = [...initialExpenses];
      saveToStorage();
    }
  } catch (e) {
    expenses = [...initialExpenses];
  }

  // DOM Elements
  const form = document.getElementById('expense-form');
  const expenseNameInput = document.getElementById('expense-name');
  const expenseAmountInput = document.getElementById('expense-amount');
  const expenseCategoryInput = document.getElementById('expense-category');
  const emojiPreview = document.getElementById('emoji-preview');

  const totalSpentEl = document.getElementById('total-spent');
  const transactionCountEl = document.getElementById('transaction-count');
  const topCategoryEl = document.getElementById('top-category');

  const insightBox = document.getElementById('insight-box');
  const breakdownList = document.getElementById('breakdown-list');

  const searchInput = document.getElementById('search-input');
  const filterCategory = document.getElementById('filter-category');
  const expenseList = document.getElementById('expense-list');

  // Category Emoji Mapping
  const categoryEmojis = {
    'Food': '🍛',
    'Transport': '🚌',
    'Education': '📚',
    'Shopping': '🛍️',
    'Entertainment': '🎬',
    'Health': '💊',
    'Bills': '💵',
    'Other': '💰'
  };

  // Keywords Map for Smart Emoji Detection
  const keywordEmojis = [
    { keys: ['tea', 'coffee', 'starbucks', 'beverage', 'drink'], emoji: '☕' },
    { keys: ['pizza', 'burger', 'sandwich', 'patis', 'samosa', 'momo'], emoji: '🍔' },
    { keys: ['maggi', 'noodles', 'ramen', 'pasta'], emoji: '🍜' },
    { keys: ['lunch', 'dinner', 'breakfast', 'meal', 'canteen', 'biryani', 'rice', 'roti', 'food'], emoji: '🍛' },
    { keys: ['bus', 'shuttle', 'pass'], emoji: '🚌' },
    { keys: ['auto', 'rickshaw', 'ola', 'uber'], emoji: '🛺' },
    { keys: ['train', 'metro', 'subway'], emoji: '🚆' },
    { keys: ['petrol', 'fuel', 'gas', 'scooty', 'bike'], emoji: '⛽' },
    { keys: ['shopping', 'clothes', 'shirt', 'jeans', 'myntra', 'amazon'], emoji: '🛍️' },
    { keys: ['movie', 'netflix', 'cinema', 'pvr', 'show', 'theatre'], emoji: '🎬' },
    { keys: ['book', 'copy', 'print', 'xerox', 'stationery', 'pen', 'pencil', 'notebook'], emoji: '📚' },
    { keys: ['college', 'semester', 'exam', 'fee', 'admission', 'uniform'], emoji: '🎓' },
    { keys: ['medicine', 'med', 'doctor', 'pill', 'health', 'tablet'], emoji: '💊' },
    { keys: ['hotel', 'stay', 'hostel', 'room'], emoji: '🏨' },
    { keys: ['travel', 'trip', 'flight', 'ticket'], emoji: '✈️' }
  ];

  // Helper to determine active emoji based on name input
  function detectEmoji(name, category) {
    const cleanName = name.trim().toLowerCase();
    
    // Check keyword matching
    for (const item of keywordEmojis) {
      if (item.keys.some(key => cleanName.includes(key))) {
        return item.emoji;
      }
    }
    // Fallback to Category base emoji
    return categoryEmojis[category] || '💰';
  }

  // Update real-time emoji indicator on form input
  function updateEmojiPreview() {
    const name = expenseNameInput.value;
    const category = expenseCategoryInput.value;
    emojiPreview.textContent = detectEmoji(name, category);
  }

  expenseNameInput.addEventListener('input', updateEmojiPreview);
  expenseCategoryInput.addEventListener('change', updateEmojiPreview);

  // Save changes helper
  function saveToStorage() {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(expenses));
    } catch (e) {
      console.error('Failed to write to local storage', e);
    }
  }

  // Utility formatter
  function formatCurrency(num) {
    return `₹${Number(num).toLocaleString('en-IN', {
      maximumFractionDigits: 2,
      minimumFractionDigits: 0
    })}`;
  }

  // Calculate & Refresh Metrics & DOM
  function updateUI() {
    // 1. Calculate Metrics
    const total = expenses.reduce((sum, item) => sum + item.amount, 0);
    const count = expenses.length;

    // Calculate sum per category
    const catTotals = {};
    expenses.forEach(item => {
      catTotals[item.category] = (catTotals[item.category] || 0) + item.amount;
    });

    // Find top spending category
    let topCatName = '—';
    let topCatVal = 0;
    Object.keys(catTotals).forEach(cat => {
      if (catTotals[cat] > topCatVal) {
        topCatVal = catTotals[cat];
        topCatName = cat;
      }
    });

    // Update Top-level Cards
    totalSpentEl.textContent = formatCurrency(total);
    transactionCountEl.textContent = count;
    
    if (topCatName !== '—') {
      const icon = categoryEmojis[topCatName] || '💰';
      topCategoryEl.textContent = `${icon} ${topCatName} · ${formatCurrency(topCatVal)}`;
    } else {
      topCategoryEl.textContent = '—';
    }

    // 2. Render Spending Breakdown (Progress Bars)
    breakdownList.innerHTML = '';
    const sortedCategories = Object.keys(categoryEmojis).sort((a,b) => {
      return (catTotals[b] || 0) - (catTotals[a] || 0);
    });

    sortedCategories.forEach(cat => {
      const amount = catTotals[cat] || 0;
      const pct = total > 0 ? Math.round((amount / total) * 100) : 0;
      const icon = categoryEmojis[cat];

      // Only show categories that have some positive spending
      if (amount > 0) {
        const row = document.createElement('div');
        row.className = 'breakdown-row';
        row.innerHTML = `
          <div class="breakdown-labels">
            <div class="breakdown-name-group">
              <span>${icon}</span>
              <span>${cat}</span>
            </div>
            <div class="breakdown-amount-group">
              <span>${formatCurrency(amount)}</span>
              <span class="breakdown-pct">${pct}%</span>
            </div>
          </div>
          <div class="progress-track">
            <div class="progress-fill" style="width: ${pct}%"></div>
          </div>
        `;
        breakdownList.appendChild(row);
      }
    });

    if (breakdownList.innerHTML === '') {
      breakdownList.innerHTML = `<p style="font-size:0.875rem; color:var(--text-muted); text-align:center; padding:1rem 0;">No active category spending.</p>`;
    }

    // 3. Render dynamic insights
    generateSmartInsight(total, count, topCatName, topCatVal, catTotals);

    // 4. Render Expense History List
    renderHistoryList();
  }

  // Generates and displays a smart contextual insight locally
  function generateSmartInsight(total, count, topCatName, topCatVal, catTotals) {
    if (count === 0) {
      insightBox.innerHTML = `<p class="insight-text">No expenses logged yet. Save your first entry to generate intelligent insights!</p>`;
      return;
    }

    let insight = '';

    if (total > 0 && topCatName !== '—') {
      const percentage = Math.round((topCatVal / total) * 100);
      
      // Categorical alerts
      if (topCatName === 'Food' && percentage > 40) {
        insight = `Food makes up ${percentage}% of your budget (${formatCurrency(topCatVal)}). Consider eating more at the hostel mess or canteen to trim costs.`;
      } else if (topCatName === 'Entertainment' && percentage > 30) {
        insight = `You spent ${formatCurrency(topCatVal)} on Entertainment (${percentage}% of total). Balancing it with Education items could improve your savings plan!`;
      } else if (topCatName === 'Transport' && percentage > 25) {
        insight = `Transport is quite high at ${percentage}% of total spending. Grouping trips or opting for college transport and bus passes might help.`;
      } else if (expenses.length >= 5) {
        insight = `Your highest category is ${topCatName} representing ${percentage}% of total outlays. Tracking 5+ items is a strong habit!`;
      } else {
        insight = `You spent ${formatCurrency(topCatVal)} on ${topCatName}, making it your current top spending category.`;
      }
    } else {
      insight = `You have recorded ${count} expenses so far. Keep monitoring daily micro-transactions.`;
    }

    insightBox.innerHTML = `<p class="insight-text">${insight}</p>`;
  }

  // Render the history list with active filter & search query
  function renderHistoryList() {
    const query = searchInput.value.toLowerCase().trim();
    const activeCat = filterCategory.value;

    const filtered = expenses.filter(item => {
      const matchesSearch = item.name.toLowerCase().includes(query);
      const matchesCategory = activeCat === 'All' || item.category === activeCat;
      return matchesSearch && matchesCategory;
    });

    expenseList.innerHTML = '';

    if (filtered.length === 0) {
      expenseList.innerHTML = `
        <div class="empty-state">
          <div class="empty-icon">🔍</div>
          <p>No matching expenses found</p>
        </div>
      `;
      return;
    }

    // Render list (newest first)
    [...filtered].reverse().forEach(item => {
      const emoji = detectEmoji(item.name, item.category);
      const row = document.createElement('div');
      row.className = 'expense-item';
      row.innerHTML = `
        <div class="expense-left">
          <div class="expense-emoji-circle">${emoji}</div>
          <div class="expense-details">
            <div class="expense-name-text">${escapeHTML(item.name)}</div>
            <div class="expense-meta">${escapeHTML(item.category)} · ${escapeHTML(item.date || 'Today')}</div>
          </div>
        </div>
        <div class="expense-right">
          <div class="expense-amount-value">${formatCurrency(item.amount)}</div>
          <button class="btn-delete" title="Delete Expense" data-id="${item.id}">✕</button>
        </div>
      `;
      expenseList.appendChild(row);
    });
  }

  // Simple HTML escape for security
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

  // Handle Form Submission
  form.addEventListener('submit', function (e) {
    e.preventDefault();

    const name = expenseNameInput.value.trim();
    const amount = parseFloat(expenseAmountInput.value);
    const category = expenseCategoryInput.value;

    if (!name || isNaN(amount) || amount <= 0) {
      return;
    }

    const todayStr = new Date().toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });

    const newExpense = {
      id: Date.now().toString(),
      name: name,
      amount: amount,
      category: category,
      date: todayStr
    };

    expenses.push(newExpense);
    saveToStorage();
    
    // Reset Form
    form.reset();
    updateEmojiPreview();
    
    // Update Layout
    updateUI();
  });

  // Handle Delete Button Click
  expenseList.addEventListener('click', function (e) {
    if (e.target.classList.contains('btn-delete')) {
      const targetId = e.target.getAttribute('data-id');
      expenses = expenses.filter(item => item.id !== targetId);
      saveToStorage();
      updateUI();
    }
  });

  // Listen for search & filters
  searchInput.addEventListener('input', renderHistoryList);
  filterCategory.addEventListener('change', renderHistoryList);

  // Initial Load and Setup
  updateEmojiPreview();
  updateUI();

})();