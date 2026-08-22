#!/bin/bash
PROJECT_DIR="/mnt/c/users/a.yassir.el/downloads/data-quality-app"
BRANCH="develop"
LOG_FILE="$PROJECT_DIR/scripts/deploy-watch.log"

cd "$PROJECT_DIR" || exit 1

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Verification des nouveaux commits..." >> "$LOG_FILE"

git fetch origin "$BRANCH" >> "$LOG_FILE" 2>&1

LOCAL_HASH=$(git rev-parse HEAD)
REMOTE_HASH=$(git rev-parse "origin/$BRANCH")

if [ "$LOCAL_HASH" != "$REMOTE_HASH" ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Nouveau commit detecte ($REMOTE_HASH). Lancement du deploiement Ansible." >> "$LOG_FILE"
    cd "$PROJECT_DIR/ansible" || exit 1
    ansible-playbook -i inventory.ini deploy.yml >> "$LOG_FILE" 2>&1
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Deploiement termine." >> "$LOG_FILE"
else
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Aucun changement, rien a faire." >> "$LOG_FILE"
fi
