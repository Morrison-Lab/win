# GitHub Copilot Instructions for win Repository

> [!IMPORTANT]
> **MANDATORY ENVIRONMENT SETUP - DO THIS FIRST, ALWAYS:**
> 
> At the START of EVERY work session on this repository:
> 1. **IMMEDIATELY install R 4.5.2+, Quarto, TinyTeX** (see Installation section below)
> 2. **Run `renv::restore()`** to install all R packages
> 3. **Verify tools are working** with `quarto --version` and `R --version`
>
> **MANDATORY TESTING BEFORE EVERY COMMIT:**
> 
> Before committing ANY changes to `.qmd` or config files:
> 1. **Run `quarto render` on the FULL repository** (not individual files)
> 2. **Verify it completes successfully** (exit code 0, no errors)
> 3. **Check all 3 output formats exist** in `_site/`: HTML, RevealJS slides, PDF handouts
> 4. Only then commit your changes
>
> **CRITICAL RULES:**
> - **CI is NOT the test** - you must test locally BEFORE pushing
> - **NEVER rely on CI to discover rendering errors** - that's your job
> - **ALWAYS run full `quarto render`** - testing individual files is insufficient
> - **This is a hard requirement - no exceptions, no excuses**

## Project Overview

`win` is both an R package and a Quarto website containing lecture notes based on Hernán MA and Robins JM's "Causal Inference: What If?" textbook. 

**Dual Nature:**
- **R Package**: Installable via `devtools::install_github("ucdavis/win")` with proper DESCRIPTION, NAMESPACE, and R package structure
- **Quarto Website**: Demonstrates Quarto's multi-format capabilities, rendering each chapter as HTML pages, RevealJS slides, and PDF handouts from the same source files

The R package structure coexists with the Quarto website through careful use of `.Rbuildignore` to exclude website-specific files from package builds.

## Technology Stack

- **Language**: R (version 4.0+, **always use the latest R release** in development and CI/CD)
- **Documentation Format**: Quarto (.qmd files)
- **Dependency Management**: renv for R package management
- **Visualization**: ggplot2, tidyverse
- **Code Style**: tidyverse style guide
- **CI/CD**: GitHub Actions workflows
- **Version Control**: Git/GitHub
- **Website Generation**: Quarto with multi-format rendering (HTML, RevealJS, PDF)

## Development Setup

### General Principles

**CRITICAL**: Do not make assumptions about what code will do - always test it yourself.

**ENVIRONMENT SETUP IS MANDATORY:**
- At the START of EVERY work session, install R, Quarto, and TinyTeX IMMEDIATELY
- Never start making changes without having the full development environment ready
- CI is for final verification ONLY - you must test locally FIRST
- Your working environment should mirror the CI environment

**MANDATORY WORKFLOW FOR ANY `.qmd` OR CONFIG CHANGES:**
1. **FIRST: Install required tools** (R 4.5.2+, Quarto, TinyTeX) if not already installed
2. **ALWAYS run FULL `quarto render`** on the entire repository before committing
3. **Test individual files only for rapid iteration** - final verification MUST be full render
4. **NEVER commit changes without successful full `quarto render`**
5. **CI is NOT a substitute for local testing** - CI failures mean you failed to test properly

- **Install required software first**: Ensure all necessary tools (R, Quarto, TinyTeX) are installed before starting work
- **Test your changes**: Run the actual commands to verify functionality
- **Run `quarto render` on FULL repository**: Testing individual files misses cross-file issues
- **Verify output**: Check that expected files are created with correct content
- **Never claim success without evidence**: Only report that something works after you've confirmed it yourself

### Prerequisites

1. R (**always use the latest R release**, currently R 4.5.2 or later)
2. RStudio (optional but recommended)
3. Quarto CLI (https://quarto.org/docs/get-started/)
4. pandoc (usually bundled with RStudio or Quarto)
5. **TinyTeX** (required for PDF rendering - see installation below)

### Installation

**CRITICAL**: Always install the latest R release AND all required tools before starting development or testing.

**On Ubuntu/Debian systems**:
```bash
# Add CRAN GPG key
wget -qO- https://cloud.r-project.org/bin/linux/ubuntu/marutter_pubkey.asc | sudo tee -a /etc/apt/trusted.gpg.d/cran_ubuntu_key.asc

# Add CRAN repository (replace $(lsb_release -cs) with your Ubuntu codename if needed)
sudo add-apt-repository "deb https://cloud.r-project.org/bin/linux/ubuntu $(lsb_release -cs)-cran40/"

# Update and install latest R
sudo apt-get update
sudo apt-get install -y r-base r-base-dev

# Verify you have the latest version (should be 4.5.2 or later)
R --version
```

**NEVER** use the R version from standard Ubuntu repositories (apt-get install r-base without adding CRAN repo) as it will be outdated (e.g., R 4.3.3 instead of R 4.5.2).

**On other systems**: Download the latest R release from https://cloud.r-project.org/

**Install Quarto** (required for rendering):

On Ubuntu/Linux:
```bash
# Download and install Quarto (check https://quarto.org/docs/get-started/ for latest version)
wget https://github.com/quarto-dev/quarto-cli/releases/download/v1.4.550/quarto-1.4.550-linux-amd64.deb
sudo dpkg -i quarto-1.4.550-linux-amd64.deb

# Verify installation
quarto --version
```

On macOS/Windows: Download installer from https://quarto.org/docs/get-started/

**Install TinyTeX** (required for PDF rendering):

```bash
# Via Quarto (preferred method)
quarto install tinytex --no-prompt

# Verify installation
quarto list tools
```

Alternative via R:
```r
install.packages("tinytex")
tinytex::install_tinytex()
```

**Install R package dependencies**:

```r
# Install renv if not already installed
install.packages("renv")

# Restore package dependencies from renv.lock
renv::restore()
```

### Key Dependencies

The project uses packages including:
- `knitr`, `rmarkdown` - document rendering (via Quarto)
- Additional packages as needed for causal inference examples

## Build, Test, and Lint Commands

### Building the Website

```bash
# Preview the website locally (with live reload)
quarto preview

# Render the entire website
quarto render

# Render a specific document
quarto render chapters/01-introduction.qmd
```

### Running Tests

This is a documentation/notes repository, so there are no formal unit tests. However, you can verify code chunks work correctly by:

```r
# In R, render a specific Quarto document
quarto::quarto_render("chapters/01-introduction.qmd")
```

### Linting

```r
# Lint R code files
lintr::lint("script.R")

# Lint R code chunks in Quarto documents (requires extracting code)
# This is typically done via the lint-changed-files workflow
```

### Spell Checking

```r
# Run spell check on the repository
spelling::spell_check_package()

# Check specific files
spelling::spell_check_files("README.md")
```

## Code Style and Conventions

### General Guidelines

1. **Follow tidyverse style guide**: Use the tidyverse style guide for R code
2. **Use clear variable names**: Prefer descriptive names over abbreviations
3. **Comment mathematical formulas**: Explain the causal inference concepts when implementing examples
4. **Reproducibility**: Ensure all code chunks are reproducible with set seeds where necessary
5. **Use pipe operators**: Prefer the native R pipe (`|>`) or magrittr pipe (`%>%`) for data manipulation

### Naming Conventions

- **Functions**: Use snake_case (e.g., `calculate_ate`, `estimate_effect`)
- **Variables**: Use snake_case (e.g., `treatment_group`, `outcome_var`)
- **Chapter files**: Use numbered format with descriptive names (e.g., `01-introduction.qmd`, `02-randomized-experiments.qmd`)

### Documentation Standards

- Use Quarto/R Markdown formatting for mathematical notation (LaTeX)
- Include explanatory text before code chunks
- Add comments within complex code blocks
- Reference the "What If?" textbook (Hernán MA, Robins JM) when applicable
- **Use theorem variations to structure content**: Use Quarto's theorem environments (`#def-`, `#thm-`, `#exm-`, `#exr-`, etc.) to organize definitions, theorems, examples, and exercises for better clarity and cross-referencing (see "Theorems and Proofs" section)
- **Use Quarto callouts for Fine Points and Technical Points**: Textbook "Fine Point" and "Technical Point" boxes should be rendered as Quarto callout blocks using the `.callout-note` class with an explicit title matching the textbook numbering, e.g.:
  ```markdown
  ::: {.callout-note title="Fine Point 17.1: Competing Events"}
  Content of the fine point...
  :::
  
  ::: {.callout-note title="Technical Point 17.1: Approximating the Hazard Ratio via a Logistic Model"}
  Content of the technical point...
  :::
  ```
  Always add the actual callout content; never leave a dangling reference to a Technical/Fine Point that has no corresponding callout in the file.
- **Reflow paragraphs --- one line per major phrase**:
  In `.qmd` chapter files, write prose with one sentence (or major clause) per source line.
  Single newlines within a paragraph render as a space in HTML/PDF,
  so this does not affect output but makes git diffs much easier to read.
  Example:
  ```markdown
  This is the first sentence of the paragraph.
  This is the second sentence, which is on its own line.
  Long sentences may be split at a natural clause boundary,
  for example after a comma or conjunction.
  ```
- **Use single space between sentences**: Use only one space after periods between sentences, not two spaces
- **Use bullet points for lists**: When presenting lists of items, tools, formats, or steps, use bullet points rather than comma-separated lists for better readability and clarity
- **Always leave a blank line before bullet point lists**: In Quarto/Markdown, always insert a blank line before starting a bullet point list to ensure proper formatting. Without the blank line, the list may not render correctly.
- **Include original textbook page numbers in section headers**: When creating chapter content based on the "What If?" textbook, include the corresponding page numbers from the original text in section headers to help readers cross-reference with the source material
  - Format: `## Section Title (pp. XX-YY)` for page ranges or `## Section Title (p. XX)` for single pages
  - Example: `## Randomization (pp. 11-15)` or `## Consistency Assumption (p. 8)`
  - Include page numbers for major sections (level 2 headers `##`) when the content directly corresponds to specific textbook sections
  - Page numbers should reference the print edition of "Causal Inference: What If?" by Hernán MA and Robins JM
- Use code chunk options appropriately:
  - `echo=FALSE` to hide code in HTML, or use format-specific visibility
  - `message=FALSE` to suppress messages
  - `fig.align='center'` for centered figures

### Code Organization

- Chapter notes in `chapters/*.qmd` files with numbered prefixes
- Main index in `index.qmd`
- Configuration files: `_quarto.yml` (shared settings), `_quarto-website.yml` (website config), `_quarto-revealjs.yml` (slides config), `_quarto-handout.yml` (PDF config)
- Styling in `styles.css`
- Documentation in `README.md`, `DUAL_FORMAT_GUIDE.md`, `STRUCTURE_VERIFICATION.md`

## Repository Structure

```
win/
├── .github/
│   ├── workflows/              # GitHub Actions workflows
│   │   ├── check-links.yml     # Link checking (uses lychee.toml)
│   │   ├── check-non-standard-chars.yaml # Non-ASCII punctuation check
│   │   ├── check-new-line-breaks.yml # Semantic-line-break check on added lines
│   │   ├── check-spelling.yaml # Spell checking
│   │   ├── lint-changed-files.yaml # R code linting (uses .lintr.R)
│   │   ├── preview.yml         # PR preview deployment
│   │   └── quarto-publish.yml  # GitHub Pages publishing (Morrison-Lab/gha reusable workflow)
│   └── copilot-instructions.md # This file
├── chapters/
│   ├── 01-introduction.qmd     # Chapter 1: Introduction
│   ├── 02-randomized-experiments.qmd # Chapter 2: Randomized Experiments
│   └── ...                     # Additional chapters
├── R/                          # R package source code
│   └── win-package.R          # Package-level documentation
├── man/                        # R package documentation (gitignored, generated by roxygen2)
├── inst/                       # R package installed files
│   └── WORDLIST               # Spell check dictionary
├── renv/                       # renv environment (initialized)
│   ├── activate.R             # renv activation script
│   ├── settings.json          # renv settings
│   └── .gitignore             # renv-specific gitignore
├── _site/                      # Generated website output (gitignored)
├── _slides/                    # Generated slides output (gitignored)
├── _handouts/                  # Generated PDF handouts (gitignored)
├── _freeze/                    # Quarto freeze cache (gitignored - do NOT commit)
├── .quarto/                    # Quarto cache (gitignored)
├── index.qmd                   # Website homepage
├── _quarto.yml                 # Shared Quarto configuration with default profile
├── _quarto-website.yml         # Website configuration (multi-format: HTML, RevealJS, PDF)
├── _quarto-revealjs.yml        # Standalone RevealJS slides configuration
├── _quarto-handout.yml         # Standalone PDF handouts configuration
├── styles.css                  # Custom CSS styling
├── DESCRIPTION                 # R package metadata
├── NAMESPACE                   # R package exports (managed by roxygen2)
├── LICENSE                     # MIT license
├── .Rbuildignore              # Files to exclude from R package build
├── .lintr.R                   # Lintr configuration
├── renv.lock                   # Package dependency lockfile
├── .Rprofile                   # R session configuration with renv activation
├── win.Rproj                   # RStudio project file (configured as R package)
├── README.md                   # Project overview
├── DUAL_FORMAT_GUIDE.md        # Guide for dual-format rendering
└── STRUCTURE_VERIFICATION.md   # Implementation checklist
```

## Quarto Document Structure

### Front Matter

Each `.qmd` file should have YAML front matter with format specifications:

```yaml
---
title: "Chapter Title"
format:
  html: default
  revealjs:
    output-file: filename-slides.html
  pdf:
    output-file: filename-handout.pdf
---
```

This allows the same source file to generate three outputs:
- HTML page for the website
- RevealJS slides with `-slides.html` suffix
- PDF handout with `-handout.pdf` suffix

### Format-Specific Content

**IMPORTANT**: Minimize use of `.content-visible` divs. Most content should be shared between formats.

**Preferred approach**: Use speaker notes for additional context:

```markdown
## Section Title

Core content that appears in both HTML and RevealJS formats.
This should be concise enough for slides but informative enough for the website.

::: {.notes}
Additional detailed explanations that would clutter slides.
These appear as speaker notes in RevealJS and as regular text in HTML/PDF.
:::
```

### Slide Breaks in RevealJS

**CRITICAL**: To prevent long title slides with content in RevealJS presentations, always add a slide break (`---`) immediately after section headings.

**Pattern to follow**:

```markdown
## Section Title (pp. XX-YY)

---

Content starts here on a new slide.
```

**Why this matters**:
- Without the slide break, content appears on the same slide as the section title
- This creates cluttered, hard-to-read title slides
- The slide break ensures the title appears alone on one slide, content on subsequent slides

**Apply this pattern**:
- After every `##` heading (section heading)
- After `###` headings when they introduce substantial content
- Not necessary after headings that are immediately followed by another heading

**Only use `.content-visible` when absolutely necessary** (rarely needed):

```markdown
::: {.content-visible when-format="html"}
Content that truly only makes sense in HTML format
:::

::: {.content-visible when-format="pdf"}
Content specific to PDF format (e.g., print-specific formatting)
:::
```

### Speaker Notes for RevealJS

Use `.notes` divs to add detailed explanations that supplement slides without cluttering them:

```markdown
## Key Concept

Brief explanation suitable for slides.

::: {.notes}
Longer explanation with examples, context, and details.
This text appears in speaker view during presentations
and as regular text in HTML/PDF formats.
:::
```

See [Quarto RevealJS Speaker Notes documentation](https://quarto.org/docs/presentations/revealjs/#speaker-notes) for more details.

### Citations and References

Use Quarto's built-in citation system rather than manual citations:

1. Create a `references.bib` file in the project root
2. Add bibliography to `_quarto.yml`:
   ```yaml
   bibliography: references.bib
   csl: https://www.zotero.org/styles/apa  # or other style
   ```
3. Use citation syntax in documents:
   ```markdown
   As shown in @hernan2020causal [Chapter 1]...
   ```
4. Add a references section at the end of documents:
   ```markdown
   ## References
   
   ::: {#refs}
   :::
   ```

See [Quarto Citations documentation](https://quarto.org/docs/authoring/citations.html) for more details.

### Code Chunks

Use R code chunks with appropriate options:

````markdown
```{r echo=FALSE, message=FALSE}
library(ggplot2)
knitr::opts_chunk$set(fig.align = 'center', message = FALSE)
```
````

### Mathematical Notation

Use LaTeX for mathematical expressions:

```markdown
Inline math: $E[Y^a]$

Display math:
$$
E[Y^a] = \sum_c E[Y^a \mid C=c] P(C=c)
$$

Aligned equations:
\begin{align}
ATE &= E[Y^1] - E[Y^0] \\
    &= E[Y \mid A=1] - E[Y \mid A=0] \quad \text{(under randomization)}
\end{align}
```

### Theorems and Proofs

Quarto supports structured theorem-like environments that are useful for organizing mathematical and conceptual content in lecture notes. Use these to clearly delineate definitions, theorems, examples, exercises, and other structured content.

**Available theorem variations:**

| Label Prefix | Printed Name | Use Case |
|--------------|--------------|----------|
| `#thm-` | Theorem | Formal mathematical theorems or key theoretical results |
| `#lem-` | Lemma | Supporting results used to prove theorems |
| `#cor-` | Corollary | Results that follow directly from theorems |
| `#prp-` | Proposition | Mathematical statements or claims |
| `#cnj-` | Conjecture | Unproven statements or hypotheses |
| `#def-` | Definition | Formal definitions of terms and concepts |
| `#exm-` | Example | Illustrative examples |
| `#exr-` | Exercise | Practice problems for readers |
| `#sol-` | Solution | Solutions to exercises |
| `#rem-` | Remark | Additional comments or observations |
| `#alg-` | Algorithm | Algorithmic procedures |

**Basic syntax:**

Create a div with the appropriate label prefix and include a title as the first heading:

```markdown
::: {#def-ate}
## Average Treatment Effect

The **average treatment effect** (ATE) is defined as:

$$E[Y^{a=1}] - E[Y^{a=0}]$$

where $Y^a$ denotes the potential outcome under treatment level $a$.
:::

See @def-ate for the formal definition.
```

**Proof environment:**

Proofs are not numbered and cannot be cross-referenced. Use the `.proof` class:

```markdown
::: {.proof}
By the law of total expectation and conditional exchangeability.
:::
```

Optionally include a heading to specify what is being proved:

```markdown
::: {.proof}
## Proof of Theorem 1

Step 1: Assume randomization...
:::
```

**Cross-referencing theorems:**

Reference theorem-like environments using `@` syntax:

```markdown
As shown in @def-exchangeability, we require the treatment to be independent
of potential outcomes. This assumption (@def-exchangeability) is satisfied
in randomized experiments (@thm-randomization).
```

**When to use theorem variations:**

- **Definitions** (`#def-`): Define all key causal inference concepts (e.g., exchangeability, consistency, positivity, confounding)
- **Theorems** (`#thm-`): State formal results (e.g., "Under randomization, association equals causation")
- **Examples** (`#exm-`): Illustrate concepts with concrete examples (e.g., Zeus's family data)
- **Exercises** (`#exr-`) and **Solutions** (`#sol-`): End-of-chapter problems
- **Remarks** (`#rem-`): Highlight important insights or common misconceptions
- **Propositions** (`#prp-`): State intermediate results

**Formatting notes:**

- In LaTeX/PDF output, these use the `amsthm` package for professional typesetting
- In HTML output, theorems are styled with appropriate CSS
- In RevealJS output, theorems work but may need adjustment for slide presentation
- All theorem types are automatically numbered (except proofs)
- Numbering is continuous across the document

**Example usage in causal inference:**

```markdown
::: {#def-consistency}
## Consistency

The **consistency assumption** states that the potential outcome under treatment 
level $a$ equals the observed outcome for individuals who actually received 
treatment level $a$:

$$Y = Y^A$$
:::

::: {#exm-consistency}
## Consistency in Zeus's Family

If Zeus receives a heart transplant ($A=1$), then his observed outcome $Y$ 
equals $Y^{a=1}$. We never observe $Y^{a=0}$ for Zeus.
:::

::: {#rem-consistency}
Consistency can be violated if treatment is not well-defined or if there are 
multiple versions of treatment.
:::
```

See [Quarto Theorems and Proofs documentation](https://quarto.org/docs/authoring/cross-references.html#theorems-and-proofs) for complete details.

## CI/CD Workflows

The repository uses GitHub Actions for continuous integration:

1. **quarto-publish.yml**: Builds and publishes the Quarto website to GitHub Pages (via the d-morrison/gha reusable workflow)
   - Runs on push to main branch
   - Renders with Quarto (Quarto actions handle setup), then deploys
     `_site/` to the `gh-pages` branch with
     JamesIves/github-pages-deploy-action, preserving the `pr-preview/`
     subtree
   - Installs TinyTeX for PDF rendering
2. **preview.yml**: Generates preview of the website for pull requests
   - Uses PR preview action to deploy to separate preview URL
   - Allows reviewers to see rendered changes
   - Watches `_quarto-*.yml` files for configuration changes
   - Outputs to `_site/` directory
3. **lint-changed-files.yaml**: Runs lintr on changed R files in pull requests
4. **check-spelling.yaml**: Checks spelling across the repository

All workflows run on relevant triggers (push to main, pull requests, etc.).

### GitHub Secrets and PATs

#### `MACROS_REPO_PAT_WIN`

The repository has a PAT (Personal Access Token) secret named **`MACROS_REPO_PAT_WIN`** that grants write access to the [`d-morrison/macros`](https://github.com/d-morrison/macros) repository, which is the upstream of the `latex-macros` git submodule (path `latex-macros/`).

**Permitted uses:**

- Push commits to a branch in `d-morrison/macros`
- Open pull requests against `d-morrison/macros`

**Restrictions:**

- **Do NOT merge pull requests into the `main` branch** of `d-morrison/macros` using this token.
  Merging is a human decision and must be done by a repository maintainer.

**How to use in a GitHub Actions workflow:**

```yaml
- name: Push changes to macros submodule
  env:
    MACROS_REPO_PAT: ${{ secrets.MACROS_REPO_PAT_WIN }}
  run: |
    git -C latex-macros remote set-url origin \
      https://x-access-token:${MACROS_REPO_PAT}@github.com/d-morrison/macros.git
    git -C latex-macros push origin HEAD:<branch-name>
```

**How to use locally (for testing):**

Set the environment variable `MACROS_REPO_PAT` to the token value, then use it as the password when pushing:

```bash
git -C latex-macros remote set-url origin \
  https://x-access-token:${MACROS_REPO_PAT}@github.com/d-morrison/macros.git
git -C latex-macros push origin HEAD:<branch-name>
```

### Debugging Workflow Failures

**CRITICAL**: When asked to fix workflow errors or when workflows fail:

1. **ALWAYS** read the workflow logs using GitHub MCP tools
2. Use `list_workflow_runs` to find recent runs
3. Use `get_job_logs` or similar tools to get detailed failure logs
4. **NEVER** assume what the error might be - always verify by reading the actual logs
5. Search for error messages in the logs to identify the root cause
6. Fix the specific error found in the logs, not what you think the error might be

This is a mandatory step - do not skip reading the logs when debugging workflow failures.

### Validating Rendering Success

**CRITICAL**: Before declaring that rendering works or that fixes are successful:

1. **ALWAYS** test `quarto render` yourself in your working environment
2. Verify that **ALL** output formats are generated successfully:
   - HTML pages (`*.html`)
   - RevealJS slides (`*-slides.html`)  
   - PDF handouts (`*-handout.pdf`)
3. Check that files actually exist in the output directory (`_site/`)
4. Verify file sizes are reasonable (not 0 bytes, not truncated)
5. **NEVER** claim success based on assumptions or partial output
6. **NEVER** declare rendering works without actually testing it

**For this project specifically**: The default `quarto render` command generates HTML, RevealJS, and PDF outputs. All three formats must render successfully for the build to pass.

## Important Notes

### Working with Causal Inference Examples

- Set random seeds for reproducibility: `set.seed()` or `withr::local_seed()`
- Document the causal concepts and their sources (refer to Hernán & Robins when applicable)
- Include original textbook page numbers in section headers when content corresponds to specific sections of the "What If?" textbook
- Include references to papers and textbooks
- Explain DAGs and causal assumptions clearly
- Use clear notation for potential outcomes and interventions

### Multi-Format Rendering

**IMPORTANT**: This project uses a multi-format structure where each chapter renders to HTML, RevealJS, and PDF.

Key considerations:
- **HTML format**: Detailed, comprehensive website content for reading and study
- **RevealJS format**: Concise, presentation-oriented slides for teaching
- **PDF format**: Print-friendly handouts with references and notes
- **Content visibility**: Use `.content-visible when-format=` divs to show/hide content based on output format
- **Slide structure**: In RevealJS sections, use `##` for slide titles and `###` for content within slides
- **Progressive reveal**: Use `.fragment` classes for incremental display in slides
- **Output files**: 
  - HTML: `{filename}.html` (e.g., `01-introduction.html`)
  - RevealJS: `{filename}-slides.html` (e.g., `01-introduction-slides.html`)
  - PDF: `{filename}-handout.pdf` (e.g., `01-introduction-handout.pdf`)

See `DUAL_FORMAT_GUIDE.md` for comprehensive patterns and best practices.

### Profile-Based Rendering

The project supports multiple rendering profiles:

1. **Default (website)**: Renders all formats (HTML, RevealJS, PDF) to `_site/`
   ```bash
   quarto render
   ```

2. **RevealJS profile**: Renders only slides to `_slides/`
   ```bash
   QUARTO_PROFILE=revealjs quarto render
   ```

3. **Handout profile**: Renders only PDFs to `_handouts/`
   ```bash
   QUARTO_PROFILE=handout quarto render
   ```

### Data Visualization

- Use ggplot2 for consistency
- Follow tidyverse aesthetic principles
- Include axis labels and titles
- Use appropriate color schemes for accessibility
- Consider how visualizations will appear in all formats (slides may need larger fonts/simpler layouts, PDFs need to be printer-friendly)

### Making Changes

**CRITICAL - MANDATORY TESTING REQUIREMENT:**

**STEP 0 - ENVIRONMENT SETUP (DO THIS FIRST, EVERY SESSION):**
- Install R 4.5.2+, Quarto, TinyTeX if not already installed (see Installation section)
- Run `renv::restore()` to install all R packages
- Verify tools work: `quarto --version`, `R --version`
- **NEVER start making code changes without having the environment ready**

**BEFORE MAKING ANY COMMIT** with `.qmd` or configuration file changes, you MUST:

1. **Run FULL `quarto render`** on the entire repository (not individual files)
2. **Wait for it to complete** - do not interrupt or assume success
3. **Verify exit code is 0** (success) - rendering MUST complete without errors
4. **Check all three output formats** exist in `_site/` for ALL documents:
   - `{filename}.html` (website pages)
   - `{filename}-slides.html` (RevealJS presentations)
   - `{filename}-handout.pdf` (PDF handouts)
5. **Only then** can you commit your changes

**CRITICAL RULES:**
- **CI is NOT the test** - it's final verification only
- **Testing individual files is insufficient** - always do full `quarto render`
- **If CI fails, you failed to test properly** - this should never happen
- **No exceptions, no excuses** - this is a hard requirement

Additional guidelines:
- When modifying `.qmd` files, ensure code chunks execute successfully
- Use `quarto render file.qmd` for rapid iteration ONLY
- Always follow up with FULL `quarto render` before committing
- Run `quarto preview` to verify changes render correctly
- Check mathematical notation renders properly (especially in PDF format)
- Ensure figures display as intended
- Verify cross-references and links work
- Update `_quarto.yml` if adding/removing pages

### Pull Request Development

**IMPORTANT**: When developing new pull requests, always run `quarto render` to ensure the website can be rendered successfully before finalizing your changes.

- **Always run `quarto render`** during PR development to verify that all changes render correctly
- **CRITICAL**: Test `quarto render` yourself and verify it actually succeeds before claiming success
  - Run the command and wait for it to complete
  - Check the exit code to confirm success (exit code 0)
  - Do not claim success based on partial output or assumptions
  - If the render fails, investigate and fix the issue before proceeding
  - **"Software not installed" is NOT a valid excuse** - install required software (R, Quarto, etc.) first if needed (see Installation section above)
  - **CRITICAL**: When installing R, you MUST use the latest R release from CRAN (see Installation section)
    - **NEVER** use the default R from Ubuntu repositories (e.g., `apt-get install r-base` without adding CRAN repo)
    - The default Ubuntu R is outdated (e.g., R 4.3.3) and will cause issues
    - Always add the CRAN repository first, then install R to get the latest version (R 4.5.2+)
    - Verify the R version with `R --version` before proceeding
- Check that the rendering completes without errors or warnings
- Review the generated output in the `_site/` directory to ensure quality
- Fix any rendering issues before requesting review
- This practice helps maintain the quality of rendered outputs and streamlines the contribution process
- Note: The CI/CD workflows (preview.yml and quarto-publish.yml) will also render the website, but catching issues locally saves time

### Dependencies

- Use `renv::snapshot()` after adding new packages
- Ensure all required packages are available
- Test that `renv::restore()` works for reproducibility

### Working with renv in CI/CD

This project uses `renv` for R package dependency management. The workflows are configured to use renv properly:

**Key points:**
1. **renv activation**: If using renv, the `.Rprofile` file activates renv with `source("renv/activate.R")`
2. **GitHub Actions setup**: Use `r-lib/actions/setup-renv@v2` in workflows instead of `setup-r-dependencies`
3. **Package repository**: The `renv.lock` file uses Posit Package Manager (https://packagemanager.posit.co/cran/latest)
4. **Cache management**: The `setup-renv` action automatically caches the renv library for faster builds

**Workflow configuration example:**
```yaml
- uses: r-lib/actions/setup-r@v2
  with:
    use-public-rspm: true

- uses: r-lib/actions/setup-renv@v2
  with:
    cache-version: 1
```

**Local testing with renv:**
- When you activate renv locally (by sourcing `.Rprofile` or running R in the project), renv creates its own package library
- The first time, run `renv::restore()` to install all packages from `renv.lock`
- Packages are cached in `~/.cache/R/renv/` (or similar) for reuse across projects
- `quarto render` will automatically use the renv environment when `.Rprofile` sources `renv/activate.R`

**Troubleshooting:**
- If `quarto render` fails with "package not found" errors, ensure you've run `renv::restore()` first
- Check that `.Rprofile` is activating renv (it should have `source("renv/activate.R")` uncommented)
- In CI/CD, the `setup-renv` action handles restoration automatically

### TinyTeX for PDF Rendering

**CRITICAL**: TinyTeX **MUST** be installed in your working environment when developing PRs for this project, as PDF format is included in the default website rendering.

**Installation**: See the "Installation" section above for TinyTeX installation instructions. This should be done at the start of PR development.

**When PDF output is required**:
- **ALWAYS at the start of PR development** - This is now a required step
- Before rendering PDF output formats
- Before running multi-format rendering that includes PDF
- When you see the error: "No TeX installation was detected"

**Important**: TinyTeX installation requires internet access to GitHub releases and CTAN mirrors. Without TinyTeX, the website rendering will fail when trying to generate PDF handouts.

**Note**: The separate `_quarto-handout.yml` profile exists as an alternative method for PDF rendering and can be used independently.

### Quarto Multi-Format Rendering

This project uses multi-format rendering to generate HTML, RevealJS slides, and PDF handouts simultaneously.

**Default website rendering** (`quarto render`):
- Generates **all three formats** in `_site/` directory:
  - `{filename}.html` - Website page
  - `{filename}-slides.html` - RevealJS presentation
  - `{filename}-handout.pdf` - PDF handout (requires TinyTeX)

**Alternative profile-based rendering**:
1. **RevealJS profile**: `QUARTO_PROFILE=revealjs quarto render` - Generates slides in `_slides/`
2. **PDF handout profile**: `QUARTO_PROFILE=handout quarto render` - Generates PDFs in `_handouts/`

**Implementation approach**:
Following the pattern from https://github.com/perellonieto/quarto_html_revealjs_test:
- **Project-level config** (`_quarto-website.yml`): Defines html, revealjs, and pdf formats
- **File-level frontmatter**: Each .qmd file specifies all three formats with `output-file` for non-html formats:
  ```yaml
  format:
    html: default
    revealjs:
      output-file: {filename}-slides.html
    pdf:
      output-file: {filename}-handout.pdf
  ```
- This generates three separate output files per source file, avoiding naming conflicts

**Key insights**:
- Both formats must be specified at two levels: project configuration AND individual file frontmatter
- The `output-file` parameter is used at the file level to avoid naming conflicts
- See: https://github.com/orgs/quarto-dev/discussions/1751

## Continuous Learning and Improvement

**IMPORTANT**: When you learn new skills, techniques, or encounter solutions to problems while working on this project, **you MUST update this instructions file** to document them for future reference.

This includes:
- New installation procedures or dependencies
- Solutions to rendering or build issues
- Workarounds for technical limitations
- New tools or commands that prove useful
- Configuration patterns that work well for this project type
- Debugging techniques specific to Quarto/R/renv

**How to update**:
1. Identify which section the new information belongs in (or create a new section if needed)
2. Add clear, concise instructions with examples where helpful
3. Include references to external resources (documentation, discussions, issues) when relevant
4. Use `store_memory` tool to save important facts about the codebase for future tasks

This ensures the instructions stay current and helpful for both yourself and other contributors.

## R Package Configuration

This repository is configured as an R package in addition to being a Quarto website. This section documents key considerations and lessons learned.

### R Package Structure

**Core Files:**
- **DESCRIPTION**: Package metadata with author info, dependencies, and license
- **NAMESPACE**: Package exports (managed by roxygen2 - start with `# Generated by roxygen2: do not edit by hand`)
- **LICENSE**: MIT license file (use `usethis::use_mit_license("Author Name")` pattern)
- **.Rbuildignore**: Critical for excluding Quarto website files from R package build
- **R/**: Directory for R source code (e.g., `R/win-package.R` for package-level docs)
- **man/**: Documentation directory (generated by roxygen2, should be gitignored except placeholders)

### RStudio Project Configuration

Update `win.Rproj` with these settings for R package development:
```
BuildType: Package
PackageUseDevtools: Yes
PackageInstallArgs: --no-multiarch --with-keep.source
PackageRoxygenize: rd,collate,namespace
```

### renv Initialization

**Key Steps:**
1. Initialize renv with `renv::init(bare = TRUE)` to avoid automatic package discovery
2. This creates `renv/activate.R`, `renv/settings.json`, and `renv/.gitignore`
3. The `.Rprofile` should activate renv: `source("renv/activate.R")`
4. Use `renv::snapshot()` to capture package state, `renv::restore()` to restore

**Important**: renv initialization should be done early to avoid conflicts with package installation.

### Linting Configuration

**File: `.lintr.R`** (not `.lintr`)
- The lint-changed-files workflow expects `.lintr.R` (note the .R extension)
- Can merge configurations from other projects (e.g., UCD-SERG/serodynamics)
- Typical settings include exclusions for specific linters and line length limits

**Workflow Update**: Ensure `.github/workflows/lint-changed-files.yaml` references `.lintr.R`:
```yaml
with:
  linters: '.lintr.R'
```

### Spell Check Configuration

**File: `inst/WORDLIST`**
- The spelling package and check-spelling workflow look for `inst/WORDLIST`
- Alphabetize entries for easier maintenance
- Include technical terms, author names, acronyms, package names
- Common additions: author name components, "demorrison", "Quarto", "RevealJS", "tidyverse", "ggplot", "RoxygenNote", "markdown"

**Troubleshooting**: If spellcheck workflow fails:
1. Use GitHub MCP tools to read workflow logs and identify misspelled words
2. Add legitimate technical terms to `inst/WORDLIST`
3. Alphabetize the list after adding new terms

### .Rbuildignore Patterns

Critical patterns to exclude Quarto website files from R package build:
```
^\.github$
^chapters$
^_quarto.*\.yml$
^_site$
^_slides$
^_handouts$
^\.quarto$
^styles\.css$
^index\.qmd$
.*\.Rproj$
^\.Rproj\.user$
^DUAL_FORMAT_GUIDE\.md$
^STRUCTURE_VERIFICATION\.md$
```

### CI/CD Workflow Considerations

**Spell Check Workflow:**
- May fail due to pre-existing issues on main branch
- Check main branch workflow history before assuming PR caused failures
- Add words to `inst/WORDLIST` to address package-specific terms

**Lint Workflow:**
- Only runs on PRs (changed files only)
- Ensure `.lintr.R` exists and is properly configured
- Update workflow file if config file name changes

### .Rprofile Configuration

Can merge settings from other R package projects (e.g., hoff-bayesian-statistics):
- renv activation
- Options for package development
- Custom startup messages or settings

**Example pattern:**
```r
source("renv/activate.R")

# Additional custom options
options(
  # your options here
)
```

### Common Issues and Solutions

**Issue**: Spellcheck workflow fails with missing words
- **Solution**: Add technical terms to `inst/WORDLIST`, alphabetize

**Issue**: Lint workflow can't find config file
- **Solution**: Ensure `.lintr.R` exists and workflow references it correctly

**Issue**: renv not activating in CI
- **Solution**: Verify `.Rprofile` contains `source("renv/activate.R")` and `renv/` directory is committed

**Issue**: Quarto files included in R package build
- **Solution**: Add appropriate patterns to `.Rbuildignore`

**Issue**: Package dependency conflicts
- **Solution**: Use `renv::snapshot()` to capture working state, ensure `renv.lock` is up to date

## Getting Help

- Project GitHub: https://github.com/ucdavis/win
- Original Textbook: Hernán MA, Robins JM. "Causal Inference: What If." Boca Raton: Chapman & Hall/CRC, 2020. (https://www.hsph.harvard.edu/miguel-hernan/causal-inference-book/)
- Quarto Documentation: https://quarto.org/docs/guide/
- Quarto Multi-format Discussion: https://github.com/orgs/quarto-dev/discussions/1751
