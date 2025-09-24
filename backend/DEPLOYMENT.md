# MediLedger Nexus - Deployment Configurations

## 📁 Render Configuration Files

### `render.yaml` (Root Directory)
- **Purpose**: Free tier optimized deployment
- **Location**: `/render.yaml` (root directory)
- **Plan**: Starter (Free tier)
- **Features**: 
  - Single web service
  - SQLite database
  - Minimal dependencies
  - 512MB RAM, 0.1 vCPU
  - Optimized for free tier limits

### `render-full.yaml` (Backend Directory)
- **Purpose**: Full-featured deployment with all services
- **Location**: `/backend/render-full.yaml`
- **Plan**: Standard/Pro (Paid tiers)
- **Features**:
  - Web service + Worker services
  - PostgreSQL database
  - Redis cache
  - Celery workers
  - Full ML/AI capabilities
  - Multiple services architecture

## 🚀 Deployment Instructions

### Free Tier Deployment (Recommended for Testing)
```bash
# Use the render.yaml in root directory
# Render will automatically detect and use it
# No additional configuration needed
```

### Full Deployment (Production)
```bash
# Copy render-full.yaml to root as render.yaml
cp backend/render-full.yaml render.yaml

# Update paths in render-full.yaml if needed
# Deploy with full services
```

## 📋 Service Comparison

| Feature | Free Tier | Full Deployment |
|---------|-----------|-----------------|
| **RAM** | 512MB | 512MB+ |
| **CPU** | 0.1 vCPU | 0.5+ vCPU |
| **Database** | SQLite | PostgreSQL |
| **Cache** | None | Redis |
| **Workers** | None | Celery |
| **ML Features** | Disabled | Enabled |
| **Cost** | Free | $7+/month |

## 🔧 Environment Variables

### Free Tier (render.yaml)
- `ENABLE_ML_FEATURES=false`
- `ENABLE_AI_FEATURES=false`
- `WORKER_PROCESSES=1`
- `DATABASE_URL=sqlite:///./mediledger_nexus.db`

### Full Deployment (render-full.yaml)
- `ENABLE_ML_FEATURES=true`
- `ENABLE_AI_FEATURES=true`
- `WORKER_PROCESSES=4`
- `DATABASE_URL=postgresql://...`

## 📊 Requirements Files

### `requirements-minimal.txt`
- **Purpose**: Free tier deployment
- **Size**: ~50-100MB
- **Dependencies**: 20 essential packages
- **Excludes**: PyTorch, pandas, scikit-learn

### `requirements.txt`
- **Purpose**: Full deployment
- **Size**: ~200-300MB
- **Dependencies**: 66 packages
- **Includes**: All ML/AI libraries

## 🎯 Deployment Strategy

1. **Start with Free Tier**: Use `render.yaml` for initial deployment
2. **Test and Monitor**: Check resource usage and performance
3. **Upgrade When Ready**: Switch to `render-full.yaml` for production
4. **Scale as Needed**: Upgrade to higher paid tiers

## ⚠️ Important Notes

- **Only one `render.yaml`** should exist in the root directory
- **Render automatically detects** `render.yaml` in the root
- **Backend directory** contains reference configurations
- **Update paths** when moving configurations between directories
