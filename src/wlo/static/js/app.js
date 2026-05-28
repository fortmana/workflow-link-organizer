function app() {
  return {
    ...bookmarksMixin(),
    section: 'bookmarks',
    config: {},

    sectionLabel() {
      return {
        bookmarks: 'Links',
        settings: 'Settings',
      }[this.section] || '';
    },

    sectionSubtitle() {
      return {
        bookmarks: 'Profile-aware links — opens in the correct browser profile',
        settings: 'Browser profiles and configuration',
      }[this.section] || '';
    },

    async init() {
      await Promise.all([
        this.loadProjects(),
        this.loadProfiles(),
        this.loadConfig(),
      ]);
    },

    async loadConfig() {
      try {
        const r = await fetch('/api/config');
        if (r.ok) {
          this.config = await r.json();
          this._applyBookmarkColWidth();
        }
      } catch (_) {}
    },

    _applyBookmarkColWidth() {
      const w = this.config['bookmarks.column_width']?.value ?? 320;
      document.documentElement.style.setProperty('--bookmark-col-width', w + 'px');
    },

    async saveConfig(key, rawValue) {
      let value;
      if (rawValue === '' || rawValue === 'null') value = null;
      else if (!isNaN(rawValue) && rawValue !== '') value = Number(rawValue);
      else value = rawValue;

      await fetch(`/api/config/${encodeURIComponent(key)}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ value }),
      });
      await this.loadConfig();
      if (key === 'bookmarks.column_width') this._applyBookmarkColWidth();
    },
  };
}
