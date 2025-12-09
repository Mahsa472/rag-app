# DVC Pipeline Setup Guide

This project uses DVC (Data Version Control) with GitHub Actions to automatically reindex documents when new PDFs are added.

## How It Works

1. **DVC tracks `data/pdfs/`** - Monitors PDF files for changes
2. **GitHub Actions triggers** - When PDFs are pushed to the repository
3. **Pipeline runs** - Automatically reindexes all PDFs
4. **ChromaDB reset** - Ensures no duplicate data (clean index)

## Initial Setup

### 1. Initialize DVC locally (one-time)

```bash
# Initialize DVC
dvc init

# Add PDFs directory to DVC tracking
dvc add data/pdfs

# Commit DVC files
git add data/pdfs.dvc .gitignore dvc.yaml
git commit -m "Initialize DVC pipeline"
git push
```

### 2. Test the pipeline locally

```bash
# Run the pipeline manually
dvc repro

# Check status
dvc status
```

## Adding New PDFs

### Step-by-Step Process

1. **Add PDFs to the directory:**
   ```bash
   cp new_document.pdf data/pdfs/
   ```

2. **Update DVC tracking:**
   ```bash
   dvc add data/pdfs
   ```

3. **Commit and push:**
   ```bash
   git add data/pdfs.dvc
   git commit -m "Add new PDFs"
   git push
   ```

4. **GitHub Actions automatically:**
   - Detects the change in `data/pdfs/`
   - Runs `dvc repro`
   - Reindexes all PDFs (resets ChromaDB to avoid duplicates)
   - Commits updated ChromaDB index

## GitHub Actions Workflow

The workflow (`.github/workflows/dvc-pipeline.yml`) triggers when:
- PDFs are added/modified in `data/pdfs/`
- Source code files change (`src/ingestion.py`, `src/embeddings_store.py`)
- `dvc.yaml` is modified
- Manual trigger via GitHub Actions UI

## Important Notes

### ChromaDB Reset Behavior

The pipeline **always resets ChromaDB** (`reset=True`) to ensure:
- ✅ No duplicate data
- ✅ Clean index with only current PDFs
- ✅ Consistent state

### DVC Files to Commit

**Commit these files:**
- `data/pdfs.dvc` - Tracks PDF files
- `data/chroma_db.dvc` - Tracks ChromaDB index (auto-generated)
- `dvc.yaml` - Pipeline definition
- `.dvcignore` - DVC ignore rules
- `metrics.json` - Pipeline metrics (auto-generated)

**Do NOT commit:**
- `data/pdfs/` - Actual PDF files (tracked by DVC)
- `data/chroma_db/` - Actual ChromaDB files (tracked by DVC)

## Local Development

### Run pipeline locally

```bash
# Check if pipeline needs to run
dvc status

# Run pipeline
dvc repro

# View pipeline graph
dvc dag
```

### Manual indexing (without DVC)

```bash
# Use the Flask API endpoint
curl -X POST http://localhost:8000/build-index
```

## Troubleshooting

### Pipeline not detecting changes

```bash
# Force pipeline to run
dvc repro --force

# Check DVC status
dvc status
```

### Clear DVC cache

```bash
dvc cache dir  # See cache location
dvc cache clear  # Clear cache
```

### Reset pipeline

```bash
# Remove outputs and restart
dvc remove data/chroma_db.dvc
dvc repro
```

## Remote Storage (Optional)

For production, store large files in S3:

```bash
# Configure S3 remote
dvc remote add -d s3remote s3://your-bucket/dvc-storage

# Push data
dvc push

# Pull data
dvc pull
```

Update `.dvc/config` with your S3 credentials.

## CI/CD Integration

The GitHub Actions workflow:
1. ✅ Installs dependencies
2. ✅ Runs DVC pipeline
3. ✅ Commits updated ChromaDB index
4. ✅ Provides metrics output

You can extend it to:
- Deploy to AWS EC2
- Update Docker images
- Send notifications

