# Quick Reference: DVC Pipeline

## What Was Set Up

✅ **DVC Pipeline** (`dvc.yaml`) - Automatically reindexes when PDFs change  
✅ **GitHub Actions** (`.github/workflows/dvc-pipeline.yml`) - Triggers on PDF changes  
✅ **Indexing Script** (`scripts/index_pipeline.py`) - Resets ChromaDB and reindexes  
✅ **Metrics** (`scripts/generate_metrics.py`) - Tracks indexing stats  

## Quick Start

### 1. Initialize DVC (one-time)

```bash
dvc init
dvc add data/pdfs
git add data/pdfs.dvc .gitignore dvc.yaml
git commit -m "Initialize DVC"
git push
```

### 2. Add New PDFs

```bash
# Add PDF
cp new_file.pdf data/pdfs/

# Update DVC
dvc add data/pdfs

# Commit and push
git add data/pdfs.dvc
git commit -m "Add new PDFs"
git push
```

**GitHub Actions will automatically:**
- Detect PDF changes
- Run DVC pipeline
- Reindex all PDFs (clean ChromaDB, no duplicates)
- Commit updated index

## Key Features

- 🔄 **Automatic**: Triggers on PDF changes via GitHub Actions
- 🧹 **Clean**: Resets ChromaDB to avoid duplicates
- 📊 **Tracked**: DVC versions your data and index
- 🚀 **CI/CD Ready**: Works seamlessly with GitHub Actions

## Manual Trigger

You can also manually trigger the workflow:
1. Go to GitHub Actions tab
2. Select "DVC Pipeline - Reindex Documents"
3. Click "Run workflow"

## Files Created

- `dvc.yaml` - Pipeline definition
- `scripts/index_pipeline.py` - Indexing script (resets ChromaDB)
- `scripts/generate_metrics.py` - Metrics generation
- `.github/workflows/dvc-pipeline.yml` - GitHub Actions workflow
- `.dvcignore` - DVC ignore rules

See `DVC_SETUP.md` for detailed documentation.

