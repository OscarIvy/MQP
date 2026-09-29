# How We Use GitHub on This Project
 
This guide is for the whole team, including anyone new to GitHub. **You don't need the terminal to upload CAD files, spreadsheets, or documents.** Uploads happen in your web browser, and a bot handles the rest. Basic Git commands are near the bottom for the people working on code.
 
## Quick summary
 
- **Uploading CAD, Excel, or documents?** Open a new Issue using the **File Upload / Resource Submission** form and attach your files. A bot commits them to the repo for you.
- **Zip your CAD files first.** GitHub won't accept `.step`, `.stl`, `.f3d`, or `.sldprt` files directly, but it accepts a `.zip` containing them.
- **Working on code?** Use a branch and a pull request. Never force-push. See [Working on code](#working-on-code).
- **Stuck or something looks wrong?** Don't try random Git commands. Ask [OscarIvy].
## Where things live
 
| Folder | What's in it |
|---|---|
| `CAD/` | `.step`, `.stp`, `.stl`, `.f3d`, `.sldprt` |
| `Excel/` | `.xlsx`, `.xls`, `.csv` |
| `Documents/` | Everything else: PDFs, Word, PowerPoint, text files |
| `.github/` | The upload form and the bots. **Please don't edit these.** |
| [FILL IN, e.g. `src/`] | Software source code |
 
The bot sorts uploads into `CAD/`, `Excel/`, and `Documents/` by file type. You don't pick the folder.
 
## Uploading files (CAD, Excel, documents)
 
1. Go to the **Issues** tab, click **New issue**, then **Get started** next to **File Upload / Resource Submission**.
2. Keep `[UPLOAD]:` at the start of the title and add a short description after it, for example `[UPLOAD]: Frame CAD rev B`.
3. Fill in the form:
   | Field | What to enter |
   |---|---|
   | **Your Name / System Component** | Required. Who you are and what the file is for, e.g. "Frame CAD" or "Battery Budget Sheet". |
   | **Summary / Commit Note** | One clear line about what changed. **Only the first line is used** as the commit message. |
   | **Addresses / Closes Issues** | Issue numbers this upload completes, like `#12, #15`. Those issues close automatically. Leave blank if none. |
   | **Category Label** | Optional. Adds a subsystem tag to the issue. |
   | **Attach Files** | Required. Drag and drop your files into this box (see the file rules below). |
4. **Wait for each file's link to appear in the box** before you submit. If you submit while a file is still uploading, it won't be included.
5. Click **Submit new issue**. Give it a minute or two. The bot will commit your files, comment on the issue, and close it.
6. Check that your file shows up in the right folder.
### File rules
 
- **Accepted directly:** `.xlsx`, `.xls`, `.csv`, `.pdf`, `.docx`, `.pptx`, `.txt`, `.md`, `.zip`, and a few others.
- **Not accepted directly (zip them first):** CAD files such as `.step`, `.stp`, `.stl`, `.f3d`, `.sldprt`.
  - Windows: select the file(s), right-click, **Send to**, **Compressed (zipped) folder**.
  - Mac: select the file(s), right-click, **Compress**.
  - You can put several files in one zip. The bot unpacks it and sorts the contents.
- **Size limit:** 25 MB per file. For anything bigger, ask [OWNER NAME].
### Good to know
 
- **Same filename = replaces the old version.** The old version is still saved in the history. Keep the filename the same to update a file. Change the name only if you want both versions side by side.
- **Inside a zip, folders are flattened.** Every file lands directly in `CAD/`, `Excel/`, or `Documents/`, so two files with the same name in one zip will overwrite each other.
- **If the bot says "No new attachments found":** the file either didn't attach, or it's identical to what's already in the repo. Click the `...` menu on the issue, choose **Edit**, and add the file. The bot runs again as long as the issue is open.
- **Once the issue is closed, editing it does nothing.** Open a new upload issue instead.
- **Every new issue also gets an AI-written summary comment.** It's a convenience and can be wrong, so go by the actual issue text.
- **Nothing happened?** Check that you've been added to the repo, that the title still starts with `[UPLOAD]:`, and open the **Actions** tab to see if the latest run failed (red X). If it did, tell [OWNER NAME].
## Getting the latest files
 
- **In the browser:** open the folder, click the file, and use the download button. **Code**, then **Download ZIP** on the main page gets everything.
- **Older versions:** open the file on GitHub and click **History**.
- **With Git:** run `git pull` (see below).
## Working on code
 
If you're only uploading files, you can skip this section.
 
**Easiest option: skip the terminal.** [GitHub Desktop](https://desktop.github.com/) or the Source Control panel in VS Code do everything below with buttons.
 
**If you want the terminal,** these are the only commands you need:
 
```bash
git clone <REPO-URL>              # once: copy the repo to your computer
cd <repo-folder>
 
git pull                          # start of every work session: get the latest changes
git switch -c my-feature          # start a new branch for your work (pick a descriptive name)
 
git status                        # see what you've changed
git add path/to/file              # stage a file ("git add ." stages everything)
git commit -m "Describe what you changed"
git push -u origin my-feature     # first push of a new branch (later pushes: just "git push")
```
 
Then:
 
1. On GitHub, click **Compare & pull request** and describe your change.
2. Have a teammate review it, then merge.
3. Update your copy: `git switch main`, then `git pull`.
**Pull at the start of every session.** The upload bot adds files directly to `main`, so your copy can fall behind without you doing anything.
 
**If `git push` says "rejected" or "fetch first":** run `git pull`, then `git push` again.
 
### Please don't
 
- **Don't run** `git push --force` (or `-f`), `git reset --hard`, or `git clean -fd`. They can permanently delete your work or your teammates' work.
- **Don't edit** anything in `.github/`. That's the upload form and the bots.
- **Don't commit code straight to `main`.** Use a branch and a pull request. (The upload bot is the only exception.)
- **Don't commit passwords, keys, or tokens.**
- **If you hit a merge conflict, stop and ask** [OWNER NAME] instead of guessing.
<details>
<summary><strong>Repo setup checklist (owner only)</strong></summary>
**Files and where they go**
 
- `.github/ISSUE_TEMPLATE/file-upload.yml` is the upload form.
- `.github/workflows/process-uploads.yml` is the bot that commits uploads.
- `.github/workflows/summarize-issues.yml` is the AI summary bot.
- All three must be on the **default branch** (`main`). Issue forms and issue-triggered workflows only work from there.
**Settings**
 
- **Add every teammate as a collaborator** (Settings, then Collaborators). The upload bot ignores issues from anyone without write access, so it silently does nothing for them.
- **Create these labels:** `file-submission`, `cad`, `excel`, `documentation`, `hardware`. Labels that don't exist can't be applied.
- **Branch protection on `main`:** the bot pushes directly to `main`. If you require pull requests there, the bot's push will fail unless it's allowed to bypass.
- **Summary bot secret:** add a repo secret named `COPILOT_PAT` (Settings, Secrets and variables, Actions) containing a personal access token from an account with Copilot access. Without it, only the summary bot fails. Uploads still work.
**Good to know**
 
- The parsing depends on the form's field labels: `Summary / Commit Note`, `Addresses / Closes Issues`, and `Category Label`. If you rename them in the form, update `process-uploads.yml` to match.
- If the repo is private, downloading attachments inside Actions can fail. After setup, test with a small file before telling the team to use it.
- If you keep a `dev` branch, merge `main` into it now and then, since the bot's commits land on `main`: `git checkout dev && git fetch && git merge origin/main`.
</details>
