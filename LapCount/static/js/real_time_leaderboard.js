let autoRefresh = false;
let refreshInterval;

function toggleLeaderboard() {
    autoRefresh = !autoRefresh;
    if (autoRefresh) {
        refreshInterval = setInterval(refreshTable, 5000); // Refresh every 5 seconds
    } else {
        clearInterval(refreshInterval);
    }
}

function refreshTable() {
    fetch("index?leaderboard=true")
        .then(response => response.text())
        .then(data => {
            const parser = new DOMParser();
            const doc = parser.parseFromString(data, 'text/html');
            const newTableBody = doc.querySelector('#swimmersTable tbody');
            if (newTableBody) {
                const currentTableBody = document.querySelector('#swimmersTable tbody');
                currentTableBody.innerHTML = newTableBody.innerHTML;

                // Update winner signs
                const rows = currentTableBody.querySelectorAll('tr');
                rows.forEach((row, index) => {
                    const nameCell = row.querySelector('td:first-child');
                    if (nameCell) {
                        let winnerSign = '';
                        if (index === 0) {
                            winnerSign = '🥇';
                        } else if (index === 1) {
                            winnerSign = '🥈';
                        } else if (index === 2) {
                            winnerSign = '🥉';
                        }
                        nameCell.innerHTML = `${winnerSign} ${nameCell.innerHTML.trim()}`;
                    }
                });
            } else {
                console.error('Failed to find the table body in the fetched HTML.');
            }
        })
        .catch(error => console.error('Error fetching the table data:', error));
}