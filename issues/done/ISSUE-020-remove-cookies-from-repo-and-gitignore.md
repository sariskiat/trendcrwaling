# [ISSUE-020] Remove fb_cookies.txt from repo and ensure all cookie files are gitignored

**Type:** AFK
**Priority:** bug
**Blocked by:** nothing

---

## Summary

`fb_cookies.txt` contains live Facebook session cookies and is tracked in the repo. Even if `.gitignore` lists it, the file was committed. All cookie files (`fb_cookies.txt`, `tt_cookies.txt`, `ig_cookies.txt`, `*_cookies.txt`) must be gitignored and removed from tracking.

---

## Acceptance Criteria

- [ ] `fb_cookies.txt` removed from git tracking via `git rm --cached`
- [ ] `.gitignore` includes `*_cookies.txt` pattern
- [ ] No cookie files are tracked by git
- [ ] Existing tests still pass

---

## Files to Create / Modify

| File | Action |
|---|---|
| `.gitignore` | Add `*_cookies.txt` pattern |
| `fb_cookies.txt` | Remove from git tracking (keep on disk) |
