/**
 * GURU DATTA PEETHAM & RUSHIVANI - CLIENT APPLICATION
 * Clean, simple, and well-commented for beginners.
 */

// ==========================================================
// 1. APPLICATION STATE
// ==========================================================
let productsList = [];
let cart = JSON.parse(localStorage.getItem('guru_datta_cart') || '[]');
let currentCategory = 'all';
let currentUser = JSON.parse(localStorage.getItem('guru_datta_user') || 'null');
let currentAuthTab = 'admin';

// Initialize when page loads
document.addEventListener('DOMContentLoaded', () => {
  loadCategories();
  loadProducts();
  updateCartBadge();
  updateAuthUI();
  loadRealtimeYouTubeContent();
  loadRealtimeCommunityPosts();

  // Shrinking navbar on scroll
  window.addEventListener('scroll', () => {
    const header = document.getElementById('mainHeader');
    if (!header) return;
    if (window.scrollY > 40) {
      header.classList.add('scrolled');
    } else {
      header.classList.remove('scrolled');
    }
  }, { passive: true });
});

// ==========================================================
// 2. CATEGORIES & PRODUCTS (SACRED STORE)
// ==========================================================

const FALLBACK_CATEGORIES = [
  { category_id: 3, category_name: 'Audumbar & Malas' },
  { category_id: 1, category_name: 'Dattatreya Murtis' },
  { category_id: 2, category_name: 'Sacred Padukas & Yantras' },
  { category_id: 4, category_name: 'Guru Charitra & Scriptures' },
  { category_id: 5, category_name: 'Datta Pooja Essentials' }
];

const FALLBACK_PRODUCTS = [
  { product_id: 1, category_id: 1, name: 'Pure Brass Lord Dattatreya Idol with Arch (7 inch)', price: 2499, original_price: 3200, stock_quantity: 20, tag: 'SACRED', image_url: 'dattatreya', description: 'Exquisite 3-faced Lord Dattatreya (Brahma, Vishnu, Maheshwara) surrounded by 4 sacred Vedas as dogs and Kamadhenu.' },
  { product_id: 2, category_id: 2, name: 'Consecrated Brass Datta Charan Paduka (Holy Feet)', price: 1299, original_price: 1750, stock_quantity: 35, tag: 'HOLY FEET', image_url: 'paduka', description: 'Heavy solid brass lotus footprints of Lord Dattatreya embossed with auspicious Ashtamangala signs.' },
  { product_id: 3, category_id: 3, name: 'Original Karungali Mala (108 Ebony Wood Beads, 8mm)', price: 1499, original_price: 1999, stock_quantity: 40, tag: 'BESTSELLER', image_url: 'karungali', description: 'Authentic black ebony wood (Karungali) energized at the Peetham. Shields against negative energies and pacifies Mars dosha.' },
  { product_id: 4, category_id: 3, name: 'Natural Black Hakik Mala (108 Beads with Silver Cap)', price: 899, original_price: 1250, stock_quantity: 45, tag: 'EVIL EYE REMEDY', image_url: 'hakik', description: 'Pure certified Kala Akik (Black Agate) energized with Datta Kavacham. Shields from evil eye (Drishti).' },
  { product_id: 5, category_id: 3, name: 'Energized Red Hakik Mala (Lal Akik, 108 Beads)', price: 950, original_price: 1300, stock_quantity: 30, tag: 'VITALITY', image_url: 'hakik', description: 'Natural Red Agate beads strung on durable sacred thread. Enhances physical vitality and courage.' },
  { product_id: 6, category_id: 3, name: 'Lab-Certified 5-Mukhi Nepali Rudraksha Mala (108 Beads)', price: 1299, original_price: 1800, stock_quantity: 50, tag: 'CERTIFIED', image_url: 'rudraksha_mala', description: 'Premium authentic 5-Mukhi Nepali Rudraksha beads with silver capping. Ideal for daily mantra japa.' },
  { product_id: 7, category_id: 3, name: 'Rare Natural 1-Mukhi (Ek Mukhi) Rudraksha in Pure Silver', price: 3499, original_price: 4500, stock_quantity: 10, tag: 'RARE / SHIVA', image_url: 'ek_mukhi', description: 'Exceedingly rare cashew-shaped 1-Mukhi Rudraksha mounted in pure 925 silver capping.' },
  { product_id: 8, category_id: 3, name: 'Sacred Gauri Shankar Rudraksha (Joined Shiva-Parvati)', price: 2999, original_price: 3800, stock_quantity: 15, tag: 'HARMONY', image_url: 'gauri_shankar', description: 'Two naturally conjoined sacred Rudraksha beads representing Shiva and Shakti.' },
  { product_id: 9, category_id: 3, name: 'Authentic Audumbar Wood Japa Mala (108 Beads)', price: 699, original_price: 950, stock_quantity: 50, tag: 'ENERGIZED', image_url: 'mala', description: 'Natural beads crafted from the holy Audumbara (Fig) tree beloved by Lord Dattatreya.' },
  { product_id: 10, category_id: 4, name: 'Shri Guru Charitra Sacred Pothi (Hardcover)', price: 850, original_price: 1100, stock_quantity: 40, tag: 'MUST READ', image_url: 'charitra', description: 'The divine scripture detailing the leelas of Lord Dattatreya, Sripada Srivallabha, and Sri Narasimha Saraswati.' },
  { product_id: 11, category_id: 2, name: 'Energized Copper Dattatreya Mahayantra (3x3 inch)', price: 799, original_price: 1050, stock_quantity: 30, tag: 'PROTECTION', image_url: 'yantra', description: 'Pure copper sacred geometric yantra blessed by Vedic priests to magnetize divine wisdom and family harmony.' },
  { product_id: 12, category_id: 5, name: 'Girnar Ashta-Gandha Pure Sandalwood Chandan (100g)', price: 349, original_price: 450, stock_quantity: 100, tag: 'FRAGRANT', image_url: 'chandan', description: 'Original saffron and sandalwood paste prepared according to ancient temple recipes for Lord Dattatreya tilak.' }
];

// Fetch categories from Python backend or fallback
async function loadCategories() {
  const container = document.getElementById('categoryButtons');
  if (!container) return;
  try {
    const res = await fetch('/api/categories');
    if (!res.ok) throw new Error('API unavailable');
    const categories = await res.json();
    renderCategoryButtons(categories);
  } catch (err) {
    renderCategoryButtons(FALLBACK_CATEGORIES);
  }
}

function renderCategoryButtons(categories) {
  const container = document.getElementById('categoryButtons');
  if (!container) return;
  const existingButtons = container.querySelectorAll('.cat-btn:not(:first-child)');
  existingButtons.forEach(b => b.remove());

  categories.forEach(cat => {
    const btn = document.createElement('button');
    btn.className = 'cat-btn';
    btn.textContent = cat.category_name;
    btn.onclick = () => selectCategory(cat.category_id, btn);
    container.appendChild(btn);
  });
}

// Fetch products from backend or fallback
async function loadProducts(search = '') {
  const grid = document.getElementById('productGrid');
  grid.innerHTML = '<div class="loading-box"><div class="spinner"></div><p>Invoking Sacred Items...</p></div>';

  try {
    let url = '/api/products?';
    if (currentCategory !== 'all') url += `category_id=${currentCategory}&`;
    if (search) url += `search=${encodeURIComponent(search)}&`;

    const res = await fetch(url);
    if (!res.ok) throw new Error('API unavailable');
    productsList = await res.json();
    renderProducts(productsList);
  } catch (err) {
    // Graceful offline & GitHub Pages fallback
    let list = [...FALLBACK_PRODUCTS];
    if (currentCategory !== 'all') {
      list = list.filter(p => p.category_id === parseInt(currentCategory));
    }
    if (search) {
      const q = search.toLowerCase();
      list = list.filter(p => p.name.toLowerCase().includes(q) || (p.description || '').toLowerCase().includes(q));
    }
    productsList = list;
    renderProducts(list);
  }
}

// Visual photo or icon for each sacred item
function getProductVisual(item) {
  const img = (item.image_url || '').toLowerCase();
  const name = (item.name || '').toLowerCase();

  if (img.includes('karungali') || name.includes('karungali')) {
    return `<img src="static/images/karungali.svg" alt="${item.name}" class="card-product-photo">`;
  }
  if (img.includes('hakik') || name.includes('hakik')) {
    return `<img src="static/images/hakik.svg" alt="${item.name}" class="card-product-photo">`;
  }
  if (img.includes('gauri') || name.includes('gauri')) {
    return `<img src="static/images/gauri_shankar.svg" alt="${item.name}" class="card-product-photo">`;
  }
  if (img.includes('ek_mukhi') || name.includes('1-mukhi')) {
    return `<img src="static/images/ek_mukhi.svg" alt="${item.name}" class="card-product-photo">`;
  }
  if (img.includes('rudraksha') || name.includes('rudraksha')) {
    return `<img src="static/images/rudraksha_mala.svg" alt="${item.name}" class="card-product-photo">`;
  }
  if (name.includes('dattatreya idol') || name.includes('brass lord dattatreya')) {
    return `<img src="static/images/datta_altar.jpg" alt="${item.name}" class="card-product-photo object-cover">`;
  }
  if (name.includes('paduka')) {
    return `<img src="static/images/dattatreya.svg" alt="${item.name}" class="card-product-photo">`;
  }
  return `<span class="emoji-photo">🪷</span>`;
}

// Render product cards on page
function renderProducts(items) {
  const grid = document.getElementById('productGrid');
  if (items.length === 0) {
    grid.innerHTML = '<div class="loading-box"><p>No sacred items found in this category.</p></div>';
    return;
  }

  grid.innerHTML = items.map(item => `
    <div class="card">
      <div class="card-icon-area">
        ${getProductVisual(item)}
        <span class="card-badge">${item.tag || 'CONSECRATED'}</span>
      </div>
      <div class="card-content">
        <h4 class="card-title">${item.name}</h4>
        <p class="card-desc">${item.description || 'Blessed devotional offering.'}</p>
        <div class="card-footer">
          <div class="price">₹${Number(item.price).toLocaleString('en-IN')}</div>
          <button class="add-btn" onclick="addToCart(${item.product_id})">+ Add to Cart</button>
        </div>
      </div>
    </div>
  `).join('');
}

// Filter category button click
function selectCategory(catId, btnElement) {
  currentCategory = catId;
  document.querySelectorAll('.cat-btn').forEach(b => b.classList.remove('active'));
  btnElement.classList.add('active');
  loadProducts();
}

// Search input debouncer
let searchTimer;
function onSearch(query) {
  clearTimeout(searchTimer);
  searchTimer = setTimeout(() => loadProducts(query.trim()), 300);
}

// ==========================================================
// 3. CART OPERATIONS
// ==========================================================
function addToCart(productId) {
  const prod = productsList.find(p => p.product_id === productId);
  if (!prod) return;

  const found = cart.find(item => item.product_id === productId);
  if (found) {
    found.quantity += 1;
  } else {
    cart.push({
      product_id: prod.product_id,
      name: prod.name,
      price: prod.price,
      quantity: 1
    });
  }

  saveCart();
  showToast(`Added "${prod.name}" to cart! 🕉️`);
}

function updateCartQty(productId, change) {
  const item = cart.find(i => i.product_id === productId);
  if (!item) return;

  item.quantity += change;
  if (item.quantity <= 0) {
    cart = cart.filter(i => i.product_id !== productId);
  }
  saveCart();
  renderCartItems();
}

function saveCart() {
  localStorage.setItem('guru_datta_cart', JSON.stringify(cart));
  updateCartBadge();
}

function updateCartBadge() {
  const totalItems = cart.reduce((sum, item) => sum + item.quantity, 0);
  const desktopBadge = document.getElementById('cartCount');
  const mobileBadge = document.getElementById('mobileCartCount');
  if (desktopBadge) desktopBadge.textContent = totalItems;
  if (mobileBadge) mobileBadge.textContent = totalItems;
}

function toggleCart() {
  const drawer = document.getElementById('cartDrawer');
  const backdrop = document.getElementById('cartBackdrop');
  drawer.classList.toggle('open');
  backdrop.classList.toggle('open');
  if (drawer.classList.contains('open')) {
    renderCartItems();
  }
}

function renderCartItems() {
  const container = document.getElementById('cartItemsContainer');
  const footer = document.getElementById('cartFooter');
  const totalDisplay = document.getElementById('cartTotalDisplay');

  if (cart.length === 0) {
    container.innerHTML = '<p class="text-center" style="margin-top: 40px;">Your cart is empty. 🪷</p>';
    footer.style.display = 'none';
    return;
  }

  footer.style.display = 'block';
  let total = 0;

  container.innerHTML = cart.map(item => {
    const itemTotal = item.price * item.quantity;
    total += itemTotal;
    return `
      <div class="cart-line">
        <div>
          <div class="cart-line-title">${item.name}</div>
          <div class="cart-line-price">₹${item.price} × ${item.quantity} = ₹${itemTotal.toLocaleString('en-IN')}</div>
        </div>
        <div>
          <button class="cat-btn" style="padding: 2px 8px; margin-right: 4px;" onclick="updateCartQty(${item.product_id}, -1)">−</button>
          <button class="cat-btn" style="padding: 2px 8px;" onclick="updateCartQty(${item.product_id}, 1)">+</button>
        </div>
      </div>
    `;
  }).join('');

  totalDisplay.textContent = `₹${total.toLocaleString('en-IN')}`;
}

// ==========================================================
// 4. CHECKOUT, DYNAMIC UPI QR & ORDER SUBMISSION
// ==========================================================
function openCheckout() {
  toggleCart();
  updateCheckoutUpiQr();
  document.getElementById('checkoutModal').classList.add('open');
}

function closeCheckout() {
  document.getElementById('checkoutModal').classList.remove('open');
}

function updateCheckoutUpiQr() {
  const total = cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);
  const upiUri = `upi://pay?pa=gurudattapeetham@upi&pn=GURU+DATTA+PEETHAM&am=${total}&tn=GuruDattaPeetham&cu=INR`;
  const qrImg = document.getElementById('upiQrImg');
  const deepLink = document.getElementById('btnUpiApp');
  if (qrImg) {
    qrImg.src = `https://api.qrserver.com/v1/create-qr-code/?size=180x180&data=${encodeURIComponent(upiUri)}`;
  }
  if (deepLink) {
    deepLink.href = upiUri;
  }
}

function togglePaymentQrView(method) {
  const upiCard = document.getElementById('upiQrCard');
  if (!upiCard) return;
  if (method === 'UPI') {
    upiCard.style.display = 'block';
    updateCheckoutUpiQr();
  } else {
    upiCard.style.display = 'none';
  }
}

async function submitOrder(e) {
  e.preventDefault();
  const btn = document.getElementById('submitOrderBtn');
  btn.textContent = 'Recording Divine Order...';
  btn.disabled = true;

  const hasWhatsapp = document.getElementById('custHasWhatsapp')?.checked ? 1 : 0;
  const utrNumber = document.getElementById('custUtr')?.value?.trim() || '';

  const payload = {
    customer: {
      customer_name: document.getElementById('custName').value,
      customer_email: document.getElementById('custEmail').value,
      customer_phone: document.getElementById('custPhone').value,
      shipping_address: document.getElementById('custAddress').value,
      payment_method: document.getElementById('custPayment').value,
      has_whatsapp: hasWhatsapp,
      utr_number: utrNumber
    },
    items: cart
  };

  try {
    const res = await fetch('/api/orders', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    const result = await res.json();
    if (res.ok) {
      cart = [];
      saveCart();
      closeCheckout();
      document.getElementById('confirmedOrderId').textContent = result.order_number;
      document.getElementById('successModal').classList.add('open');
      loadProducts();
    } else {
      alert(result.error || 'Failed to submit order');
    }
  } catch (err) {
    alert('Error connecting to backend database');
  } finally {
    btn.textContent = 'Place Divine Order';
    btn.disabled = false;
  }
}

function closeSuccessModal() {
  document.getElementById('successModal').classList.remove('open');
}

// ==========================================================
// 5. AUTHENTICATION (ADMIN, DEVOTEE & GOOGLE LOGIN)
// ==========================================================
function openAuthModal() {
  document.getElementById('authModal').classList.add('open');
}

function closeAuthModal() {
  document.getElementById('authModal').classList.remove('open');
}

function switchAuthTab(tab) {
  currentAuthTab = tab;
  const tabAdmin = document.getElementById('tabAdminLogin');
  const tabUser = document.getElementById('tabUserLogin');
  const hint = document.getElementById('adminHint');
  const googleBox = document.getElementById('googleAuthBox');
  const modalTitle = document.getElementById('authModalTitle');

  if (tab === 'admin') {
    tabAdmin.classList.add('active');
    tabUser.classList.remove('active');
    modalTitle.textContent = '👑 Admin Login (Guru Datta Peetham)';
    if (hint) hint.style.display = 'block';
    if (googleBox) googleBox.style.display = 'none';
  } else {
    tabUser.classList.add('active');
    tabAdmin.classList.remove('active');
    modalTitle.textContent = '👤 Devotee Login';
    if (hint) hint.style.display = 'none';
    if (googleBox) googleBox.style.display = 'block';
  }
}

async function triggerGoogleSignIn() {
  const email = prompt("Enter your Google / Gmail account:", "devotee@gmail.com");
  if (!email) return;
  const name = prompt("Enter your Full Name:", email.split("@")[0]);

  try {
    const res = await fetch('/api/auth/google', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: email.trim(), name: (name || '').trim() })
    });
    const data = await res.json();
    if (res.ok && data.success) {
      currentUser = data.user;
      localStorage.setItem('guru_datta_user', JSON.stringify(currentUser));
      closeAuthModal();
      updateAuthUI();
      showToast(`Welcome ${currentUser.full_name || currentUser.username}! Signed in with Google. 🪷`);
    } else {
      alert(data.error || "Google Sign-In failed.");
    }
  } catch (err) {
    alert("Error connecting to Google authentication service.");
  }
}

async function handleLogin(e) {
  e.preventDefault();
  const usernameInput = document.getElementById('loginUsername').value;
  const passwordInput = document.getElementById('loginPassword').value;
  const submitBtn = document.getElementById('loginSubmitBtn');

  submitBtn.disabled = true;
  submitBtn.textContent = 'Verifying...';

  try {
    const res = await fetch('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        username: usernameInput,
        password: passwordInput
      })
    });

    const data = await res.json();

    if (res.ok && data.success) {
      currentUser = data.user;
      localStorage.setItem('guru_datta_user', JSON.stringify(currentUser));
      closeAuthModal();
      updateAuthUI();
      showToast(`Welcome ${currentUser.full_name || currentUser.username}! 🙏`);
      
      // If admin logged in, open the Orders dashboard
      if (currentUser.role === 'admin') {
        openAdminOrdersModal();
      }
    } else {
      alert(data.error || 'Invalid credentials. Please try again.');
    }
  } catch (err) {
    alert('Failed to connect to authentication service.');
  } finally {
    submitBtn.disabled = false;
    submitBtn.textContent = 'Sign In';
  }
}

function handleLogout() {
  currentUser = null;
  localStorage.removeItem('guru_datta_user');
  updateAuthUI();
  showToast('Logged out successfully. 🕉️');
}

// Update Header & Mobile Dock according to login state
function updateAuthUI() {
  const container = document.getElementById('authContainer');
  const mobileLabel = document.getElementById('mobileAuthLabel');
  const mobileIcon = document.getElementById('mobileAuthIcon');

  if (currentUser) {
    if (currentUser.role === 'admin') {
      container.innerHTML = `
        <div class="user-session-box">
          <span class="admin-badge-pill">👑 Admin</span>
          <button class="btn-admin-orders" onclick="openAdminOrdersModal()">📋 Dashboard</button>
          <button class="btn-logout" onclick="handleLogout()">Logout</button>
        </div>
      `;
      if (mobileLabel) mobileLabel.textContent = 'Admin';
      if (mobileIcon) mobileIcon.textContent = '👑';
    } else {
      container.innerHTML = `
        <div class="user-session-box">
          <span>🙏 ${currentUser.full_name || currentUser.username}</span>
          <button class="btn-logout" onclick="handleLogout()">Logout</button>
        </div>
      `;
      if (mobileLabel) mobileLabel.textContent = 'Account';
      if (mobileIcon) mobileIcon.textContent = '👤';
    }
  } else {
    container.innerHTML = `
      <button class="btn-auth-trigger" id="authBtn" onclick="openAuthModal()">
        <span>👤 Login / Admin</span>
      </button>
    `;
    if (mobileLabel) mobileLabel.textContent = 'Admin';
    if (mobileIcon) mobileIcon.textContent = '👑';
  }
}

// Mobile bottom dock handler for Admin/Auth button
function onMobileAuthClick() {
  if (currentUser && currentUser.role === 'admin') {
    openAdminOrdersModal();
  } else {
    openAuthModal();
  }
}

// ==========================================================
// 6. PROFESSIONAL ADMIN DASHBOARD (ORDERS, RATES, ISSUES)
// ==========================================================
function openAdminOrdersModal() {
  document.getElementById('adminOrdersModal').classList.add('open');
  switchAdminTab('orders');
}

function closeAdminOrdersModal() {
  document.getElementById('adminOrdersModal').classList.remove('open');
}

function switchAdminTab(tabName) {
  const tabs = ['orders', 'products', 'issues'];
  tabs.forEach(t => {
    const btn = document.getElementById(`tabBtn${t.charAt(0).toUpperCase() + t.slice(1)}`);
    const pane = document.getElementById(`paneAdmin${t.charAt(0).toUpperCase() + t.slice(1)}`);
    if (btn) btn.classList.toggle('active', t === tabName);
    if (pane) pane.classList.toggle('active', t === tabName);
  });

  if (tabName === 'orders') loadAdminOrders();
  else if (tabName === 'products') loadAdminProductsTable();
  else if (tabName === 'issues') loadAdminIssues();
}

async function loadAdminOrders() {
  const countDisplay = document.getElementById('adminOrdersCount');
  const tableBody = document.getElementById('adminOrdersTableBody');
  countDisplay.textContent = 'Fetching orders...';
  tableBody.innerHTML = '<tr><td colspan="8" class="text-center">Loading orders from database...</td></tr>';

  try {
    const res = await fetch('/api/orders');
    const orders = await res.json();

    countDisplay.textContent = `Total Orders Placed: ${orders.length}`;

    if (orders.length === 0) {
      tableBody.innerHTML = '<tr><td colspan="8" class="text-center">No orders placed yet.</td></tr>';
      return;
    }

    tableBody.innerHTML = orders.map(order => {
      const cleanPhone = (order.customer_phone || '').replace(/[^0-9]/g, '');
      const waLink = `https://wa.me/91${cleanPhone}?text=${encodeURIComponent("నమస్కారం " + order.customer_name + " గారు! గురు దత్త పీఠం నుండి మీ ఆర్డర్ (" + order.order_number + ") కన్ఫర్మ్ అయింది. శ్రీ గురుదేవ దత్త!")}`;
      const isPaid = order.payment_status === 'PAID_VERIFIED';

      return `
        <tr>
          <td><strong>${order.order_number}</strong><br><small style="color:#777;">${order.created_at || ''}</small></td>
          <td><strong>${order.customer_name}</strong><br><small>${order.customer_email || ''}</small></td>
          <td>
            <a href="tel:${order.customer_phone}" style="color:var(--maroon);font-weight:700;">${order.customer_phone}</a>
            ${order.has_whatsapp ? `<br><a href="${waLink}" target="_blank" class="btn-whatsapp-chat">💬 WhatsApp Devotee</a>` : ''}
          </td>
          <td><small>${order.shipping_address || '-'}</small></td>
          <td><strong style="color:var(--saffron);">₹${Number(order.total_amount).toLocaleString('en-IN')}</strong></td>
          <td>
            <span class="payment-badge ${isPaid ? 'PAID_VERIFIED' : 'PENDING_VERIFICATION'}">
              ${isPaid ? '✅ PAID & VERIFIED' : '⏳ PENDING VERIFICATION'}
            </span>
            <br>
            <small>UTR: <strong>${order.utr_number || 'None'}</strong></small>
            <button class="btn-toggle-payment" onclick="togglePaymentVerification(${order.order_id}, '${order.payment_status}')">
              ${isPaid ? 'Mark Pending' : '✅ Verify Payment'}
            </button>
          </td>
          <td>
            <span class="status-badge ${order.order_status}">
              ${order.order_status}
            </span>
          </td>
          <td>
            <select class="status-select" onchange="updateOrderStatus(${order.order_id}, this.value)">
              <option value="CONFIRMED" ${order.order_status === 'CONFIRMED' ? 'selected' : ''}>CONFIRMED</option>
              <option value="DISPATCHED" ${order.order_status === 'DISPATCHED' ? 'selected' : ''}>DISPATCHED</option>
              <option value="DELIVERED" ${order.order_status === 'DELIVERED' ? 'selected' : ''}>DELIVERED</option>
              <option value="CANCELLED" ${order.order_status === 'CANCELLED' ? 'selected' : ''}>CANCELLED</option>
            </select>
          </td>
        </tr>
      `;
    }).join('');
  } catch (err) {
    countDisplay.textContent = 'Error loading orders';
    tableBody.innerHTML = '<tr><td colspan="8" class="text-center" style="color:red;">Error connecting to orders database.</td></tr>';
  }
}

async function togglePaymentVerification(orderId, currentStatus) {
  const nextStatus = (currentStatus === 'PAID_VERIFIED') ? 'PENDING_VERIFICATION' : 'PAID_VERIFIED';
  try {
    const res = await fetch(`/api/admin/orders/${orderId}/payment`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ payment_status: nextStatus })
    });
    if (res.ok) {
      showToast(`Payment updated: ${nextStatus === 'PAID_VERIFIED' ? 'PAID & VERIFIED ✅' : 'PENDING ⏳'}`);
      loadAdminOrders();
    } else {
      alert("Failed to update payment status");
    }
  } catch (err) {
    alert("Error updating payment verification");
  }
}

async function updateOrderStatus(orderId, newStatus) {
  try {
    const res = await fetch(`/api/admin/orders/${orderId}/status`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status: newStatus })
    });

    if (res.ok) {
      showToast(`Order status updated to ${newStatus} ✨`);
      loadAdminOrders();
    } else {
      alert('Failed to update order status');
    }
  } catch (err) {
    alert('Error updating order');
  }
}

// 6.2 PRODUCTS & RATES MANAGEMENT
async function loadAdminProductsTable() {
  const tbody = document.getElementById('adminProductsTableBody');
  tbody.innerHTML = '<tr><td colspan="7" class="text-center">Loading sacred items...</td></tr>';

  try {
    const res = await fetch('/api/products');
    const prods = await res.json();

    if (prods.length === 0) {
      tbody.innerHTML = '<tr><td colspan="7" class="text-center">No items found in store.</td></tr>';
      return;
    }

    tbody.innerHTML = prods.map(p => `
      <tr>
        <td>#${p.product_id}</td>
        <td><strong>${p.name}</strong></td>
        <td><small>${p.category_name || 'General'}</small></td>
        <td>
          <input type="number" id="rateInput_${p.product_id}" class="rate-input" value="${p.price}" min="1" step="0.01">
          <button class="btn-save-rate" onclick="saveProductRate(${p.product_id})">Save ₹</button>
        </td>
        <td><span style="font-weight:700;">${p.stock_quantity}</span></td>
        <td><span class="card-badge" style="position:static;">${p.tag || 'CONSECRATED'}</span></td>
        <td>
          <button class="btn-del-item" onclick="deleteStoreProduct(${p.product_id}, '${p.name.replace(/'/g, "\\'")}')">🗑️ Delete</button>
        </td>
      </tr>
    `).join('');
  } catch (err) {
    tbody.innerHTML = '<tr><td colspan="7" class="text-center" style="color:red;">Error loading items.</td></tr>';
  }
}

async function saveProductRate(productId) {
  const input = document.getElementById(`rateInput_${productId}`);
  const newRate = parseFloat(input?.value);
  if (!newRate || newRate <= 0) {
    alert("Please enter a valid rate/price.");
    return;
  }

  try {
    const res = await fetch(`/api/products/${productId}/price`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ price: newRate })
    });
    if (res.ok) {
      showToast(`Rate updated successfully to ₹${newRate} ✨`);
      loadAdminProductsTable();
      loadProducts(); // Update the main store view
    } else {
      alert("Failed to update item price");
    }
  } catch (err) {
    alert("Error updating product rate");
  }
}

async function deleteStoreProduct(productId, name) {
  if (!confirm(`Are you sure you want to remove "${name}" from the store?`)) return;

  try {
    const res = await fetch(`/api/products/${productId}`, {
      method: 'DELETE'
    });
    if (res.ok) {
      showToast(`Removed "${name}" from store.`);
      loadAdminProductsTable();
      loadProducts();
    } else {
      alert("Failed to delete product");
    }
  } catch (err) {
    alert("Error deleting item");
  }
}

async function handleAddProduct(e) {
  e.preventDefault();
  const name = document.getElementById('newProdName').value;
  const category_id = parseInt(document.getElementById('newProdCategory').value);
  const price = parseFloat(document.getElementById('newProdPrice').value);
  const stock_quantity = parseInt(document.getElementById('newProdStock').value);
  const tag = document.getElementById('newProdTag').value;

  try {
    const res = await fetch('/api/products', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        name,
        category_id,
        price,
        stock_quantity,
        tag,
        description: `Consecrated ${name} blessed at Guru Datta Peetham altar.`
      })
    });

    if (res.ok) {
      showToast(`Added "${name}" to store! 🪷`);
      e.target.reset();
      loadAdminProductsTable();
      loadProducts();
    } else {
      alert("Failed to add new item");
    }
  } catch (err) {
    alert("Error adding sacred item");
  }
}

// 6.3 DEVOTEE ISSUES & HELPDESK
function openIssueModal() {
  document.getElementById('issueModal').classList.add('open');
}

function closeIssueModal() {
  document.getElementById('issueModal').classList.remove('open');
}

async function submitDevoteeIssue(e) {
  e.preventDefault();
  const btn = document.getElementById('submitIssueBtn');
  btn.textContent = 'Submitting...';
  btn.disabled = true;

  const payload = {
    devotee_name: document.getElementById('issueName').value,
    phone: document.getElementById('issuePhone').value,
    has_whatsapp: document.getElementById('issueHasWhatsapp')?.checked ? 1 : 0,
    email: document.getElementById('issueEmail').value,
    order_number: document.getElementById('issueOrderNo').value,
    issue_type: document.getElementById('issueType').value,
    description: document.getElementById('issueDesc').value
  };

  try {
    const res = await fetch('/api/issues', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    if (res.ok) {
      closeIssueModal();
      e.target.reset();
      showToast("Your issue has been recorded! Guruji's team will contact you on WhatsApp / phone shortly. 🙏");
    } else {
      alert("Failed to submit issue. Please check fields.");
    }
  } catch (err) {
    alert("Error connecting to helpdesk.");
  } finally {
    btn.textContent = 'Submit Issue 🙏';
    btn.disabled = false;
  }
}

async function loadAdminIssues() {
  const countDisplay = document.getElementById('adminIssuesCount');
  const tbody = document.getElementById('adminIssuesTableBody');
  countDisplay.textContent = 'Fetching devotee issues...';
  tbody.innerHTML = '<tr><td colspan="8" class="text-center">Loading issues...</td></tr>';

  try {
    const res = await fetch('/api/admin/issues');
    const issues = await res.json();

    countDisplay.textContent = `Devotee Issues Raised: ${issues.length}`;

    if (issues.length === 0) {
      tbody.innerHTML = '<tr><td colspan="8" class="text-center">No open issues reported. All is blessed! 🪷</td></tr>';
      return;
    }

    tbody.innerHTML = issues.map(iss => {
      const cleanPhone = (iss.phone || '').replace(/[^0-9]/g, '');
      const waLink = `https://wa.me/91${cleanPhone}?text=${encodeURIComponent("నమస్కారం " + iss.devotee_name + " గారు! గురు దత్త పీఠం హెల్ప్‌డెస్క్ నుండి మీ సమస్య (" + iss.issue_type + ") గురించి మాట్లాడుతున్నాము. శ్రీ గురుదేవ దత్త!")}`;
      const isResolved = iss.status === 'RESOLVED';

      return `
        <tr>
          <td><strong>#${iss.issue_id}</strong></td>
          <td><strong>${iss.devotee_name}</strong><br><small>${iss.email || ''}</small></td>
          <td>
            <a href="tel:${iss.phone}" style="color:var(--maroon);font-weight:700;">${iss.phone}</a>
            ${iss.has_whatsapp ? `<br><a href="${waLink}" target="_blank" class="btn-whatsapp-chat">💬 Chat</a>` : ''}
          </td>
          <td><small>${iss.order_number || '-'}</small></td>
          <td><span class="card-badge" style="position:static;">${iss.issue_type}</span></td>
          <td><small style="line-height:1.4; display:block; max-width:260px;">${iss.description}</small></td>
          <td>
            <span class="status-badge ${isResolved ? 'DELIVERED' : 'CONFIRMED'}">
              ${iss.status}
            </span>
          </td>
          <td>
            ${!isResolved ? `<button class="btn-save-rate" onclick="resolveDevoteeIssue(${iss.issue_id})">✅ Resolve</button>` : `<span style="color:#166534; font-size:0.75rem;">Done</span>`}
          </td>
        </tr>
      `;
    }).join('');
  } catch (err) {
    tbody.innerHTML = '<tr><td colspan="8" class="text-center" style="color:red;">Error loading devotee issues.</td></tr>';
  }
}

async function resolveDevoteeIssue(issueId) {
  try {
    const res = await fetch(`/api/admin/issues/${issueId}/status`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status: 'RESOLVED', notes: 'Resolved by Admin' })
    });
    if (res.ok) {
      showToast(`Issue #${issueId} marked as RESOLVED ✨`);
      loadAdminIssues();
    } else {
      alert("Failed to update issue status");
    }
  } catch (err) {
    alert("Error updating issue");
  }
}

// ==========================================================
// 7. SACRED TOAST NOTIFICATION
// ==========================================================
function showToast(msg) {
  const toast = document.getElementById('toast');
  toast.textContent = msg;
  toast.style.display = 'block';
  setTimeout(() => {
    toast.style.display = 'none';
  }, 3200);
}

// ==========================================================
// 8. REAL-TIME YOUTUBE VIDEOS & SHORTS (@Rushivani)
// ==========================================================
async function loadRealtimeYouTubeContent() {
  const shortsContainer = document.getElementById('shortsGrid');
  const videosContainer = document.getElementById('videosGrid');

  try {
    const res = await fetch('/api/youtube/feed');
    const data = await res.json();

    if (!res.ok || !data.shorts || !data.videos) return;

    // Render Real-Time Shorts with Automatic Thumbnails
    if (data.shorts.length > 0 && shortsContainer) {
      shortsContainer.innerHTML = data.shorts.slice(0, 6).map(short => `
        <a href="${short.url}" target="_blank" class="short-card">
          <div class="short-thumb-wrapper">
            <img src="${short.thumbnail}" alt="${short.title}" loading="lazy" onerror="this.src='https://i.ytimg.com/vi/${short.id}/0.jpg'">
            <div class="short-overlay">
              <span class="short-play-btn">▶</span>
              <span class="short-tag">⚡ Short</span>
            </div>
          </div>
          <div class="short-info">
            <h4>${short.title}</h4>
            <span>@Rushivani • Click to Watch</span>
          </div>
        </a>
      `).join('');
    }

    // Render Real-Time Videos with Automatic Thumbnails & Inline Player
    if (data.videos.length > 0 && videosContainer) {
      videosContainer.innerHTML = data.videos.slice(0, 6).map(video => `
        <article class="video-card">
          <a href="${video.url}" target="_blank" style="text-decoration:none; color:inherit;">
            <div class="video-thumbnail">
              <div class="yt-play-overlay">▶</div>
              <img src="${video.thumbnail}" alt="${video.title}" loading="lazy" onerror="this.src='https://i.ytimg.com/vi/${video.id}/0.jpg'">
              <span class="video-duration">Pravachanam</span>
            </div>
          </a>
          <div class="video-details">
            <h4>${video.title}</h4>
            <div class="video-action-row">
              <a href="${video.url}" target="_blank" class="watch-now-btn">Watch on YouTube ▶</a>
              <button class="btn-play-inline" onclick="playVideoModal('${video.id}', '${video.title.replace(/'/g, "\\'")}')">Play Here 📺</button>
            </div>
          </div>
        </article>
      `).join('');
    }
  } catch (err) {
    console.warn("Using default real-time cards, feed fetch:", err);
  }
}

function playVideoModal(videoId, title) {
  const modal = document.getElementById('videoModal');
  const iframe = document.getElementById('videoIframe');
  const titleElem = document.getElementById('videoModalTitle');
  const extLink = document.getElementById('videoExternalLink');

  if (titleElem) titleElem.textContent = title || 'Rushivani Pravachanam';
  if (iframe) iframe.src = `https://www.youtube.com/embed/${videoId}?autoplay=1`;
  if (extLink) extLink.href = `https://www.youtube.com/watch?v=${videoId}`;

  if (modal) modal.classList.add('open');
}

function closeVideoModal() {
  const modal = document.getElementById('videoModal');
  const iframe = document.getElementById('videoIframe');
  if (iframe) iframe.src = '';
  if (modal) modal.classList.remove('open');
}

// ==========================================================
// 9. REAL-TIME YOUTUBE COMMUNITY POSTS (@Rushivani/posts)
// ==========================================================
async function loadRealtimeCommunityPosts() {
  const container = document.getElementById('communityGrid');
  if (!container) return;

  try {
    const res = await fetch('/api/youtube/posts');
    const data = await res.json();

    if (!res.ok || !data.posts || data.posts.length === 0) return;

    container.innerHTML = data.posts.slice(0, 6).map(post => {
      const primaryImg = (post.images && post.images.length > 0) ? post.images[0] : null;
      const imgMarkup = primaryImg ? `
        <div class="post-image-banner">
          <a href="${post.url}" target="_blank" style="width:100%; height:100%; display:block;">
            <img src="${primaryImg}" alt="${(post.title || '').replace(/"/g, '&quot;')}" class="post-featured-media" style="width:100%; height:100%; object-fit:cover;" loading="lazy">
          </a>
        </div>
      ` : '';

      let tagClass = 'mala-tag';
      if (post.tag && post.tag.includes('భవిష్య')) tagClass = 'festival-tag';
      else if (post.tag && post.tag.includes('లైవ్')) tagClass = 'aarti-tag';

      return `
        <article class="post-card premium-card">
          <div class="post-header-row">
            <div class="author-avatar-box">
              <img src="static/images/guruji.png" alt="Rushivani" class="author-avatar">
              <div>
                <strong>Rushivani ఋషివాణి</strong>
                <span class="author-handle">@Rushivani • ${post.published || 'Recent'}</span>
              </div>
            </div>
            <span class="post-tag ${tagClass}">${post.tag || '📢 తాజా అప్డేట్'}</span>
          </div>
          ${imgMarkup}
          <h4 class="post-title">${post.title || 'Rushivani Community Post'}</h4>
          <p class="post-content">${post.content || ''}</p>
          <div class="post-footer">
            <span class="post-likes">❤️ YouTube Community</span>
            <a href="${post.url}" target="_blank" class="post-yt-btn">View on YouTube ▶</a>
          </div>
        </article>
      `;
    }).join('');
  } catch (err) {
    console.warn("Could not fetch realtime community posts:", err);
  }
}

