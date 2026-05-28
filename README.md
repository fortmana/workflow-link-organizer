# Workflow Link Organizer

A local bookmark manager that knows **which browser profile to use**. Organize
web links, local files, and folders by work context — then click once and
everything opens in the right place, already signed in.

Built for people who juggle multiple clients, projects, or accounts and are tired
of logging in and out all day.

> **New here and not technical?** Read **[GET-STARTED.md](GET-STARTED.md)** — it
> walks you through setup with Claude Code doing the work. No coding required.

---

## Why this beats browser bookmarks

### 1. It manages browser profiles for you
Browser **profiles** keep each context completely separate — different logins,
saved passwords, cookies, and history per profile. If you work across multiple
clients or accounts, profiles are the difference between "click and you're in" and
"log out, log back in, fight the password manager."

Workflow Link Organizer assigns each group of links to a profile. Click a link in
your **Client A** group and it opens in Client A's Chrome profile — already
authenticated to their SharePoint, their portal, their tools. Click something in
**Client B** and it opens in Client B's profile instead. No manual switching, no
accidental cross-posting to the wrong account.

Standard bookmarks can't do this. They all open in whatever profile happens to be
in front, so you're constantly logging in and out.

### 2. It's more than web links
A "link" here can be:
- a **website** (opens in the assigned browser profile),
- a **local file** — a spreadsheet, a PDF, a document (opens in its default app),
- a **folder** on your computer (opens in File Explorer).

Your whole working context for a project lives in one place — the client portal,
the shared drive folder, and the working spreadsheet, side by side. No more
hunting across browser bookmarks, Desktop shortcuts, and buried Explorer windows.

### 3. It's visual and built to evolve with your work
- Group links into **projects**, each with its own color.
- **Drag to reorder** links and rearrange project cards across columns.
- **Collapse** projects you're not using right now.
- Add links instantly with the **quick-add bar**.

It lives in a browser tab you keep open — always visible, always one click away.
Not a hidden, ever-growing stack of bookmarks you can never find anything in.

---

## A real example

You're a consultant with three active clients. Each has a SharePoint site, a
project-management tool, and a billing portal — nine logins across three identities.

**With browser bookmarks:** one flat list, one profile. Opening Client B's
SharePoint means logging out of Client A first. Half your clicks lead to "wrong
account" screens.

**With Workflow Link Organizer:** three project cards — Client A, B, C — each tied
to its own browser profile. Client A's card holds their SharePoint, their PM tool,
their billing portal, *and* a shortcut to the working folder on your drive and the
current status spreadsheet. One click on any of them opens in Client A's identity,
already signed in. Switching clients is switching cards.

---

## Setting up browser profiles

This is what makes the app powerful, so it's worth doing first.

### Google Chrome
1. Click your **profile avatar** in the top-right corner of Chrome.
2. Click **Add** at the bottom of the menu.
3. Choose **Sign in** (to sync with a Google account) or **Continue without an account**.
4. Give the profile a clear name — e.g. `Client A`, `Internal`, `Personal`.
5. The new profile opens in its own window with its own cookies and saved passwords.

### Microsoft Edge
1. Click your **profile avatar** in the top-right corner of Edge.
2. Click **Add profile**, then **Add**.
3. Sign in with a Microsoft account or continue without one.
4. Name it to match the work context.
5. Done — Edge profiles are fully isolated, just like Chrome's.

### Naming convention
Pick names you'll recognize in the app's profile picker. Common approaches:
- **By client:** `Acme Health`, `Globex`, `Initech`
- **By account:** `Work Google`, `Personal Google`
- **By role:** `Consulting`, `Internal`, `Personal`

Once your profiles exist, the app detects them automatically under
**Settings → Browser Profiles**, where you can give each a friendly label.

---

## Quick start (if you're comfortable with the basics)

```powershell
git clone https://github.com/fortmana/workflow-link-organizer.git
cd workflow-link-organizer
powershell -ExecutionPolicy Bypass -File setup.ps1
.\Start.bat
```

Opens at **http://127.0.0.1:5757**. Full setup details and configuration options
are in **[CLAUDE.md](CLAUDE.md)**.

---

## Requirements

- Windows 10 or 11
- Python 3.10 or newer
- Google Chrome and/or Microsoft Edge (for multi-profile support)

## How it works

A small local web server (Flask + Waitress) serves a single-page interface
(Alpine.js, no build step) and stores everything in a local SQLite database at
`%LOCALAPPDATA%\WorkflowLinkOrganizer\wlo.db`. It runs from a system-tray icon and
listens only on your own machine (`127.0.0.1`). Nothing leaves your computer.

## License

MIT
