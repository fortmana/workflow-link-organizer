-- Remove browser path config keys added in 001/002 — feature reverted;
-- auto-detection from standard paths handles all common cases.
DELETE FROM config
 WHERE key IN (
   'bookmarks.chrome_exe',
   'bookmarks.chrome_user_data',
   'bookmarks.edge_exe',
   'bookmarks.edge_user_data'
 );
