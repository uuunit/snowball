/**
 * 滚雪球 - 公共脚本
 * 字号调节 | 阅读进度条 | 键盘翻页 | 阅读进度记忆 | 返回顶部 | 全文搜索
 */
(function() {
  'use strict';

  // ===== 字号调节 =====
  var fs = 1;
  window.adjFont = function(d) {
    fs = Math.max(.8, Math.min(1.6, fs + d * .1));
    document.documentElement.style.fontSize = fs + 'em';
    try { localStorage.setItem('snowball-fs', fs); } catch(e) {}
  };

  // ===== 页面标识（用于阅读进度记忆 key）=====
  var PATH = location.pathname.split('/').pop() || 'index.html';

  // ===== DOM Ready =====
  window.addEventListener('load', function() {
    // 恢复字号
    try {
      var s = parseFloat(localStorage.getItem('snowball-fs'));
      if (s) { fs = s; document.documentElement.style.fontSize = fs + 'em'; }
    } catch(e) {}

    // 恢复阅读位置（跳过锚点跳转的情况）
    if (!location.hash) {
      try {
        var pos = parseFloat(localStorage.getItem('snowball-pos-' + PATH));
        if (pos && pos > 60) {
          setTimeout(function() { window.scrollTo(0, pos); }, 80);
        }
      } catch(e) {}
    }
  });

  // ===== 滚动：进度条 + 返回顶部 + 防抖存位置 =====
  var scrollTimer;
  window.addEventListener('scroll', function() {
    var h = document.documentElement.scrollHeight - window.innerHeight;
    var p = h > 0 ? Math.min(100, Math.max(0, window.scrollY / h * 100)) : 0;
    var fill = document.getElementById('progressFill');
    if (fill) fill.style.width = p + '%';

    // 返回顶部按钮
    var bt = document.getElementById('backTop');
    if (bt) bt.classList.toggle('show', window.scrollY > 400);

    // 防抖存储阅读位置
    clearTimeout(scrollTimer);
    scrollTimer = setTimeout(function() {
      try { localStorage.setItem('snowball-pos-' + PATH, window.scrollY); } catch(e) {}
    }, 400);
  }, { passive: true });

  // ===== 键盘翻页 =====
  document.addEventListener('keydown', function(e) {
    // 搜索框内不翻页
    var tag = (e.target.tagName || '').toUpperCase();
    if (tag === 'INPUT' || tag === 'TEXTAREA') return;
    // 搜索模态打开时不翻页
    var modal = document.getElementById('searchModal');
    if (modal && modal.style.display === 'flex') {
      if (e.key === 'Escape') toggleSearch();
      return;
    }
    var nav = document.querySelector('.page-nav');
    if (!nav) return;
    if (e.key === 'ArrowLeft' && nav.dataset.prev) location.href = nav.dataset.prev;
    if (e.key === 'ArrowRight' && nav.dataset.next) location.href = nav.dataset.next;
  });

  // ===== 返回顶部 =====
  window.backToTop = function() {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  // ===== 全文搜索 =====
  var searchData = null;
  var searchTimer = null;

  function loadSearch() {
    if (searchData !== null) return Promise.resolve(searchData);
    return fetch('search-index.json').then(function(r) { return r.json(); }).then(function(d) {
      searchData = d;
      return d;
    }).catch(function() { searchData = []; return []; });
  }

  window.toggleSearch = function() {
    var modal = document.getElementById('searchModal');
    if (!modal) return;
    if (modal.style.display === 'flex') {
      modal.style.display = 'none';
      var results = document.getElementById('searchResults');
      if (results) results.innerHTML = '';
      var input = document.getElementById('searchInput');
      if (input) input.value = '';
    } else {
      modal.style.display = 'flex';
      var input = document.getElementById('searchInput');
      if (input) setTimeout(function() { input.focus(); }, 60);
    }
  };

  window.onSearchInput = function(q) {
    clearTimeout(searchTimer);
    searchTimer = setTimeout(function() {
      var results = document.getElementById('searchResults');
      if (!results) return;
      q = (q || '').trim();
      if (q.length < 2) { results.innerHTML = ''; return; }
      results.innerHTML = '<div class="search-loading">搜索中…</div>';
      loadSearch().then(function(data) {
        var matches = [];
        for (var i = 0; i < data.length; i++) {
          var ch = data[i];
          // 搜标题/副标题
          if (ch.title.indexOf(q) >= 0 || ch.subtitle.indexOf(q) >= 0) {
            matches.push({ n: ch.n, title: ch.title, para: 0, snippet: ch.subtitle || ch.title });
          }
          // 搜段落摘要
          for (var j = 0; j < ch.paras.length; j++) {
            var p = ch.paras[j];
            var idx = p.s.indexOf(q);
            if (idx >= 0) {
              var start = Math.max(0, idx - 10);
              var end = Math.min(p.s.length, idx + q.length + 12);
              matches.push({ n: ch.n, title: ch.title, para: p.i, snippet: '…' + p.s.slice(start, end) + '…' });
            }
          }
        }
        if (matches.length === 0) {
          results.innerHTML = '<div class="search-empty">未找到「' + q + '」相关内容</div>';
        } else {
          results.innerHTML = matches.slice(0, 30).map(function(r) {
            var href = 'ch' + String(r.n).padStart(2, '0') + '.html' + (r.para ? '#para-' + r.para : '');
            return '<a href="' + href + '" class="search-result">' +
              '<span class="sr-ch">第' + r.n + '章</span>' +
              '<span class="sr-title">' + r.title + '</span>' +
              '<span class="sr-snippet">' + r.snippet + '</span>' +
              '</a>';
          }).join('');
        }
      });
    }, 200);
  };

})();
