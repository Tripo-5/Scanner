document.addEventListener("DOMContentLoaded", function() {
    function updateStats() {
        fetch('/api/stats')
        .then(response => response.json())
        .then(data => {
            document.getElementById("proxy-count").innerText = data.proxies.valid;
            document.getElementById("host-count").innerText = data.hosts.valid;
            document.getElementById("brute-count").innerText = data.bruteforce.success;
        })
        .catch(error => console.error("Error fetching stats:", error));
    }
    setInterval(updateStats, 5000);
    updateStats();
});
