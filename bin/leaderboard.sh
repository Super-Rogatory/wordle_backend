. ~/.bash_profile && \
echo "Update Leaderboard: $(date)" && \
# getTop10 - standalone program placeholder name
$PROJ_PATH/dist/getTop10 | redis-cli --pipe 