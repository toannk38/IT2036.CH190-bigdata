# Vietnam Stock AI Backend - Project Documentation

## Structure

```
report/
├── slide/                  # LaTeX Beamer presentation
│   ├── main.tex           # Main slide file
│   ├── sections/          # Individual slide sections
│   └── images/            # Images for slides
├── report/                # Detailed LaTeX report
│   ├── main.tex           # Main report file
│   ├── chapters/          # Report chapters
│   ├── appendices/        # Appendices
│   └── images/            # Images for report
└── diagrams/              # Draw.io XML diagram files
```

## LaTeX Compilation Instructions

### Prerequisites
- LaTeX distribution (TeX Live, MiKTeX, etc.)
- Vietnamese language support packages
- XeLaTeX or LuaLaTeX (recommended for Vietnamese)

### Compilation Commands

#### For Slides (Beamer)
```bash
cd report/slide/
xelatex main.tex
# or
lualatex main.tex
# or (if Vietnamese fonts are properly configured)
pdflatex main.tex
```

#### For Report
```bash
cd report/report/
xelatex main.tex
xelatex main.tex  # Run twice for proper cross-references
# or
lualatex main.tex
lualatex main.tex
```

### Vietnamese Language Support

The documents are configured with:
- `\usepackage[utf8]{inputenc}` - UTF-8 encoding
- `\usepackage[vietnamese]{babel}` - Vietnamese language support

For best results with Vietnamese characters, use XeLaTeX or LuaLaTeX which have better Unicode support.

### Font Requirements

If using XeLaTeX/LuaLaTeX, ensure Vietnamese fonts are installed:
- Windows: Times New Roman, Arial (built-in)
- Linux: Install `fonts-liberation` or `fonts-dejavu`
- macOS: System fonts should work

## Editing Instructions

1. Edit slide content in `slide/sections/` files
2. Edit report content in `report/chapters/` files
3. Add images to respective `images/` directories
4. Edit diagrams using Draw.io and save as XML in `diagrams/`

## Notes

- All placeholder content is marked with `[...]` brackets
- Diagram placeholders reference files in `diagrams/` directory
- Technical terms are kept in English while descriptions are in Vietnamese
- Use UTF-8 encoding for all text files