-- Update browser path config key descriptions with helpful guidance for locating paths.
UPDATE config
   SET description = 'Path to Chrome User Data directory (parent of Default, Profile 1, etc.). To find it: open chrome://version in Chrome and look at Profile Path — copy everything above the last folder name.'
 WHERE key = 'bookmarks.chrome_user_data';

UPDATE config
   SET description = 'Path to Edge User Data directory. To find it: open edge://version in Edge and look at Profile Path — copy everything above the last folder name.'
 WHERE key = 'bookmarks.edge_user_data';

UPDATE config
   SET description = 'Path to chrome.exe. Default: C:\Program Files\Google\Chrome\Application\chrome.exe'
 WHERE key = 'bookmarks.chrome_exe';

UPDATE config
   SET description = 'Path to msedge.exe. Default: C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
 WHERE key = 'bookmarks.edge_exe';
