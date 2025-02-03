function updateStats() {
    fetch('/stats')
        .then(response => response.json())
        .then(data => {
            console.log("Stats received:", data); // Debugging log

            document.getElementById("total_proxies").innerText = data.proxies.total;
            document.getElementById("valid_proxies").innerText = data.proxies.valid;
            document.getElementById("dead_proxies").innerText = data.proxies.dead;
            document.getElementById("total_hosts").innerText = data.hosts.total;
            document.getElementById("live_hosts").innerText = data.hosts.valid;
            document.getElementById("dead_hosts").innerText = data.hosts.dead;
            document.getElementById("brute_running").innerText = data.bruteforce.running;
            document.getElementById("brute_success").innerText = data.bruteforce.success;
            document.getElementById("brute_failed").innerText = data.bruteforce.failed;
        })
        .catch(error => console.error("Error fetching stats:", error));
}

// Auto-refresh every 5 seconds
setInterval(updateStats, 5000);

// Start proxy testing
function startProxyTest() {
    fetch('/proxies/test', { method: 'POST' })
        .then(() => alert('Proxy testing started!'));
}

// Start host scanning
function startHostScan() {
    fetch('/hosts/scan', { method: 'POST' })
        .then(() => alert('Host scanning started!'));
}

// Start brute-force attack
function startBruteForce() {
    fetch('/bruteforce/start', { method: 'POST' })
        .then(() => alert('Brute-force attack started!'));
}
