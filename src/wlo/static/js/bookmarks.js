function bookmarksMixin() {
  return {
    projects: [],
    profiles: [],
    profileLabels: {},      // { "chrome|Default": "My Label" } — bound to Settings inputs
    collapsedProjects: {},  // { projectId: true } — persisted to localStorage
    editingLink: {},        // { linkId: { name, path, notes, browser, profile_dir } }
    editingProject: {},     // { projectId: { name, color, default_browser, default_profile_dir, default_profile_name } }
    showAddProject: false,
    newProject: { name: '', color: '#4A90D9', default_browser: '', default_profile_dir: '', default_profile_name: '' },
    projectAddingLink: {},  // keyed by project id — per-card add-link state
    newLink: {},            // keyed by project id — add-link form state
    quickAdd: { url: '', name: '', project_id: localStorage.getItem('wlo-quick-add-project') || '' },
    quickAddStatus: null,   // null | 'ok' | 'error'
    quickAddMessage: '',

    // ── Color picker ──────────────────────────────────────────────────────
    colorPickerOpen: false,
    editProjectColorPickerOpen: false,
    recentColors: JSON.parse(localStorage.getItem('wlo-recent-colors') || '[]'),

    _swatchPalette: (() => {
      const cols = [
        ['#ffffff','#f5f5f5','#e0e0e0','#9e9e9e','#616161','#424242','#000000'], // neutral
        ['#ffcdd2','#ef9a9a','#e57373','#f44336','#e53935','#c62828','#b71c1c'], // red
        ['#fce4ec','#f48fb1','#ec407a','#e91e63','#c2185b','#ad1457','#880e4f'], // pink
        ['#f3e5f5','#ce93d8','#ab47bc','#9c27b0','#7b1fa2','#6a1b9a','#4a148c'], // purple
        ['#e3f2fd','#90caf9','#42a5f5','#2196f3','#1976d2','#1565c0','#0d47a1'], // blue
        ['#e0f2f1','#80cbc4','#26a69a','#009688','#00897b','#00796b','#004d40'], // teal
        ['#e8f5e9','#a5d6a7','#66bb6a','#4caf50','#388e3c','#2e7d32','#1b5e20'], // green
        ['#fffde7','#fff176','#ffee58','#fdd835','#f9a825','#f57f17','#ff6f00'], // yellow
        ['#fff3e0','#ffcc80','#ffa726','#ff9800','#f57c00','#e65100','#bf360c'], // orange
        ['#efebe9','#d7ccc8','#bcaaa4','#795548','#6d4c41','#5d4037','#3e2723'], // brown
      ];
      const flat = [];
      for (let r = 0; r < 7; r++)
        for (let c = 0; c < cols.length; c++)
          flat.push(cols[c][r]);
      return flat;
    })(),

    pickColor(hex) {
      this.newProject.color = hex;
      this.recentColors = [hex, ...this.recentColors.filter(c => c !== hex)].slice(0, 10);
      localStorage.setItem('wlo-recent-colors', JSON.stringify(this.recentColors));
      this.colorPickerOpen = false;
    },

    pickProjectEditColor(projId, hex) {
      if (this.editingProject[projId]) this.editingProject[projId].color = hex;
      this.recentColors = [hex, ...this.recentColors.filter(c => c !== hex)].slice(0, 10);
      localStorage.setItem('wlo-recent-colors', JSON.stringify(this.recentColors));
      this.editProjectColorPickerOpen = false;
    },

    onColorHexInput(val) {
      if (/^#[0-9a-f]{6}$/i.test(val)) this.newProject.color = val;
    },

    _fileExt(path) {
      if (!path) return '';
      const seg = path.replace(/[/\\]+$/, '').split(/[/\\]/).pop() || '';
      const dot = seg.lastIndexOf('.');
      return dot > 0 ? seg.slice(dot + 1).toUpperCase() : '';
    },

    async submitQuickAdd() {
      if (!this.quickAdd.url.trim()) return;
      const payload = { url: this.quickAdd.url.trim() };
      if (this.quickAdd.name.trim()) payload.name = this.quickAdd.name.trim();
      if (this.quickAdd.project_id) payload.project = this.quickAdd.project_id;
      const r = await fetch('/api/bookmarks/links/quick', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      if (r.ok) {
        const link = await r.json();
        const proj = this.projects.find(p => p.id === link.project_id);
        if (proj) proj.links.push(link);
        localStorage.setItem('wlo-quick-add-project', this.quickAdd.project_id);
        this.quickAdd = { url: '', name: '', project_id: this.quickAdd.project_id };
        this.quickAddStatus = 'ok';
        this.quickAddMessage = `Added "${link.name}"`;
      } else {
        const body = await r.json().catch(() => ({}));
        this.quickAddStatus = 'error';
        this.quickAddMessage = body.error || 'Failed to add link';
      }
      setTimeout(() => { this.quickAddStatus = null; }, 3000);
    },

    projectColumns: [],
    _draggingProject: false,

    _rebuildCols() {
      const cols = {};
      for (const proj of this.projects) {
        const c = proj.column_index ?? 0;
        if (!cols[c]) cols[c] = [];
        cols[c].push(proj);
      }
      const maxCol = Object.keys(cols).length > 0
        ? Math.max(...Object.keys(cols).map(Number))
        : 0;
      // Fill any gaps and append one trailing empty column as a permanent drop target
      for (let i = 0; i <= maxCol + 1; i++) {
        if (!cols[i]) cols[i] = [];
      }
      this.projectColumns = Object.keys(cols).map(k => parseInt(k)).sort((a, b) => a - b)
        .map(idx => ({ index: idx, projects: cols[idx].slice().sort((a, b) => a.sort_order - b.sort_order || a.id - b.id) }));
    },

    async loadProjects() {
      try {
        const r = await fetch('/api/bookmarks/projects');
        if (r.ok) {
          this.projects = await r.json();
          this._rebuildCols();
          const saved = localStorage.getItem('wlo_collapsed_projects');
          if (saved) this.collapsedProjects = JSON.parse(saved);
        }
      } catch (_) {}
    },

    async loadProfiles() {
      try {
        const r = await fetch('/api/bookmarks/profiles');
        if (r.ok) {
          this.profiles = await r.json();
          const labels = {};
          this.profiles.forEach(p => { labels[`${p.browser}|${p.profile_dir}`] = p.display_name; });
          this.profileLabels = labels;
        }
      } catch (_) {}
    },

    // ── Profile label / active ────────────────────────────────────────────

    async saveAllProfileLabels() {
      await Promise.all(
        this.profiles.map(p => {
          const key = `${p.browser}|${p.profile_dir}`;
          const label = (this.profileLabels[key] || '').trim();
          return fetch(`/api/bookmarks/profiles/${p.browser}/${encodeURIComponent(p.profile_dir)}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ label }),
          });
        })
      );
      await this.loadProfiles();
    },

    async toggleProfileActive(browser, profileDir) {
      const p = this.profiles.find(p => p.browser === browser && p.profile_dir === profileDir);
      const newActive = p ? !p.active : false;
      await fetch(`/api/bookmarks/profiles/${browser}/${encodeURIComponent(profileDir)}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ active: newActive }),
      });
      await this.loadProfiles();
    },

    profileLabel(browser, profileDir) {
      const match = this.profiles.find(p => p.browser === browser && p.profile_dir === profileDir);
      return match ? `${this._browserLabel(match.browser)} / ${match.display_name}` : profileDir || 'Default browser';
    },

    _browserLabel(b) { return b === 'chrome' ? 'Chrome' : 'Edge'; },

    // ── Collapsible cards ─────────────────────────────────────────────────

    toggleCollapse(projectId) {
      this.collapsedProjects = { ...this.collapsedProjects, [projectId]: !this.collapsedProjects[projectId] };
      localStorage.setItem('wlo_collapsed_projects', JSON.stringify(this.collapsedProjects));
    },

    collapseAll() {
      const collapsed = {};
      this.projects.forEach(p => { collapsed[p.id] = true; });
      this.collapsedProjects = collapsed;
      localStorage.setItem('wlo_collapsed_projects', JSON.stringify(this.collapsedProjects));
    },

    expandAll() {
      this.collapsedProjects = {};
      localStorage.setItem('wlo_collapsed_projects', JSON.stringify(this.collapsedProjects));
    },

    // ── Projects CRUD ─────────────────────────────────────────────────────

    startEditProject(proj) {
      this.editingProject = {
        ...this.editingProject,
        [proj.id]: {
          name: proj.name,
          color: proj.color,
          column_index: proj.column_index ?? 0,
          default_browser: proj.default_browser || '',
          default_profile_dir: proj.default_profile_dir || '',
          default_profile_name: proj.default_profile_name || '',
        },
      };
    },

    cancelEditProject(projId) {
      const updated = { ...this.editingProject };
      delete updated[projId];
      this.editingProject = updated;
    },

    async saveEditProject(projId) {
      const form = this.editingProject[projId];
      if (!form || !form.name.trim()) return;
      const body = { name: form.name.trim(), color: form.color, column_index: form.column_index ?? 0 };
      if (form.default_browser) {
        body.default_browser = form.default_browser;
        body.default_profile_dir = form.default_profile_dir;
        body.default_profile_name = form.default_profile_name;
      }
      const r = await fetch(`/api/bookmarks/projects/${projId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });
      if (r.ok) {
        const updated = await r.json();
        const idx = this.projects.findIndex(p => p.id === projId);
        if (idx >= 0) this.projects[idx] = updated;
        this._rebuildCols();
        this.cancelEditProject(projId);
      }
    },

    async createProject() {
      if (!this.newProject.name.trim()) return;
      const body = { ...this.newProject };
      if (!body.default_browser) { delete body.default_browser; delete body.default_profile_dir; delete body.default_profile_name; }
      const r = await fetch('/api/bookmarks/projects', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });
      if (r.ok) {
        const proj = await r.json();
        this.projects.push(proj);
        this._rebuildCols();
        this.showAddProject = false;
        this.newProject = { name: '', color: '#4A90D9', default_browser: '', default_profile_dir: '', default_profile_name: '' };
      }
    },

    async deleteProject(id) {
      await fetch(`/api/bookmarks/projects/${id}`, { method: 'DELETE' });
      this.projects = this.projects.filter(p => p.id !== id);
      this._rebuildCols();
    },

    // ── Links CRUD ────────────────────────────────────────────────────────

    startAddLink(projectId) {
      this.projectAddingLink = { ...this.projectAddingLink, [projectId]: true };
      this.newLink = { ...this.newLink, [projectId]: { name: '', path: '', notes: '', browser: '', profile_dir: '' } };
    },

    cancelAddLink(projectId) {
      this.projectAddingLink = { ...this.projectAddingLink, [projectId]: false };
    },

    async submitLink(projectId) {
      const form = this.newLink[projectId];
      if (!form.name.trim() || !form.path.trim()) return;
      const body = { name: form.name, path: form.path, notes: form.notes || null };
      if (form.browser) { body.browser = form.browser; body.profile_dir = form.profile_dir; }
      const r = await fetch(`/api/bookmarks/projects/${projectId}/links`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });
      if (r.ok) {
        const link = await r.json();
        const proj = this.projects.find(p => p.id === projectId);
        if (proj) proj.links.push(link);
        this.projectAddingLink = { ...this.projectAddingLink, [projectId]: false };
      }
    },

    startEditLink(link) {
      this.editingLink = {
        ...this.editingLink,
        [link.id]: {
          name: link.name,
          path: link.path,
          notes: link.notes || '',
          browser: link.browser || '',
          profile_dir: link.profile_dir || '',
          project_id: link.project_id,
        },
      };
    },

    cancelEditLink(linkId) {
      const updated = { ...this.editingLink };
      delete updated[linkId];
      this.editingLink = updated;
    },

    async saveEditLink(projectId, linkId) {
      const form = this.editingLink[linkId];
      if (!form || !form.name.trim() || !form.path.trim()) return;
      const body = { name: form.name, path: form.path, notes: form.notes || null };
      if (form.browser) { body.browser = form.browser; body.profile_dir = form.profile_dir; }
      const moving = form.project_id && form.project_id !== projectId;
      if (moving) body.project_id = form.project_id;
      const r = await fetch(`/api/bookmarks/links/${linkId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });
      if (r.ok) {
        const updated = await r.json();
        const srcProj = this.projects.find(p => p.id === projectId);
        if (moving) {
          if (srcProj) srcProj.links = srcProj.links.filter(l => l.id !== linkId);
          const destProj = this.projects.find(p => p.id === form.project_id);
          if (destProj) destProj.links.push(updated);
        } else if (srcProj) {
          const idx = srcProj.links.findIndex(l => l.id === linkId);
          if (idx >= 0) srcProj.links[idx] = updated;
        }
        this.cancelEditLink(linkId);
      }
    },

    async openLink(linkId) {
      await fetch(`/api/bookmarks/links/${linkId}/open`, { method: 'POST' });
    },

    async deleteLink(projectId, linkId) {
      await fetch(`/api/bookmarks/links/${linkId}`, { method: 'DELETE' });
      const proj = this.projects.find(p => p.id === projectId);
      if (proj) proj.links = proj.links.filter(l => l.id !== linkId);
    },

    initLinkSort(el, projectId) {
      if (!window.Sortable) return;
      const existing = Sortable.get(el);
      if (existing) existing.destroy();
      Sortable.create(el, {
        animation: 150,
        draggable: '.link-item',
        cancel: 'input, select, button, textarea, a',
        ghostClass: 'sortable-ghost',
        onEnd: (evt) => {
          if (evt.oldIndex === evt.newIndex && evt.from === evt.to) return;
          const proj = this.projects.find(p => p.id === projectId);
          if (!proj) return;
          const ids = [...el.querySelectorAll('.link-item')].map(n => parseInt(n.dataset.linkId));
          ids.forEach((id, idx) => fetch(`/api/bookmarks/links/${id}`, {
            method: 'PUT', headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ sort_order: idx }),
          }));
          // Reorder raw (non-proxied) links array in-place — no Alpine reactive trigger,
          // no re-render, no conflict with SortableJS. proj itself must be raw-unwrapped
          // so that accessing .links gives the actual array rather than another proxy.
          const rawProj = window.Alpine ? Alpine.raw(proj) : null;
          if (rawProj) {
            const byId = Object.fromEntries(rawProj.links.map(l => [l.id, l]));
            ids.forEach((id, idx) => { if (byId[id]) byId[id].sort_order = idx; });
            rawProj.links.splice(0, rawProj.links.length, ...ids.map(id => byId[id]).filter(Boolean));
          }
        },
      });
    },

    initProjectSort(el, colIndex) {
      if (!window.Sortable) return;
      const existing = Sortable.get(el);
      if (existing) existing.destroy();
      Sortable.create(el, {
        group: 'project-cols',
        animation: 150,
        draggable: '.project-card',
        cancel: 'input, select, button, textarea, a',
        ghostClass: 'sortable-ghost',
        emptyInsertThreshold: 40,
        onStart: () => { this._draggingProject = true; },
        onEnd: (evt) => {
          if (evt.oldIndex === evt.newIndex && evt.from === evt.to) return;
          const fromColIndex = parseInt(evt.from.dataset.colIndex);
          const toColIndex = parseInt(evt.to.dataset.colIndex);
          const crossCol = evt.from !== evt.to;
          const byId = Object.fromEntries(this.projects.map(p => [p.id, p]));

          if (crossCol) {
            // Remove SortableJS-moved node before Alpine re-renders to prevent duplicate
            const movedId = parseInt(evt.item.dataset.projectId);
            evt.item.remove();
            if (byId[movedId]) {
              byId[movedId].column_index = toColIndex;
              byId[movedId].sort_order = [...evt.to.querySelectorAll(':scope > .project-card')].length;
            }
            fetch(`/api/bookmarks/projects/${movedId}`, {
              method: 'PUT', headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ sort_order: byId[movedId]?.sort_order ?? 99, column_index: toColIndex }),
            });
          }

          // Persist + sync sort_orders for source (and dest for within-col)
          const syncCol = (containerEl, colIdx) => {
            const ids = [...containerEl.querySelectorAll(':scope > .project-card')].map(n => parseInt(n.dataset.projectId));
            ids.forEach((id, idx) => {
              if (byId[id]) { byId[id].sort_order = idx; byId[id].column_index = colIdx; }
              fetch(`/api/bookmarks/projects/${id}`, {
                method: 'PUT', headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ sort_order: idx, column_index: colIdx }),
              });
            });
          };
          syncCol(evt.from, fromColIndex);
          if (crossCol) syncCol(evt.to, toColIndex);
          this._rebuildCols();
          this._draggingProject = false;
        },
      });
    },

    onProfileSelect(projectId, e) {
      const val = e.target.value;
      const form = this.newLink[projectId];
      if (!val) { form.browser = ''; form.profile_dir = ''; return; }
      const [browser, profileDir] = val.split('|');
      form.browser = browser;
      form.profile_dir = profileDir;
    },

    onEditProfileSelect(linkId, e) {
      const val = e.target.value;
      const form = this.editingLink[linkId];
      if (!val) { form.browser = ''; form.profile_dir = ''; return; }
      const [browser, profileDir] = val.split('|');
      form.browser = browser;
      form.profile_dir = profileDir;
    },
  };
}
