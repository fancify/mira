"""Settings console page — GET /settings."""


def render_settings_page() -> str:
    from vibe.topbar import theme_vars_css, topbar_css, topbar_html, settings_overlay_html, topbar_js
    _theme_css = theme_vars_css()
    _tb_css    = topbar_css()
    _tb_html   = topbar_html(title="设置", back_url="/")
    _overlays  = settings_overlay_html()
    _tb_js     = topbar_js()

    page_css = r"""
  a { color: inherit; text-decoration: none; }

  /* ── tab bar ── */
  .console-tabs {
    position: sticky; top: 48px; z-index: 90;
    display: flex; gap: 0; background: var(--panel);
    border-bottom: 1px solid var(--border);
  }
  .tab-btn {
    flex: 1; padding: 10px 0; text-align: center;
    font-size: 13px; font-family: var(--mono);
    color: var(--sub); background: none; border: none;
    cursor: pointer; transition: all .15s;
    border-bottom: 2px solid transparent;
  }
  .tab-btn.active { color: var(--accent); border-bottom-color: var(--accent); font-weight: 600; }
  .tab-btn:hover { color: var(--text); }

  /* ── main area ── */
  .console-main { max-width: 900px; margin: 0 auto; padding: 20px 20px 60px; }
  .tab-panel { display: none; }
  .tab-panel.active { display: block; }

  /* ── section card ── */
  .cfg-section {
    background: var(--panel); border: 1px solid var(--border);
    border-radius: var(--radius); padding: 20px; margin-bottom: 16px;
  }
  .cfg-section h3 {
    font-size: 13px; font-weight: 600; color: var(--text);
    margin-bottom: 14px;
  }

  /* ── form elements ── */
  .cfg-row { display: flex; align-items: center; gap: 10px; margin-bottom: 10px; }
  .cfg-row label { min-width: 80px; font-size: 12px; color: var(--sub); flex-shrink: 0; }
  .cfg-input {
    flex: 1; padding: 6px 10px; font-size: 12px; font-family: var(--mono);
    background: var(--bg); color: var(--text);
    border: 1px solid var(--border); border-radius: var(--radius-sm);
    outline: none; transition: border-color .15s;
  }
  .cfg-input:focus { border-color: var(--accent); }
  select.cfg-input { cursor: pointer; }
  textarea.cfg-input { resize: vertical; min-height: 60px; }

  .cfg-btn {
    padding: 6px 16px; font-size: 12px; font-family: var(--mono);
    border: 1px solid var(--accent); color: var(--accent);
    background: none; border-radius: var(--radius-sm);
    cursor: pointer; transition: all .15s;
  }
  .cfg-btn:hover { background: var(--accent); color: #fff; }
  .cfg-btn.primary { background: var(--accent); color: #fff; }
  .cfg-btn.danger { border-color: #e55; color: #e55; }
  .cfg-btn.danger:hover { background: #e55; color: #fff; }
  .cfg-btn.small { padding: 3px 10px; font-size: 11px; }

  /* ── key list ── */
  .key-item {
    display: grid; grid-template-columns: auto 1fr auto auto;
    align-items: center; gap: 10px;
    padding: 10px 0; border-bottom: 1px solid var(--border);
  }
  .key-item:last-child { border-bottom: none; }
  .key-badge {
    font-size: 10px; padding: 2px 8px; border-radius: 10px;
    font-weight: 600; text-transform: uppercase;
  }
  .key-badge.ai       { background: rgba(168,130,255,.15); color: #a882ff; }
  .key-badge.cloud     { background: rgba(80,200,120,.15); color: #50c878; }
  .key-badge.database  { background: rgba(240,160,80,.15); color: #f0a050; }
  .key-badge.other     { background: rgba(160,160,160,.15); color: #a0a0a0; }

  .key-name { font-size: 12px; color: var(--text); font-weight: 500; }
  .key-val  { font-size: 11px; color: var(--sub); font-family: var(--mono); }
  .key-note { font-size: 11px; color: var(--sub); margin-top: 2px; }
  .key-actions { display: flex; gap: 6px; }

  .key-form { display: none; margin-bottom: 16px; padding: 14px;
              background: rgba(var(--accent-rgb),.04); border-radius: var(--radius);
              border: 1px dashed rgba(var(--accent-rgb),.2); }
  .key-form.show { display: block; }
  .key-form-title { font-size: 12px; color: var(--accent); font-weight: 600; margin-bottom: 10px; }

  /* ── project layout ── */
  .proj-layout { display: grid; grid-template-columns: 240px 1fr; gap: 16px; min-height: 400px; }
  .proj-list {
    background: var(--panel); border: 1px solid var(--border);
    border-radius: var(--radius); overflow-y: auto; max-height: 520px;
  }
  .proj-item {
    padding: 10px 14px; font-size: 12px; color: var(--sub);
    cursor: pointer; border-bottom: 1px solid var(--border);
    transition: all .1s; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
  }
  .proj-item:hover { color: var(--text); background: rgba(var(--accent-rgb),.06); }
  .proj-item.active { color: var(--accent); background: rgba(var(--accent-rgb),.1); font-weight: 600; }
  .proj-editor {
    background: var(--panel); border: 1px solid var(--border);
    border-radius: var(--radius); padding: 20px;
  }
  .proj-editor-empty { display: flex; align-items: center; justify-content: center;
                       color: var(--sub); font-size: 13px; }

  /* bound keys chips */
  .bound-keys { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 4px; }
  .bound-chip {
    display: inline-flex; align-items: center; gap: 4px;
    padding: 3px 10px; font-size: 11px; border-radius: 12px;
    background: rgba(var(--accent-rgb),.1); color: var(--accent);
  }
  .bound-chip .remove { cursor: pointer; opacity: .6; font-size: 13px; }
  .bound-chip .remove:hover { opacity: 1; }

  /* ── list rows (scan_dirs, excludes) ── */
  .list-row { display: flex; align-items: center; gap: 8px; margin-bottom: 6px; }
  .list-row .cfg-input { flex: 1; }
  .list-row .remove-btn {
    width: 24px; height: 24px; display: flex; align-items: center; justify-content: center;
    background: none; border: 1px solid var(--border); border-radius: var(--radius-sm);
    color: var(--sub); cursor: pointer; font-size: 14px; transition: all .15s;
  }
  .list-row .remove-btn:hover { border-color: #e55; color: #e55; }

  /* ── toast ── */
  .toast {
    position: fixed; bottom: 24px; right: 24px; z-index: 999;
    padding: 10px 20px; border-radius: var(--radius);
    font-size: 12px; font-family: var(--mono); color: #fff;
    opacity: 0; transform: translateY(10px);
    transition: opacity .25s, transform .25s;
    pointer-events: none;
  }
  .toast.show { opacity: 1; transform: translateY(0); }
  .toast.success { background: #2ea043; }
  .toast.error   { background: #e55; }

  /* ── responsive ── */
  @media (max-width: 700px) {
    .proj-layout { grid-template-columns: 1fr; }
    .proj-list { max-height: 200px; }
    .key-item { grid-template-columns: 1fr; gap: 4px; }
  }
"""

    page_html = f"""
{_tb_html}

<div class="console-tabs">
  <button class="tab-btn active" onclick="switchTab('keys')">密钥管理</button>
  <button class="tab-btn" onclick="switchTab('projects')">项目配置</button>
  <button class="tab-btn" onclick="switchTab('system')">系统设置</button>
</div>

<div class="console-main">

  <!-- ── Tab: Keys ── -->
  <div class="tab-panel active" id="tab-keys">
    <div class="cfg-section">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px">
        <h3 style="margin:0">密钥列表</h3>
        <button class="cfg-btn small" onclick="toggleKeyForm()">+ 添加密钥</button>
      </div>
      <div class="key-form" id="key-form">
        <div class="key-form-title" id="key-form-title">添加密钥</div>
        <div class="cfg-row">
          <label>名称</label>
          <input class="cfg-input" id="kf-name" placeholder="e.g. OpenAI API Key">
        </div>
        <div class="cfg-row">
          <label>分类</label>
          <select class="cfg-input" id="kf-category">
            <option value="ai">AI 模型</option>
            <option value="cloud">云服务</option>
            <option value="database">数据库</option>
            <option value="other">其他</option>
          </select>
        </div>
        <div class="cfg-row">
          <label>密钥</label>
          <input class="cfg-input" id="kf-key" placeholder="sk-...">
        </div>
        <div class="cfg-row">
          <label>备注</label>
          <input class="cfg-input" id="kf-note" placeholder="可选备注">
        </div>
        <div style="display:flex;gap:8px;margin-top:10px">
          <button class="cfg-btn primary" onclick="saveKey()">保存</button>
          <button class="cfg-btn" onclick="toggleKeyForm()">取消</button>
        </div>
      </div>
      <div id="keys-list"></div>
    </div>
  </div>

  <!-- ── Tab: Projects ── -->
  <div class="tab-panel" id="tab-projects">
    <div class="proj-layout">
      <div class="proj-list" id="proj-list"></div>
      <div class="proj-editor proj-editor-empty" id="proj-editor">
        <span>← 选择一个项目</span>
      </div>
    </div>
  </div>

  <!-- ── Tab: System ── -->
  <div class="tab-panel" id="tab-system">
    <div class="cfg-section">
      <h3>基本设置</h3>
      <div class="cfg-row">
        <label>端口</label>
        <input class="cfg-input" id="sys-port" placeholder="8000" style="max-width:120px" disabled>
      </div>
      <div class="cfg-row">
        <label>管理密码</label>
        <input class="cfg-input" id="sys-password" type="password" placeholder="设置管理员密码">
      </div>
      <div class="cfg-row">
        <label>通知音效</label>
        <select class="cfg-input" id="sys-sound" style="max-width:180px">
          <option value="Pop">Pop</option>
          <option value="Ding">Ding</option>
          <option value="None">无</option>
        </select>
      </div>
      <div style="margin-top:12px">
        <button class="cfg-btn primary" onclick="saveSystem()">保存基本设置</button>
      </div>
    </div>

    <div class="cfg-section">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px">
        <h3 style="margin:0">扫描目录</h3>
        <button class="cfg-btn small" onclick="addScanDir()">+ 添加</button>
      </div>
      <div id="scan-dirs-list"></div>
    </div>

    <div class="cfg-section">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px">
        <h3 style="margin:0">排除规则</h3>
        <button class="cfg-btn small" onclick="addExclude()">+ 添加</button>
      </div>
      <div id="excludes-list"></div>
    </div>

    <div style="margin-top:8px">
      <button class="cfg-btn primary" onclick="saveSystemLists()">保存列表设置</button>
    </div>
  </div>

</div>

<div class="toast" id="toast"></div>

{_overlays}
"""

    page_js = r"""
/* ── helpers ── */
function _esc(s) {
  var d = document.createElement('div');
  d.textContent = String(s || '');
  return d.innerHTML;
}
function _categoryLabel(cat) {
  var m = {ai:'AI 模型', cloud:'云服务', database:'数据库', other:'其他'};
  return m[cat] || m.other;
}
function showToast(msg, isError) {
  var t = document.getElementById('toast');
  t.textContent = msg;
  t.className = 'toast show ' + (isError ? 'error' : 'success');
  setTimeout(function() { t.className = 'toast'; }, 2500);
}

/* ── tab switching ── */
function switchTab(tab) {
  var btns = document.querySelectorAll('.tab-btn');
  var panels = document.querySelectorAll('.tab-panel');
  for (var i = 0; i < btns.length; i++) btns[i].classList.remove('active');
  for (var i = 0; i < panels.length; i++) panels[i].classList.remove('active');
  var idx = {keys:0, projects:1, system:2}[tab] || 0;
  btns[idx].classList.add('active');
  document.getElementById('tab-' + tab).classList.add('active');
  if (tab === 'keys') loadKeys();
  else if (tab === 'projects') loadProjects();
  else if (tab === 'system') loadSystem();
}

/* ══════════════════════════════════════════════════════════════════
   Keys
   ══════════════════════════════════════════════════════════════════ */
var _editingKeyId = null;

function loadKeys() {
  fetch('/api/settings/keys', {headers: _authHeaders()})
    .then(function(r) {
      if (r.status === 401) { openLoginModal(loadKeys); return null; }
      return r.json();
    })
    .then(function(data) {
      if (!data) return;
      var keys = data.keys || [];
      var el = document.getElementById('keys-list');
      if (!keys.length) {
        el.innerHTML = '<div style="color:var(--sub);font-size:12px;padding:16px 0;text-align:center">暂无密钥</div>';
        return;
      }
      el.innerHTML = keys.map(function(k) {
        return '<div class="key-item">' +
          '<span class="key-badge ' + _esc(k.category) + '">' + _esc(_categoryLabel(k.category)) + '</span>' +
          '<div><div class="key-name">' + _esc(k.name) + '</div>' +
          '<div class="key-val">' + _esc(k.key) + '</div>' +
          (k.note ? '<div class="key-note">' + _esc(k.note) + '</div>' : '') +
          '</div>' +
          '<div class="key-actions">' +
          '<button class="cfg-btn small" onclick="editKey(\'' + _esc(k.id) + '\')">编辑</button>' +
          '<button class="cfg-btn small danger" onclick="deleteKey(\'' + _esc(k.id) + '\',\'' + _esc(k.name) + '\')">删除</button>' +
          '</div>' +
          '<span></span>' +
          '</div>';
      }).join('');
    });
}

function toggleKeyForm() {
  var form = document.getElementById('key-form');
  if (form.classList.contains('show')) {
    form.classList.remove('show');
    _editingKeyId = null;
    document.getElementById('kf-name').value = '';
    document.getElementById('kf-category').value = 'ai';
    document.getElementById('kf-key').value = '';
    document.getElementById('kf-note').value = '';
    document.getElementById('key-form-title').textContent = '添加密钥';
  } else {
    form.classList.add('show');
  }
}

function editKey(id) {
  fetch('/api/settings/keys', {headers: _authHeaders()})
    .then(function(r) { return r.json(); })
    .then(function(data) {
      var keys = data.keys || [];
      var k = null;
      for (var i = 0; i < keys.length; i++) {
        if (keys[i].id === id) { k = keys[i]; break; }
      }
      if (!k) return;
      _editingKeyId = id;
      document.getElementById('kf-name').value = k.name || '';
      document.getElementById('kf-category').value = k.category || 'other';
      document.getElementById('kf-key').value = k.key || '';
      document.getElementById('kf-note').value = k.note || '';
      document.getElementById('key-form-title').textContent = '编辑密钥';
      var form = document.getElementById('key-form');
      if (!form.classList.contains('show')) form.classList.add('show');
    });
}

function saveKey() {
  var name = document.getElementById('kf-name').value.trim();
  var category = document.getElementById('kf-category').value;
  var key = document.getElementById('kf-key').value.trim();
  var note = document.getElementById('kf-note').value.trim();
  if (!name || !key) { showToast('名称和密钥为必填项', true); return; }
  var url = _editingKeyId ? '/api/settings/keys/' + _editingKeyId : '/api/settings/keys';
  var method = _editingKeyId ? 'PUT' : 'POST';
  fetch(url, {
    method: method, headers: Object.assign({'Content-Type':'application/json'}, _authHeaders()),
    body: JSON.stringify({name:name, category:category, key:key, note:note})
  })
    .then(function(r) {
      if (r.status === 401) { openLoginModal(function() { saveKey(); }); return null; }
      return r.json();
    })
    .then(function(data) {
      if (!data) return;
      if (data.ok) {
        showToast(_editingKeyId ? '已更新' : '已添加');
        toggleKeyForm();
        loadKeys();
      } else {
        showToast(data.detail || '保存失败', true);
      }
    })
    .catch(function() { showToast('网络错误', true); });
}

function deleteKey(id, name) {
  if (!confirm('确定删除密钥 "' + name + '"？')) return;
  fetch('/api/settings/keys/' + id, {
    method: 'DELETE', headers: _authHeaders()
  })
    .then(function(r) {
      if (r.status === 401) { openLoginModal(function() { deleteKey(id, name); }); return null; }
      return r.json();
    })
    .then(function(data) {
      if (!data) return;
      if (data.ok) { showToast('已删除'); loadKeys(); }
      else { showToast(data.detail || '删除失败', true); }
    })
    .catch(function() { showToast('网络错误', true); });
}

/* ══════════════════════════════════════════════════════════════════
   Projects
   ══════════════════════════════════════════════════════════════════ */
var _allProjects = [];
var _selectedProjectId = null;
var _projConfig = {};
var _allKeys = [];

function loadProjects() {
  fetch('/api/projects', {headers: _authHeaders()})
    .then(function(r) {
      if (r.status === 401) { openLoginModal(loadProjects); return null; }
      return r.json();
    })
    .then(function(data) {
      if (!data) return;
      _allProjects = data;
      var el = document.getElementById('proj-list');
      if (!data.length) {
        el.innerHTML = '<div style="padding:16px;color:var(--sub);font-size:12px;text-align:center">无项目</div>';
        return;
      }
      el.innerHTML = data.map(function(p) {
        var cls = (_selectedProjectId === p.id) ? 'proj-item active' : 'proj-item';
        return '<div class="' + cls + '" onclick="selectProject(\'' + _esc(p.id) + '\')">' + _esc(p.name) + '</div>';
      }).join('');
    });
  // also load keys for binding
  fetch('/api/settings/keys', {headers: _authHeaders()})
    .then(function(r) { return r.json(); })
    .then(function(data) { _allKeys = (data && data.keys) || []; })
    .catch(function() {});
}

function selectProject(id) {
  _selectedProjectId = id;
  // highlight in sidebar
  var items = document.querySelectorAll('.proj-item');
  for (var i = 0; i < items.length; i++) items[i].classList.remove('active');
  for (var i = 0; i < items.length; i++) {
    if (items[i].getAttribute('onclick').indexOf(id) !== -1) items[i].classList.add('active');
  }
  fetch('/api/settings/projects/' + id + '/config', {headers: _authHeaders()})
    .then(function(r) {
      if (r.status === 401) { openLoginModal(function() { selectProject(id); }); return null; }
      return r.json();
    })
    .then(function(data) {
      if (!data) return;
      _projConfig = data;
      renderProjectEditor();
    });
}

function renderProjectEditor() {
  var d = _projConfig;
  var el = document.getElementById('proj-editor');
  el.className = 'proj-editor';
  var boundHtml = '';
  var bk = d.bound_keys || [];
  for (var i = 0; i < bk.length; i++) {
    boundHtml += '<span class="bound-chip">' + _esc(bk[i]) +
      ' <span class="remove" onclick="unbindKey(\'' + _esc(bk[i]) + '\')">&times;</span></span>';
  }
  el.innerHTML =
    '<div class="cfg-row"><label>名称</label><input class="cfg-input" id="pe-name" value="' + _esc(d.name || '') + '"></div>' +
    '<div class="cfg-row"><label>描述</label><textarea class="cfg-input" id="pe-desc">' + _esc(d.description || '') + '</textarea></div>' +
    '<div class="cfg-row"><label>领域</label><input class="cfg-input" id="pe-domain" value="' + _esc(d.domain || '') + '"></div>' +
    '<div class="cfg-row"><label>状态</label><input class="cfg-input" id="pe-status" value="' + _esc(d.status || '') + '"></div>' +
    '<div class="cfg-row"><label>服务</label><input class="cfg-input" id="pe-service" value="' + _esc(d.service || '') + '"></div>' +
    '<div class="cfg-row"><label>部署</label><input class="cfg-input" id="pe-deploy" value="' + _esc(d.deploy || '') + '"></div>' +
    '<div class="cfg-row"><label>绑定密钥</label><div style="flex:1">' +
    '<div class="bound-keys" id="bound-keys">' + boundHtml + '</div>' +
    '<button class="cfg-btn small" style="margin-top:8px" onclick="showKeyPicker()">+ 绑定密钥</button>' +
    '</div></div>' +
    '<div id="key-picker" style="display:none;margin:8px 0 8px 90px">' +
    '<select class="cfg-input" id="pick-key" style="max-width:200px"></select> ' +
    '<button class="cfg-btn small" onclick="bindSelectedKey()">确认</button>' +
    '</div>' +
    '<div style="margin-top:14px"><button class="cfg-btn primary" onclick="saveProject()">保存项目配置</button></div>';
}

function showKeyPicker() {
  var picker = document.getElementById('key-picker');
  picker.style.display = 'block';
  var sel = document.getElementById('pick-key');
  var bound = _projConfig.bound_keys || [];
  var opts = '<option value="">-- 选择密钥 --</option>';
  for (var i = 0; i < _allKeys.length; i++) {
    var k = _allKeys[i];
    if (bound.indexOf(k.id) === -1) {
      opts += '<option value="' + _esc(k.id) + '">' + _esc(k.name) + '</option>';
    }
  }
  sel.innerHTML = opts;
}

function bindSelectedKey() {
  var sel = document.getElementById('pick-key');
  var kid = sel.value;
  if (!kid) return;
  if (!_projConfig.bound_keys) _projConfig.bound_keys = [];
  if (_projConfig.bound_keys.indexOf(kid) === -1) {
    _projConfig.bound_keys.push(kid);
  }
  renderProjectEditor();
}

function unbindKey(kid) {
  if (!_projConfig.bound_keys) return;
  _projConfig.bound_keys = _projConfig.bound_keys.filter(function(k) { return k !== kid; });
  renderProjectEditor();
}

function saveProject() {
  if (!_selectedProjectId) return;
  var body = {
    name: document.getElementById('pe-name').value.trim(),
    description: document.getElementById('pe-desc').value.trim(),
    domain: document.getElementById('pe-domain').value.trim(),
    status: document.getElementById('pe-status').value.trim(),
    service: document.getElementById('pe-service').value.trim(),
    deploy: document.getElementById('pe-deploy').value.trim(),
    bound_keys: _projConfig.bound_keys || []
  };
  fetch('/api/settings/projects/' + _selectedProjectId + '/config', {
    method: 'PUT', headers: Object.assign({'Content-Type':'application/json'}, _authHeaders()),
    body: JSON.stringify(body)
  })
    .then(function(r) {
      if (r.status === 401) { openLoginModal(saveProject); return null; }
      return r.json();
    })
    .then(function(data) {
      if (!data) return;
      if (data.ok) showToast('项目配置已保存');
      else showToast(data.detail || '保存失败', true);
    })
    .catch(function() { showToast('网络错误', true); });
}

/* ══════════════════════════════════════════════════════════════════
   System
   ══════════════════════════════════════════════════════════════════ */
function loadSystem() {
  fetch('/api/settings', {headers: _authHeaders()})
    .then(function(r) {
      if (r.status === 401) { openLoginModal(loadSystem); return null; }
      return r.json();
    })
    .then(function(data) {
      if (!data) return;
      var pw = document.getElementById('sys-password');
      if (data.admin_password) pw.value = data.admin_password;
      var snd = document.getElementById('sys-sound');
      snd.value = data.notification_sound || 'Pop';
    });

  fetch('/api/settings/system-lists', {headers: _authHeaders()})
    .then(function(r) { return r.json(); })
    .then(function(data) {
      if (!data) return;
      renderListRows('scan-dirs-list', data.scan_dirs || []);
      renderListRows('excludes-list', data.exclude || []);
    })
    .catch(function() {});
}

function renderListRows(containerId, items) {
  var el = document.getElementById(containerId);
  el.innerHTML = items.map(function(v) {
    return '<div class="list-row">' +
      '<input class="cfg-input list-val" value="' + _esc(v) + '">' +
      '<button class="remove-btn" onclick="this.parentElement.remove()">&times;</button>' +
      '</div>';
  }).join('');
}

function addScanDir() {
  var el = document.getElementById('scan-dirs-list');
  var row = document.createElement('div');
  row.className = 'list-row';
  row.innerHTML = '<input class="cfg-input list-val" placeholder="/path/to/projects">' +
    '<button class="remove-btn" onclick="this.parentElement.remove()">&times;</button>';
  el.appendChild(row);
}

function addExclude() {
  var el = document.getElementById('excludes-list');
  var row = document.createElement('div');
  row.className = 'list-row';
  row.innerHTML = '<input class="cfg-input list-val" placeholder="node_modules">' +
    '<button class="remove-btn" onclick="this.parentElement.remove()">&times;</button>';
  el.appendChild(row);
}

function saveSystem() {
  var body = {
    admin_password: document.getElementById('sys-password').value,
    notification_sound: document.getElementById('sys-sound').value
  };
  fetch('/api/settings', {
    method: 'POST', headers: Object.assign({'Content-Type':'application/json'}, _authHeaders()),
    body: JSON.stringify(body)
  })
    .then(function(r) {
      if (r.status === 401) { openLoginModal(saveSystem); return null; }
      return r.json();
    })
    .then(function(data) {
      if (!data) return;
      if (data.ok) showToast('基本设置已保存');
      else showToast(data.detail || '保存失败', true);
    })
    .catch(function() { showToast('网络错误', true); });
}

function saveSystemLists() {
  var scanInputs = document.querySelectorAll('#scan-dirs-list .list-val');
  var exclInputs = document.querySelectorAll('#excludes-list .list-val');
  var scanDirs = [];
  var excludes = [];
  for (var i = 0; i < scanInputs.length; i++) {
    var v = scanInputs[i].value.trim();
    if (v) scanDirs.push(v);
  }
  for (var i = 0; i < exclInputs.length; i++) {
    var v = exclInputs[i].value.trim();
    if (v) excludes.push(v);
  }
  fetch('/api/settings/system-lists', {
    method: 'POST', headers: Object.assign({'Content-Type':'application/json'}, _authHeaders()),
    body: JSON.stringify({scan_dirs: scanDirs, exclude: excludes})
  })
    .then(function(r) {
      if (r.status === 401) { openLoginModal(saveSystemLists); return null; }
      return r.json();
    })
    .then(function(data) {
      if (!data) return;
      if (data.ok) showToast('列表设置已保存');
      else showToast(data.detail || '保存失败', true);
    })
    .catch(function() { showToast('网络错误', true); });
}

/* ── init ── */
document.addEventListener('DOMContentLoaded', function() {
  _initAuth().then(function() { loadKeys(); });
});
"""

    return (
        "<!DOCTYPE html>\n"
        '<html lang="zh">\n'
        "<head>\n"
        '<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        "<title>设置 · Mira</title>\n"
        "<script>document.documentElement.dataset.theme = localStorage.getItem('mira-skin') || 'default';</script>\n"
        '<link rel="icon" href="/static/favicon.svg" type="image/svg+xml">\n'
        '<link rel="stylesheet" href="/static/fonts/fonts.css">\n'
        "<style>\n"
        "  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }\n"
        + _theme_css
        + "  body { background: var(--bg); color: var(--text); font-family: var(--mono); }\n"
        + _tb_css
        + page_css
        + "</style>\n</head>\n<body>\n\n"
        + page_html + "\n\n"
        + "<script>\n"
        + _tb_js + "\n"
        + page_js
        + "\n</script>\n</body>\n</html>\n"
    )
