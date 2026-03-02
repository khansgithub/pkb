Sure. Let's trace through this tiny markdown document:

````markdown
# git
## credential cache helper
```bash
git config --global credential.helper cache
```
## global user.email
```bash
git config --global user.email "you@example.com"
```
````

Here's what happens line-by-line, showing the stack at each step:

---

**Line: `# git`** — It's a heading, level 1. Stack is empty, so pop nothing. No parent in stack, so append to `doc.sections`. Push onto stack.

```
stack: [ Section("git", level=1) ]
```

**Line: `## credential cache helper`** — Heading, level 2. Stack top is `git` (level 1). 1 < 2, so don't pop. `git` is the parent — append to `git.children`. Push onto stack.

```
stack: [ Section("git", level=1),  Section("credential cache helper", level=2) ]
```

**Line: `` ```bash ``** — Code fence opens. Create `CodeBlock(language="bash")`.

**Line: `git config --global credential.helper cache`** — Inside code block, append to `code_block.lines`.

**Line: `` ``` ``** — Code fence closes. `stack[-1]` is `credential cache helper` — append the code block to its children.

```
tree so far:
  git
    credential cache helper
      CodeBlock("bash", ["git config --global credential.helper cache"])
```

**Line: `## global user.email`** — Heading, level 2. Stack top is `credential cache helper` (level 2). 2 >= 2, so **pop it**. Now stack top is `git` (level 1). 1 < 2, stop popping. `git` is the parent — append. Push onto stack.

```
stack: [ Section("git", level=1),  Section("global user.email", level=2) ]
```

The remaining code block attaches to `global user.email` the same way.

---

**Final tree:**

```
Document
  └── Section("git", level=1)
        ├── Section("credential cache helper", level=2)
        │     └── CodeBlock("bash", ["git config --global credential.helper cache"])
        └── Section("global user.email", level=2)
              └── CodeBlock("bash", ["git config --global user.email ..."])
```

---

The key insight is that the stack always represents your current **ancestry path** — like a breadcrumb trail. When you hit a new heading, you just pop until the top of the stack is shallower than you, and that's your parent. That single `while` loop replaces all four heading-level branches in the current code.
