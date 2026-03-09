/* ========================================
   GRUHA ALANKARA – MAIN SCRIPT
   ======================================== */

'use strict';

// Backend API base URL
const API_BASE = 'http://localhost:5000';

// =====================
// CUSTOM CURSOR
// =====================
(function initCursor() {
  const cursor = document.getElementById('cursor');
  const dot = document.getElementById('cursorDot');
  if (!cursor || !dot) return;

  let mouseX = -100, mouseY = -100;
  let cursorX = -100, cursorY = -100;

  document.addEventListener('mousemove', e => {
    mouseX = e.clientX;
    mouseY = e.clientY;
    dot.style.left = mouseX + 'px';
    dot.style.top = mouseY + 'px';
  });

  function animateCursor() {
    cursorX += (mouseX - cursorX) * 0.12;
    cursorY += (mouseY - cursorY) * 0.12;
    cursor.style.left = cursorX + 'px';
    cursor.style.top = cursorY + 'px';
    requestAnimationFrame(animateCursor);
  }
  animateCursor();

  document.querySelectorAll('a, button, .furniture-card, .gallery-item, .quick-btn').forEach(el => {
    el.addEventListener('mouseenter', () => {
      cursor.style.transform = 'translate(-50%, -50%) scale(1.6)';
      cursor.style.borderColor = 'rgba(255,255,255,0.8)';
    });
    el.addEventListener('mouseleave', () => {
      cursor.style.transform = 'translate(-50%, -50%) scale(1)';
      cursor.style.borderColor = 'rgba(255,255,255,0.5)';
    });
  });
})();

// =====================
// NAVBAR SCROLL
// =====================
(function initNavbar() {
  const navbar = document.getElementById('navbar');
  if (!navbar) return;

  window.addEventListener('scroll', () => {
    navbar.classList.toggle('scrolled', window.scrollY > 60);
  });

  // Active link on scroll
  const sections = document.querySelectorAll('section[id]');
  const navLinks = document.querySelectorAll('.nav-link');

  const observer = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        navLinks.forEach(link => link.classList.remove('active'));
        const activeLink = document.querySelector(`.nav-link[href="#${entry.target.id}"]`);
        if (activeLink) activeLink.classList.add('active');
      }
    });
  }, { threshold: 0.3 });

  sections.forEach(s => observer.observe(s));
})();

// =====================
// HAMBURGER MENU
// =====================
(function initHamburger() {
  const btn = document.getElementById('hamburger');
  const menu = document.getElementById('mobileMenu');
  if (!btn || !menu) return;

  btn.addEventListener('click', () => {
    const isOpen = menu.classList.toggle('open');
    btn.querySelector('span:nth-child(1)').style.transform = isOpen ? 'rotate(45deg) translate(4px, 4px)' : '';
    btn.querySelector('span:nth-child(2)').style.opacity = isOpen ? '0' : '';
    btn.querySelector('span:nth-child(3)').style.transform = isOpen ? 'rotate(-45deg) translate(4px, -4px)' : '';
  });

  document.querySelectorAll('.mobile-link').forEach(link => {
    link.addEventListener('click', () => {
      menu.classList.remove('open');
    });
  });
})();

// =====================
// SCROLL REVEAL
// =====================
(function initScrollReveal() {
  const revealItems = document.querySelectorAll('.section-header, .analysis-card, .furniture-card, .gallery-item');
  const obs = new IntersectionObserver(entries => {
    entries.forEach((entry, i) => {
      if (entry.isIntersecting) {
        setTimeout(() => {
          entry.target.style.opacity = '1';
          entry.target.style.transform = 'translateY(0)';
        }, i * 60);
        obs.unobserve(entry.target);
      }
    });
  }, { threshold: 0.1 });

  revealItems.forEach(el => {
    el.style.opacity = '0';
    el.style.transform = 'translateY(20px)';
    el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
    obs.observe(el);
  });
})();

// =====================
// FILE UPLOAD & DRAG DROP
// =====================
(function initUpload() {
  const area = document.getElementById('uploadArea');
  const inner = document.getElementById('uploadInner');
  const preview = document.getElementById('uploadPreview');
  const previewImg = document.getElementById('previewImg');
  const fileInput = document.getElementById('fileInput');
  const removeBtn = document.getElementById('removeImg');
  const analyzeBtn = document.getElementById('analyzeBtn');
  const btnLoader = document.getElementById('btnLoader');
  const analysisResults = document.getElementById('analysisResults');
  const furnitureSection = document.getElementById('furniture');

  if (!area) return;

  let hasImage = false;

  function showPreview(file) {
    if (!file || !file.type.startsWith('image/')) return;
    const reader = new FileReader();
    reader.onload = e => {
      previewImg.src = e.target.result;
      previewImg.setAttribute('src', e.target.result);
      inner.style.display = 'none';
      preview.style.display = 'block';
      analyzeBtn.disabled = false;
      hasImage = true;
      // Notify AR section that a room image is available
      window.dispatchEvent(new CustomEvent('roomImageChanged', { detail: { src: e.target.result } }));
    };
    reader.readAsDataURL(file);
  }

  // Drag events
  ['dragenter', 'dragover'].forEach(evt => {
    area.addEventListener(evt, e => {
      e.preventDefault();
      area.classList.add('drag-over');
    });
  });

  ['dragleave', 'drop'].forEach(evt => {
    area.addEventListener(evt, e => {
      e.preventDefault();
      area.classList.remove('drag-over');
    });
  });

  area.addEventListener('drop', e => {
    const file = e.dataTransfer.files[0];
    showPreview(file);
  });

  fileInput.addEventListener('change', e => {
    showPreview(e.target.files[0]);
  });

  area.addEventListener('click', e => {
    if (!hasImage) fileInput.click();
  });

  removeBtn.addEventListener('click', e => {
    e.stopPropagation();
    previewImg.src = '';
    previewImg.setAttribute('src', '');
    inner.style.display = 'flex';
    preview.style.display = 'none';
    analyzeBtn.disabled = true;
    hasImage = false;
    fileInput.value = '';
    analysisResults.style.display = 'none';
    furnitureSection.style.display = 'none';
    // Notify AR section that image was removed
    window.dispatchEvent(new CustomEvent('roomImageChanged', { detail: { src: '' } }));
  });

  // Analyze — connects to backend API
  analyzeBtn.addEventListener('click', async () => {
    if (!hasImage) return;
    const btnText = analyzeBtn.querySelector('.btn-text');
    btnText.style.display = 'none';
    btnLoader.style.display = 'block';
    analyzeBtn.disabled = true;

    try {
      // Step 1: Upload the image
      const formData = new FormData();
      formData.append('image', fileInput.files[0] || await (await fetch(previewImg.src)).blob());

      const uploadRes = await fetch(API_BASE + '/upload-room', { method: 'POST', body: formData });
      const uploadData = await uploadRes.json();

      if (!uploadData.success) {
        showToast(uploadData.error || 'Upload failed');
        btnText.style.display = 'inline';
        btnLoader.style.display = 'none';
        analyzeBtn.disabled = false;
        return;
      }

      window.__uploadedFilename = uploadData.filename;

      // Step 2: Generate full design (analyzes + recommends + generates)
      const designRes = await fetch(API_BASE + '/generate-design', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ filename: uploadData.filename }),
      });
      const designData = await designRes.json();

      btnText.style.display = 'inline';
      btnLoader.style.display = 'none';
      analyzeBtn.disabled = false;

      if (designData.success) {
        // Update analysis cards with real data
        const cards = document.querySelectorAll('.analysis-card .ac-val');
        if (cards[0]) cards[0].textContent = designData.style || 'Modern';
        if (cards[1]) cards[1].textContent = designData.design?.room_analysis_summary?.brightness || 'Well-Lit';
        if (cards[2]) cards[2].textContent = (designData.design?.room_analysis_summary?.floor_space_pct || 72) + '% Optimal';
        const colors = designData.design?.color_theme;
        if (cards[3] && colors) cards[3].textContent = colors.primary + ' / ' + colors.accent;
        const scoreEl = document.querySelector('.score-val');
        if (scoreEl) scoreEl.textContent = (designData.design?.design_score || 87) + '/100';

        // Store recommendations for furniture grid
        if (designData.recommended_furniture) {
          window.__backendFurniture = designData.recommended_furniture;
        }

        analysisResults.style.display = 'block';
        furnitureSection.style.display = 'block';
        analysisResults.scrollIntoView({ behavior: 'smooth', block: 'center' });
        initFurnitureGrid();
      } else {
        showToast(designData.error || 'Analysis failed');
      }
    } catch (err) {
      console.error('Backend error:', err);
      // Fallback to static demo if backend is not running
      btnText.style.display = 'inline';
      btnLoader.style.display = 'none';
      analyzeBtn.disabled = false;
      analysisResults.style.display = 'block';
      furnitureSection.style.display = 'block';
      analysisResults.scrollIntoView({ behavior: 'smooth', block: 'center' });
      initFurnitureGrid();
      showToast('Using demo mode — start backend for full AI analysis');
    }
  });
})();

// =====================
// FURNITURE DATA & GRID
// =====================
const furnitureData = [
  { name: 'Oslo Sofa', style: 'Scandinavian', price: '₹85,000', emoji: '🛋', category: 'seating' },
  { name: 'Drift Armchair', style: 'Contemporary', price: '₹32,000', emoji: '🪑', category: 'seating' },
  { name: 'Nord Coffee Table', style: 'Minimalist', price: '₹18,500', emoji: '🪵', category: 'tables' },
  { name: 'Arc Floor Lamp', style: 'Industrial', price: '₹12,000', emoji: '💡', category: 'lighting' },
  { name: 'Tokyo Bookshelf', style: 'Japanese', price: '₹45,000', emoji: '📚', category: 'storage' },
  { name: 'Mist Side Table', style: 'Wabi-Sabi', price: '₹9,500', emoji: '🪨', category: 'tables' },
  { name: 'Silk Pendant Light', style: 'Luxe Minimal', price: '₹28,000', emoji: '🕯', category: 'lighting' },
  { name: 'Stone Credenza', style: 'Modern', price: '₹72,000', emoji: '🗃', category: 'storage' },
];

let furnitureInitialized = false;

function initFurnitureGrid() {
  if (furnitureInitialized) return;
  furnitureInitialized = true;

  const grid = document.getElementById('furnitureGrid');
  if (!grid) return;

  // Merge backend data into display format if available
  const backendItems = (window.__backendFurniture || []).map(p => ({
    name: p.product_name,
    style: p.style,
    price: '₹' + Number(p.price).toLocaleString('en-IN'),
    emoji: categoryEmoji(p.category),
    category: mapCategory(p.category),
  }));
  const displayData = backendItems.length > 0 ? backendItems : furnitureData;

  function renderFurniture(filter) {
    const filtered = filter === 'all' ? displayData : displayData.filter(f => f.category === filter);
    grid.innerHTML = '';
    filtered.forEach((item, i) => {
      const card = document.createElement('div');
      card.className = 'furniture-card';
      card.style.animationDelay = `${i * 0.06}s`;
      card.innerHTML = `
        <div class="furniture-img">${item.emoji}</div>
        <div class="furniture-info">
          <div class="furniture-name">${item.name}</div>
          <div class="furniture-style">${item.style}</div>
          <div class="furniture-price">${item.price}</div>
          <div class="furniture-actions">
            <button class="furniture-btn primary" onclick="scrollToAR('${item.name}')">Preview in AR</button>
            <button class="furniture-btn" onclick="bookViaBuddy('${item.name}')">Book via AI Buddy</button>
          </div>
        </div>
      `;
      grid.appendChild(card);
    });
  }

  renderFurniture('all');

  document.querySelectorAll('.filter-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      renderFurniture(btn.dataset.filter);
    });
  });

  setTimeout(() => {
    document.getElementById('furniture').scrollIntoView({ behavior: 'smooth' });
  }, 100);
}

function scrollToAR(name) {
  document.getElementById('ar').scrollIntoView({ behavior: 'smooth' });
  showToast(`Loading "${name}" in AR Designer...`);
}

function bookViaBuddy(name) {
  document.getElementById('buddy').scrollIntoView({ behavior: 'smooth' });
  setTimeout(() => {
    const input = document.getElementById('chatInput');
    if (input) {
      input.value = `I'd like to book the ${name}. What's the process?`;
      sendMessage(`I'd like to book the ${name}. What's the process?`);
    }
  }, 600);
}

// =====================
// TOAST NOTIFICATION
// =====================
function showToast(message, duration = 3000) {
  const existing = document.querySelector('.toast');
  if (existing) existing.remove();

  const toast = document.createElement('div');
  toast.className = 'toast';
  toast.textContent = message;
  toast.style.cssText = `
    position: fixed;
    bottom: 32px;
    right: 32px;
    background: #1a1a1a;
    color: #fff;
    border: 1px solid #333;
    padding: 12px 20px;
    border-radius: 4px;
    font-family: 'DM Mono', monospace;
    font-size: 13px;
    z-index: 9000;
    animation: fadeInUp 0.3s ease both;
    letter-spacing: 0.04em;
    max-width: 320px;
  `;
  document.body.appendChild(toast);
  setTimeout(() => { toast.style.opacity = '0'; toast.style.transition = '0.3s'; setTimeout(() => toast.remove(), 300); }, duration);
}

// =====================
// AR — Room Image + Three.js
// =====================
(function initAR() {
  let scene, camera, renderer, animId;
  let arObjects = [];
  let selectedFurnitureType = 'sofa';
  let selectedObject = null;
  let objectCount = 0;

  const roomBg = document.getElementById('arRoomBg');
  const canvas = document.getElementById('arCanvas');
  const startBtn = document.getElementById('startARBtn');
  const stopBtn = document.getElementById('stopARBtn');
  const idleState = document.getElementById('arIdleState');
  const activeUI = document.getElementById('arActiveUI');
  const countEl = document.getElementById('arCount');
  const idleText = document.getElementById('arIdleText');

  if (!startBtn || !canvas) return;

  // Enable the Visualize button whenever an image is uploaded
  function checkUploadedImage() {
    const el = document.getElementById('previewImg');
    const src = el ? el.getAttribute('src') : '';
    if (src && src.length > 10) {
      startBtn.disabled = false;
      if (idleText) idleText.textContent = 'Room image ready — click Visualize Room to begin';
    } else {
      startBtn.disabled = true;
      if (idleText) idleText.textContent = 'Upload a room image first to visualize furniture';
    }
  }

  // Listen for custom event from upload section (most reliable)
  window.addEventListener('roomImageChanged', checkUploadedImage);

  // Also observe attribute changes as backup
  const uploadObserver = new MutationObserver(checkUploadedImage);
  const previewEl = document.getElementById('previewImg');
  if (previewEl) {
    uploadObserver.observe(previewEl, { attributes: true, attributeFilter: ['src'] });
  }
  // Initial check
  checkUploadedImage();

  // Furniture type selector
  document.querySelectorAll('.ar-item-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.ar-item-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      selectedFurnitureType = btn.dataset.type;
    });
  });

  function initThreeJS() {
    const w = canvas.offsetWidth || 800;
    const h = canvas.offsetHeight || 450;

    scene = new THREE.Scene();
    camera = new THREE.PerspectiveCamera(75, w / h, 0.1, 100);
    camera.position.set(0, 1.6, 3);
    camera.lookAt(0, 0, 0);

    renderer = new THREE.WebGLRenderer({ canvas: canvas, alpha: true, antialias: true });
    renderer.setSize(w, h);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;

    // Lights
    const ambient = new THREE.AmbientLight(0xffffff, 0.6);
    scene.add(ambient);

    const dirLight = new THREE.DirectionalLight(0xffffff, 0.8);
    dirLight.position.set(2, 4, 2);
    dirLight.castShadow = true;
    scene.add(dirLight);

    // Ground plane (invisible helper)
    const groundGeo = new THREE.PlaneGeometry(20, 20);
    const groundMat = new THREE.MeshBasicMaterial({ visible: false });
    const ground = new THREE.Mesh(groundGeo, groundMat);
    ground.rotation.x = -Math.PI / 2;
    ground.name = 'ground';
    scene.add(ground);

    function animate() {
      animId = requestAnimationFrame(animate);
      arObjects.forEach(obj => {
        if (obj.userData.autoRotate) {
          obj.rotation.y += 0.005;
        }
      });
      renderer.render(scene, camera);
    }
    animate();

    window.addEventListener('resize', () => {
      const w2 = canvas.offsetWidth;
      const h2 = canvas.offsetHeight;
      camera.aspect = w2 / h2;
      camera.updateProjectionMatrix();
      renderer.setSize(w2, h2);
    });
  }

  // Style-based color themes for furniture
  const STYLE_COLORS = {
    'default':                { main: 0x8B7355, accent: 0xA0522D, legs: 0x4A3728, cushion: 0xD2B48C, leaf: 0x4CAF50, pot: 0x8D6E63 },
    'Scandinavian Minimal':   { main: 0xF5F0E8, accent: 0xC4B8A5, legs: 0x3E3E3E, cushion: 0xE8DCC8, leaf: 0x7CB342, pot: 0xBCAAA4 },
    'Japandi Fusion':         { main: 0xD7CCC8, accent: 0x8D6E63, legs: 0x3E2723, cushion: 0xEFEBE9, leaf: 0x558B2F, pot: 0x5D4037 },
    'Zen Minimalism':         { main: 0xE0D8CC, accent: 0x9E9E9E, legs: 0x424242, cushion: 0xF5F5F5, leaf: 0x66BB6A, pot: 0x6D4C41 },
    'Biophilic Modern':       { main: 0xA5D6A7, accent: 0x66BB6A, legs: 0x33691E, cushion: 0xC8E6C9, leaf: 0x2E7D32, pot: 0x4E342E },
    'Rustic Contemporary':    { main: 0xA1887F, accent: 0x6D4C41, legs: 0x3E2723, cushion: 0xD7CCC8, leaf: 0x8BC34A, pot: 0x795548 },
    'Quiet Luxury':           { main: 0xBDBDBD, accent: 0x9E9E9E, legs: 0xC9B037, cushion: 0xE0E0E0, leaf: 0x43A047, pot: 0x757575 },
  };

  let currentStyle = 'default';

  function getColors(style) {
    return STYLE_COLORS[style] || STYLE_COLORS['default'];
  }

  function createFurnitureMesh(type, style) {
    const c = getColors(style || currentStyle);
    const group = new THREE.Group();
    const mat = new THREE.MeshLambertMaterial({ color: c.main });
    const darkMat = new THREE.MeshLambertMaterial({ color: c.accent });
    const legMat = new THREE.MeshLambertMaterial({ color: c.legs });

    if (type === 'sofa') {
      const base = new THREE.Mesh(new THREE.BoxGeometry(1.4, 0.35, 0.7), mat);
      base.position.y = 0.18;
      const back = new THREE.Mesh(new THREE.BoxGeometry(1.4, 0.5, 0.15), mat);
      back.position.set(0, 0.6, -0.28);
      const armL = new THREE.Mesh(new THREE.BoxGeometry(0.15, 0.3, 0.7), darkMat);
      armL.position.set(-0.68, 0.4, 0);
      const armR = armL.clone();
      armR.position.x = 0.68;
      group.add(base, back, armL, armR);
    } else if (type === 'table') {
      const top = new THREE.Mesh(new THREE.BoxGeometry(1.0, 0.06, 0.6), darkMat);
      top.position.y = 0.45;
      [[0.42, 0.22], [-0.42, 0.22], [0.42, -0.22], [-0.42, -0.22]].forEach(([x, z]) => {
        const leg = new THREE.Mesh(new THREE.CylinderGeometry(0.04, 0.04, 0.45, 8), legMat);
        leg.position.set(x, 0.22, z);
        group.add(leg);
      });
      group.add(top);
    } else if (type === 'lamp') {
      const pole = new THREE.Mesh(new THREE.CylinderGeometry(0.025, 0.025, 1.5, 8), legMat);
      pole.position.y = 0.75;
      const shade = new THREE.Mesh(new THREE.ConeGeometry(0.25, 0.4, 16, 1, true), darkMat);
      shade.position.y = 1.6;
      shade.rotation.x = Math.PI;
      const base2 = new THREE.Mesh(new THREE.CylinderGeometry(0.12, 0.12, 0.05, 16), legMat);
      base2.position.y = 0.025;
      group.add(pole, shade, base2);
    } else if (type === 'plant') {
      const potMat = new THREE.MeshLambertMaterial({ color: c.pot });
      const leafMat = new THREE.MeshLambertMaterial({ color: c.leaf });
      const pot = new THREE.Mesh(new THREE.CylinderGeometry(0.12, 0.09, 0.22, 16), potMat);
      pot.position.y = 0.11;
      const plant = new THREE.Mesh(new THREE.SphereGeometry(0.28, 16, 12), leafMat);
      plant.scale.set(1, 1.2, 1);
      plant.position.y = 0.55;
      group.add(pot, plant);
    } else if (type === 'bookshelf') {
      const frame = new THREE.Mesh(new THREE.BoxGeometry(0.8, 1.4, 0.3), darkMat);
      frame.position.y = 0.7;
      for (let i = 0; i < 4; i++) {
        const shelf = new THREE.Mesh(new THREE.BoxGeometry(0.76, 0.03, 0.28), legMat);
        shelf.position.set(0, 0.15 + i * 0.35, 0);
        group.add(shelf);
      }
      group.add(frame);
    } else if (type === 'rug') {
      const cushionMat = new THREE.MeshLambertMaterial({ color: c.cushion });
      const rug = new THREE.Mesh(new THREE.BoxGeometry(2.0, 0.02, 1.4), cushionMat);
      rug.position.y = 0.01;
      group.add(rug);
    }

    group.castShadow = true;
    group.receiveShadow = true;
    return group;
  }

  function placeObject(x, y) {
    if (!scene) return;
    const mesh = createFurnitureMesh(selectedFurnitureType);
    const spreadX = (x / canvas.offsetWidth - 0.5) * 4;
    mesh.position.set(spreadX, 0, -1 - Math.random() * 2);
    mesh.userData.autoRotate = false;
    scene.add(mesh);
    arObjects.push(mesh);
    objectCount++;
    countEl.textContent = objectCount;
    selectedObject = mesh;
    showToast(`${capitalize(selectedFurnitureType)} placed in scene`);
  }

  // Place a specific furniture type at exact 3D coordinates
  function placeFurnitureAt(type, posX, posY, posZ, rotY) {
    if (!scene) return;
    const mesh = createFurnitureMesh(type, currentStyle);
    mesh.position.set(posX, posY, posZ);
    if (rotY) mesh.rotation.y = rotY;
    mesh.userData.autoRotate = false;
    scene.add(mesh);
    arObjects.push(mesh);
    objectCount++;
    countEl.textContent = objectCount;
    selectedObject = mesh;
  }

  // Auto-place a curated set of furniture to visualize the room
  function autoPlaceFurniture(style) {
    currentStyle = style || 'default';
    // Clear any existing objects first
    arObjects.forEach(obj => scene && scene.remove(obj));
    arObjects = [];
    objectCount = 0;

    // Layout: spread furniture across the room naturally
    // Sofa - center-left foreground
    placeFurnitureAt('sofa', -0.8, 0, -1.0, 0.15);
    // Table - center, in front of sofa
    placeFurnitureAt('table', 0.0, 0, -0.3, 0);
    // Lamp - far right
    placeFurnitureAt('lamp', 1.6, 0, -1.5, 0);
    // Plant - near right
    placeFurnitureAt('plant', 1.0, 0, -0.5, 0);
    // Rug - under the table area
    placeFurnitureAt('rug', 0.0, 0, -0.8, 0.1);
    // Bookshelf - far left background
    placeFurnitureAt('bookshelf', -1.8, 0, -2.2, 0.3);

    countEl.textContent = objectCount;
    showToast(`Placed ${objectCount} furniture items — ${currentStyle} style`);
  }

  canvas.addEventListener('click', e => {
    if (!scene) return;
    const rect = canvas.getBoundingClientRect();
    placeObject(e.clientX - rect.left, e.clientY - rect.top);
  });

  // Control buttons
  document.getElementById('rotateBtn')?.addEventListener('click', () => {
    if (selectedObject) selectedObject.userData.autoRotate = !selectedObject.userData.autoRotate;
    showToast('Rotating selected object');
  });

  document.getElementById('scaleUpBtn')?.addEventListener('click', () => {
    if (selectedObject) selectedObject.scale.multiplyScalar(1.15);
    showToast('Scaled up');
  });

  document.getElementById('scaleDownBtn')?.addEventListener('click', () => {
    if (selectedObject) selectedObject.scale.multiplyScalar(0.87);
    showToast('Scaled down');
  });

  document.getElementById('resetSceneBtn')?.addEventListener('click', () => {
    arObjects.forEach(obj => scene && scene.remove(obj));
    arObjects = [];
    objectCount = 0;
    countEl.textContent = '0';
    selectedObject = null;
    showToast('Scene reset');
  });

  // Expose a function to start AR from outside (used by Gallery "View in AR")
  window.__startARWithRoom = function(style) {
    const el = document.getElementById('previewImg');
    const src = el ? el.getAttribute('src') : '';
    if (!src || src.length < 10) {
      showToast('Please upload a room image first in the Upload Room section');
      return;
    }
    // Store requested style for when startBtn fires
    if (style) window.__arRequestedStyle = style;
    // If already running, just re-place with new style
    if (scene) {
      autoPlaceFurniture(style || 'default');
      return;
    }
    startBtn.click();
  };

  startBtn.addEventListener('click', () => {
    const el = document.getElementById('previewImg');
    const src = el ? el.getAttribute('src') : '';
    if (!src || src.length < 10) {
      showToast('Please upload a room image first');
      return;
    }

    // Show uploaded room image as background
    roomBg.src = src;
    roomBg.style.display = 'block';
    idleState.style.display = 'none';
    activeUI.style.display = 'block';
    initThreeJS();

    // Auto-place furniture after a short delay for Three.js to settle
    const requestedStyle = window.__arRequestedStyle || 'default';
    window.__arRequestedStyle = null;
    setTimeout(() => autoPlaceFurniture(requestedStyle), 300);
  });

  stopBtn.addEventListener('click', () => {
    roomBg.src = '';
    roomBg.style.display = 'none';
    if (animId) cancelAnimationFrame(animId);
    if (renderer) {
      renderer.dispose();
      renderer = null;
    }
    scene = null;
    arObjects = [];
    objectCount = 0;
    countEl.textContent = '0';
    selectedObject = null;
    idleState.style.display = 'flex';
    activeUI.style.display = 'none';
    checkUploadedImage();
    showToast('AR visualization stopped');
  });
})();

// =====================
// AI BUDDY CHAT
// =====================
(function initChat() {
  const messagesEl = document.getElementById('chatMessages');
  const input = document.getElementById('chatInput');
  const sendBtn = document.getElementById('sendBtn');
  const typingIndicator = document.getElementById('chatTyping');
  const clearBtn = document.getElementById('clearChatBtn');
  const quickReplies = document.getElementById('quickReplies');

  if (!input) return;

  const aiResponses = {
    default: [
      "Great question! For your space, I'd recommend starting with a neutral base palette — warm whites and natural wood tones work beautifully for creating a serene environment.",
      "Based on current design trends, Japandi style (Japanese + Scandinavian fusion) is extremely popular. It emphasizes clean lines, natural materials, and functional beauty.",
      "I've analyzed similar spaces and found that layered lighting — ambient, task, and accent — dramatically transforms any room's atmosphere.",
      "For your room type, I suggest the Oslo Sofa as your anchor piece, complemented by the Nord Coffee Table. This combination creates visual harmony while maintaining flow.",
      "Would you like me to generate a complete design mood board for your space? I can factor in your room dimensions and natural light conditions.",
    ],
    sofa: [
      "🛋 Excellent choice! For a modern sofa, I recommend the Oslo Sofa in warm linen — it pairs beautifully with Scandinavian interiors. Available in 2-seater and 3-seater configurations.\n\nPrice range: ₹65,000 – ₹1,20,000\nDelivery: 3–4 weeks\n\nShall I book a consultation or add this to your wishlist?",
      "🛋 For your living room, the Drift Sectional in charcoal gray would be stunning. Its modular design lets you reconfigure based on your space. Want me to check availability?",
    ],
    booking: [
      "📦 I'd be happy to help you book! Here's what you need:\n\n1. Confirm your delivery address\n2. Choose a delivery slot (Mon–Sat)\n3. Select assembly preference\n\nShall I initiate the booking process? I'll need your preferred date.",
      "✅ Booking initiated! Your furniture will be reserved for 24 hours. To confirm, simply share your delivery details and I'll finalize everything.",
    ],
    budget: [
      "💰 Budget Planning for a Living Room:\n\n• Sofa: ₹65,000 – ₹1,20,000\n• Coffee Table: ₹15,000 – ₹35,000\n• Lighting: ₹10,000 – ₹25,000\n• Accent Chairs: ₹25,000 – ₹50,000\n• Décor & Plants: ₹8,000 – ₹15,000\n\nEstimated Total: ₹1.23L – ₹2.45L\n\nI can help you optimize within your specific budget!",
    ],
    trend: [
      "🎨 Top Interior Design Trends 2025:\n\n• Japandi minimalism with warm neutrals\n• Biophilic design with natural textures\n• Curved furniture replacing sharp edges\n• Quiet luxury — understated, premium materials\n• Multifunctional furniture for compact spaces\n\nWhich trend resonates with your taste?",
    ],
    layout: [
      "📐 Room Planning Tips:\n\n1. Define zones — seating, dining, workspace\n2. Maintain 90cm walkways between furniture\n3. Anchor with a large area rug\n4. Face seating toward a focal point\n5. Use vertical space for storage\n\nWant me to visualize a layout in AR? Just head to the AR Designer section!",
    ],
  };

  function getAIResponse(userMsg) {
    const lower = userMsg.toLowerCase();
    if (lower.includes('sofa') || lower.includes('couch')) return getRandom(aiResponses.sofa);
    if (lower.includes('book') || lower.includes('order') || lower.includes('buy') || lower.includes('purchase')) return getRandom(aiResponses.booking);
    if (lower.includes('budget') || lower.includes('cost') || lower.includes('price') || lower.includes('estimate')) return getRandom(aiResponses.budget);
    if (lower.includes('trend') || lower.includes('trending') || lower.includes('popular') || lower.includes('latest')) return getRandom(aiResponses.trend);
    if (lower.includes('layout') || lower.includes('plan') || lower.includes('arrange') || lower.includes('room')) return getRandom(aiResponses.layout);
    return getRandom(aiResponses.default);
  }

  function getRandom(arr) {
    return arr[Math.floor(Math.random() * arr.length)];
  }

  function formatTime() {
    return new Date().toLocaleTimeString('en', { hour: '2-digit', minute: '2-digit' });
  }

  function appendMessage(role, text) {
    const wrap = document.createElement('div');
    wrap.className = `message ${role === 'user' ? 'user-message' : 'bot-message'}`;
    const avatar = role === 'user' ? 'U' : 'B';
    wrap.innerHTML = `
      <div class="msg-avatar">${avatar}</div>
      <div class="msg-content">
        <div class="msg-bubble">${text.replace(/\n/g, '<br>')}</div>
        <div class="msg-time">${formatTime()}</div>
      </div>
    `;
    messagesEl.appendChild(wrap);
    messagesEl.scrollTo({ top: messagesEl.scrollHeight, behavior: 'smooth' });
  }

  function showTyping() {
    if (typingIndicator) typingIndicator.style.display = 'block';
  }

  function hideTyping() {
    if (typingIndicator) typingIndicator.style.display = 'none';
  }

  window.sendMessage = async function(overrideText) {
    const text = overrideText || input.value.trim();
    if (!text) return;
    input.value = '';

    // Remove quick replies after first message
    if (quickReplies) quickReplies.remove();

    appendMessage('user', text);
    showTyping();

    try {
      const res = await fetch(API_BASE + '/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text }),
      });
      const data = await res.json();
      hideTyping();
      if (data.success) {
        appendMessage('bot', data.response);
      } else {
        appendMessage('bot', getAIResponse(text));
      }
    } catch (err) {
      // Fallback to client-side responses if backend is unavailable
      hideTyping();
      appendMessage('bot', getAIResponse(text));
    }
  };

  sendBtn.addEventListener('click', () => sendMessage());

  input.addEventListener('keypress', e => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  });

  clearBtn?.addEventListener('click', () => {
    messagesEl.innerHTML = '';
    appendMessage('bot', "Chat cleared! I'm ready to help you with your next interior design challenge. What are you working on?");
  });

  // Quick replies
  document.querySelectorAll('.quick-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const msg = btn.dataset.msg;
      input.value = msg;
      sendMessage(msg);
    });
  });
})();

// =====================
// VOICE RECOGNITION
// =====================
(function initVoice() {
  const micBtn = document.getElementById('micBtn');
  const chatInput = document.getElementById('chatInput');
  if (!micBtn) return;

  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

  if (!SpeechRecognition) {
    micBtn.title = 'Voice not supported in this browser';
    micBtn.style.opacity = '0.4';
    micBtn.addEventListener('click', () => showToast('Voice recognition not supported. Try Chrome.'));
    return;
  }

  const recognition = new SpeechRecognition();
  recognition.continuous = false;
  recognition.interimResults = false;
  recognition.lang = 'en-IN';

  let isListening = false;

  recognition.onstart = () => {
    isListening = true;
    micBtn.classList.add('active');
    showToast('🎤 Listening... speak now');
  };

  recognition.onresult = e => {
    const transcript = e.results[0][0].transcript;
    if (chatInput) chatInput.value = transcript;
    showToast(`Heard: "${transcript}"`);
    setTimeout(() => window.sendMessage(transcript), 300);
  };

  recognition.onerror = e => {
    isListening = false;
    micBtn.classList.remove('active');
    if (e.error === 'not-allowed') showToast('Microphone permission denied.');
    else showToast('Voice recognition error. Try again.');
  };

  recognition.onend = () => {
    isListening = false;
    micBtn.classList.remove('active');
  };

  micBtn.addEventListener('click', () => {
    if (isListening) {
      recognition.stop();
    } else {
      try {
        recognition.start();
      } catch (err) {
        showToast('Could not start voice recognition.');
      }
    }
  });
})();

// =====================
// GALLERY
// =====================
(function initGallery() {
  const grid = document.getElementById('galleryGrid');
  if (!grid) return;

  const galleryItems = [
    { emoji: '🏠', style: 'Scandinavian Minimal', name: 'White Light Studio' },
    { emoji: '🛋', style: 'Japandi Fusion', name: 'Warm Wabi Living Room' },
    { emoji: '🍵', style: 'Zen Minimalism', name: 'Tea House Bedroom' },
    { emoji: '🌿', style: 'Biophilic Modern', name: 'Green Sanctuary' },
    { emoji: '🪵', style: 'Rustic Contemporary', name: 'Oak & Stone Study' },
    { emoji: '🕯', style: 'Quiet Luxury', name: 'Candlelight Dining' },
  ];

  galleryItems.forEach((item, i) => {
    const el = document.createElement('div');
    el.className = 'gallery-item';
    el.style.animationDelay = `${i * 0.08}s`;
    el.innerHTML = `
      <div class="gallery-img">${item.emoji}</div>
      <div class="gallery-overlay">
        <div class="gallery-info">
          <div class="gallery-style">${item.style}</div>
          <div class="gallery-name">${item.name}</div>
          <button class="gallery-view-btn" onclick="viewInAR('${item.name}')">View in AR</button>
        </div>
      </div>
    `;
    grid.appendChild(el);
  });
})();

// Map gallery names to style keys for themed furniture colors
const GALLERY_STYLE_MAP = {
  'White Light Studio': 'Scandinavian Minimal',
  'Warm Wabi Living Room': 'Japandi Fusion',
  'Tea House Bedroom': 'Zen Minimalism',
  'Green Sanctuary': 'Biophilic Modern',
  'Oak & Stone Study': 'Rustic Contemporary',
  'Candlelight Dining': 'Quiet Luxury',
};

function viewInAR(name) {
  document.getElementById('ar').scrollIntoView({ behavior: 'smooth' });
  const style = GALLERY_STYLE_MAP[name] || 'default';
  showToast(`Visualizing "${name}" (${style}) in your room...`);
  // Auto-start AR with the uploaded room image and style-themed furniture
  setTimeout(() => {
    if (window.__startARWithRoom) window.__startARWithRoom(style);
  }, 600);
}

// =====================
// UTILITY
// =====================
function capitalize(str) {
  return str.charAt(0).toUpperCase() + str.slice(1);
}

function categoryEmoji(cat) {
  const map = { seating: '🛋', tables: '🪵', lighting: '💡', storage: '📚' };
  return map[cat] || '🪑';
}

function mapCategory(cat) {
  // Ensure backend category names match frontend filter values
  const map = { seating: 'seating', tables: 'tables', lighting: 'lighting', storage: 'storage' };
  return map[cat] || cat;
}

// =====================
// HERO PARALLAX
// =====================
(function initParallax() {
  const heroBg = document.querySelector('.hero-bg-grid');
  if (!heroBg) return;

  window.addEventListener('scroll', () => {
    const scrollY = window.scrollY;
    heroBg.style.transform = `translateY(${scrollY * 0.3}px)`;
  }, { passive: true });
})();

// =====================
// NAV CTA SCROLL
// =====================
document.querySelector('.nav-cta')?.addEventListener('click', () => {
  document.getElementById('upload').scrollIntoView({ behavior: 'smooth' });
});

// =====================
// HERO BUTTONS SCROLL
// =====================
document.querySelectorAll('[href="#upload"]').forEach(el => {
  el.addEventListener('click', e => {
    e.preventDefault();
    document.getElementById('upload').scrollIntoView({ behavior: 'smooth' });
  });
});

document.querySelectorAll('[href="#ar"]').forEach(el => {
  el.addEventListener('click', e => {
    e.preventDefault();
    document.getElementById('ar').scrollIntoView({ behavior: 'smooth' });
  });
});

// =====================
// THEME TOGGLE
// =====================
(function initThemeToggle() {
  const toggle = document.getElementById('themeToggle');
  if (!toggle) return;

  const DARK = 'dark-theme';
  const saved = localStorage.getItem('gruha-theme');
  if (saved === DARK) document.body.classList.add(DARK);

  toggle.addEventListener('click', () => {
    const isDark = document.body.classList.toggle(DARK);
    localStorage.setItem('gruha-theme', isDark ? DARK : 'light');
    showToast(isDark ? '🌙 Dark theme activated' : '☀️ Light theme activated', 1800);
  });
})();

console.log('%cGruha Alankara 🏠', 'font-size: 20px; font-weight: bold; color: white; background: black; padding: 10px 20px;');
console.log('%cAI + AR Interior Design Platform — v1.0', 'font-size: 12px; color: #888;');
