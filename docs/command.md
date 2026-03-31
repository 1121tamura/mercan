- cd /workspace
- uv init backend
- ls -la /workspace/backend

- cd /workspace/backend
- uv add --bounds exact fastapi sqlalchemy alembic uvicorn
- cat pyproject.toml

実行コマンド
- cd /workspace/backend
- mkdir -p presentation/routers presentation/schemas
- mkdir -p application/usecases application/dtos
- mkdir -p domain/entities domain/value_objects domain/repositories domain/services
- mkdir -p infrastructure/repositories infrastructure/database infrastructure/parsers
- mkdir -p tests
確認コマンド
- find . -maxdepth 3 -type d | sort