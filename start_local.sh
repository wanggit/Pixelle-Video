#!/bin/bash
# Pixelle-Video 本地启动脚本
set -e

cd "$(dirname "$0")"

# 检查 venv
if [ ! -f ".venv/bin/python" ]; then
  echo "❌ 虚拟环境不存在，运行: uv sync"
  uv sync
fi

# 检查是否已在运行
if curl -s http://localhost:8501/_stcore/health > /dev/null 2>&1; then
  echo "⚠️  服务已在运行: http://localhost:8501"
  exit 0
fi

echo "🚀 启动 Pixelle-Video..."
nohup .venv/bin/python -m streamlit run web/app.py \
  --server.port 8501 \
  --server.headless true \
  --browser.gatherUsageStats false \
  </dev/null > /tmp/streamlit.log 2>&1 &
PID=$!

# 等待启动（最多 15 秒）
echo "⏳ 等待服务就绪..."
for i in $(seq 1 15); do
  sleep 1
  curl -s http://localhost:8501/_stcore/health > /dev/null 2>&1 && break
done

# 验证
if curl -s http://localhost:8501/_stcore/health > /dev/null 2>&1; then
  echo "✅ 启动成功! PID=$PID"
  echo "🌐 访问: http://localhost:8501"
else
  echo "❌ 启动失败，查看日志: cat /tmp/streamlit.log"
  exit 1
fi
