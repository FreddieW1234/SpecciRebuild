// ---- Tab switching ----
document.addEventListener('DOMContentLoaded', function () {

  // Tab navigation via data-tab buttons
  document.querySelectorAll('[data-tab]').forEach(function (btn) {
    btn.addEventListener('click', function (e) {
      e.preventDefault();
      var target = this.dataset.tab;
      var container = this.closest('.tabs');
      if (!container) return;

      container.querySelectorAll('.tab-btn').forEach(function (b) { b.classList.remove('active'); });
      container.querySelectorAll('.tab-panel').forEach(function (p) { p.classList.remove('active'); });

      this.classList.add('active');
      var panel = container.querySelector('#' + target);
      if (panel) panel.classList.add('active');

      // Update URL hash without scrolling
      history.replaceState(null, '', '#' + target);
    });
  });

  // Activate tab from URL hash on load
  var hash = window.location.hash.replace('#', '');
  if (hash) {
    var btn = document.querySelector('[data-tab="' + hash + '"]');
    if (btn) btn.click();
  }

  // ---- Dynamic inline table rows ----
  document.querySelectorAll('[data-add-row]').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var tableId = this.dataset.addRow;
      var tbody = document.querySelector('#' + tableId + ' tbody');
      var template = document.querySelector('#' + tableId + '-row-template');
      if (!tbody || !template) return;
      var idx = tbody.querySelectorAll('tr').length;
      var html = template.innerHTML.replace(/__IDX__/g, idx);
      var tr = document.createElement('tr');
      tr.innerHTML = html;
      tbody.appendChild(tr);
    });
  });

  // ---- Remove inline table row ----
  document.addEventListener('click', function (e) {
    if (e.target.closest('[data-remove-row]')) {
      var btn = e.target.closest('[data-remove-row]');
      var tr = btn.closest('tr');
      if (tr) tr.remove();
    }
  });

  // ---- Confirm delete forms ----
  document.querySelectorAll('[data-confirm]').forEach(function (el) {
    el.addEventListener('submit', function (e) {
      if (!confirm(this.dataset.confirm || 'Are you sure?')) {
        e.preventDefault();
      }
    });
  });

  // ---- Auto-dismiss flash messages ----
  setTimeout(function () {
    document.querySelectorAll('.flash-messages .alert').forEach(function (el) {
      el.style.transition = 'opacity .5s';
      el.style.opacity = '0';
      setTimeout(function () { el.remove(); }, 500);
    });
  }, 5000);

});
