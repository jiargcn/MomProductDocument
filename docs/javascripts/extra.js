/* 侧边栏导航修复 */
(function() {
  function setupNavAndStyles() {
    // 导航 checkbox toggle 修复
    var toggles = document.querySelectorAll('.md-nav__toggle');
    toggles.forEach(function(toggle) {
      toggle.addEventListener('change', function(e) {
        var isChecked = this.checked;
        var nav = this.nextElementSibling;
        while (nav && nav.tagName !== 'NAV') {
          nav = nav.nextElementSibling;
        }
        if (nav && nav.tagName === 'NAV') {
          nav.setAttribute('aria-expanded', isChecked);
        }
      });

      if (toggle.checked) {
        var nav = toggle.nextElementSibling;
        while (nav && nav.tagName !== 'NAV') {
          nav = nav.nextElementSibling;
        }
        if (nav && nav.tagName === 'NAV') {
          nav.setAttribute('aria-expanded', 'true');
        }
      }
    });

    // 一级导航项样式 - 直接设置内联样式确保生效
    var sectionItems = document.querySelectorAll('.md-nav__item--section > .md-nav__link');
    sectionItems.forEach(function(link) {
      link.style.color = '#4051b5';
      link.style.fontWeight = '700';
      link.style.cursor = 'default';
    });
  }

  // Material theme uses document$ for SPA-like navigation
  if (typeof document$ !== 'undefined') {
    document$.subscribe(function() {
      setTimeout(setupNavAndStyles, 100);
    });
  }

  // Fallback: also run on DOMContentLoaded and load events
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', setupNavAndStyles);
  } else {
    // DOM already ready, but still delay to ensure Material theme is done
    setTimeout(setupNavAndStyles, 100);
  }
})();

/* 占位符标红功能 */
(function() {
  function highlightPendingPlaceholders() {
    var placeholderKeywords = ['待确认', '待截图确认', '待补充'];
    var allElements = document.querySelectorAll('*');

    allElements.forEach(function(el) {
      // Skip elements that are parents of other elements (avoid double-wrapping)
      if (el.children.length > 0) return;

      var text = el.textContent || '';
      for (var i = 0; i < placeholderKeywords.length; i++) {
        if (text.includes(placeholderKeywords[i])) {
          el.style.color = '#d32f2f';
          el.style.backgroundColor = 'rgba(211, 47, 47, 0.1)';
          el.style.padding = '0.1em 0.3em';
          el.style.borderRadius = '0.2em';
          el.style.fontWeight = '500';
          break;
        }
      }
    });
  }

  if (typeof document$ !== 'undefined') {
    document$.subscribe(function() {
      setTimeout(highlightPendingPlaceholders, 100);
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', highlightPendingPlaceholders);
  } else {
    setTimeout(highlightPendingPlaceholders, 100);
  }
})();

/* Mermaid 弹窗功能 */
(function() {
  function initMermaidModal() {
    var mermaids = document.querySelectorAll('.mermaid');
    if (mermaids.length === 0) return;

    // 移除已存在的弹窗
    var existingModal = document.querySelector('.mermaid-modal');
    if (existingModal) existingModal.remove();

    // 创建弹窗元素
    var modal = document.createElement('div');
    modal.className = 'mermaid-modal';
    modal.innerHTML = '<div class="mermaid-modal-content"><button class="mermaid-modal-close">×</button><div class="mermaid-modal-body"></div><div class="mermaid-zoom-controls"><button class="mermaid-zoom-btn" data-action="zoom-in">+</button><button class="mermaid-zoom-btn" data-action="zoom-out">-</button><button class="mermaid-zoom-btn" data-action="reset">R</button></div></div>';
    document.body.appendChild(modal);

    var modalContent = modal.querySelector('.mermaid-modal-body');
    var closeBtn = modal.querySelector('.mermaid-modal-close');
    var zoomInBtn = modal.querySelector('[data-action="zoom-in"]');
    var zoomOutBtn = modal.querySelector('[data-action="zoom-out"]');
    var resetBtn = modal.querySelector('[data-action="reset"]');

    var currentScale = 1;
    var isDragging = false;
    var startX, startY, translateX = 0, translateY = 0;

    // 点击 mermaid 图表打开弹窗
    mermaids.forEach(function(mermaid) {
      mermaid.addEventListener('click', function(e) {
        e.preventDefault();
        e.stopPropagation();

        var svg = mermaid.querySelector('svg');
        if (svg) {
          modalContent.innerHTML = '';
          var clonedSvg = svg.cloneNode(true);
          clonedSvg.style.transform = 'scale(1) translate(0, 0)';
          clonedSvg.style.transition = 'transform 0.2s ease';
          modalContent.appendChild(clonedSvg);

          currentScale = 1;
          translateX = 0;
          translateY = 0;
          modal.classList.add('active');
        }
      });
    });

    // 关闭弹窗
    closeBtn.addEventListener('click', function() {
      modal.classList.remove('active');
    });

    modal.addEventListener('click', function(e) {
      if (e.target === modal) {
        modal.classList.remove('active');
      }
    });

    // 缩放功能
    zoomInBtn.addEventListener('click', function() {
      currentScale = Math.min(currentScale + 0.2, 3);
      var svg = modalContent.querySelector('svg');
      if (svg) {
        svg.style.transform = 'scale(' + currentScale + ') translate(' + translateX + 'px, ' + translateY + 'px)';
      }
    });

    zoomOutBtn.addEventListener('click', function() {
      currentScale = Math.max(currentScale - 0.2, 0.3);
      var svg = modalContent.querySelector('svg');
      if (svg) {
        svg.style.transform = 'scale(' + currentScale + ') translate(' + translateX + 'px, ' + translateY + 'px)';
      }
    });

    resetBtn.addEventListener('click', function() {
      currentScale = 1;
      translateX = 0;
      translateY = 0;
      var svg = modalContent.querySelector('svg');
      if (svg) {
        svg.style.transform = 'scale(1) translate(0, 0)';
      }
    });

    // 拖拽功能
    var modalContentEl = modal.querySelector('.mermaid-modal-content');

    modalContentEl.addEventListener('mousedown', function(e) {
      if (e.target.tagName === 'svg' || e.target.tagName === 'path' || e.target.tagName === 'rect' || e.target.tagName === 'circle' || e.target.tagName === 'line' || e.target.tagName === 'text' || e.target.tagName === 'g') {
        isDragging = true;
        startX = e.clientX - translateX;
        startY = e.clientY - translateY;
        modalContentEl.style.cursor = 'grabbing';
      }
    });

    document.addEventListener('mousemove', function(e) {
      if (!isDragging) return;
      translateX = e.clientX - startX;
      translateY = e.clientY - startY;
      var svg = modalContent.querySelector('svg');
      if (svg) {
        svg.style.transform = 'scale(' + currentScale + ') translate(' + translateX + 'px, ' + translateY + 'px)';
      }
    });

    document.addEventListener('mouseup', function() {
      isDragging = false;
      modalContentEl.style.cursor = 'pointer';
    });
  }

  // Material theme uses document$ for SPA-like navigation
  if (typeof document$ !== 'undefined') {
    document$.subscribe(function() {
      setTimeout(initMermaidModal, 100);
    });
  }

  // Fallback
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initMermaidModal);
  } else {
    setTimeout(initMermaidModal, 100);
  }
})();